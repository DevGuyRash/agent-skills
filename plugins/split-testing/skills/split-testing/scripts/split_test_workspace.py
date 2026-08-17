#!/usr/bin/env python3
"""Create opaque workspaces and preserve reveal-after-judgment custody."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import sys
import tempfile
from contextlib import contextmanager
from typing import Any, Optional

try:
    import fcntl
except ImportError:  # pragma: no cover - the CLI rejects non-POSIX hosts first
    fcntl = None  # type: ignore[assignment]


SCHEMA_VERSION = "1.0"
CONTROL_DIR = ".split-testing"
STATE_FILE = "experiment.json"
LOCK_FILE = "workspace.lock"
TOKEN_PATTERN = re.compile(r"^[0-9a-f]{32}$")
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
LEGACY_SAMPLE_PATTERN = re.compile(r"^S([0-9]{3,})$")
BLOCK_SAMPLE_PATTERN = re.compile(r"^B([0-9]{3,})-S([0-9]{3,})$")
HELP = """usage: split_test_workspace.py COMMAND ...

commands:
  init ROOT
  add-round ROOT DESIGN.json
  assignments ROOT ROUND_ID
  anonymize ROOT ROUND_ID
  reveal ROOT ROUND_ID
  status ROOT
"""


class UsageError(Exception):
    """The caller supplied an invalid command or design."""


class OperationError(Exception):
    """The requested state transition could not be completed."""


def fail(message: str, code: int) -> int:
    print(f"error: {message}", file=sys.stderr)
    print("hint: run split_test_workspace.py --help", file=sys.stderr)
    return code


def absolute_root(raw: str) -> Path:
    if os.name != "posix" or fcntl is None:
        raise UsageError("this helper requires POSIX file custody and locking")
    root = Path(raw)
    if not root.is_absolute():
        raise UsageError("ROOT must be an explicit absolute path")
    root = Path(os.path.normpath(root))
    ensure_no_symlink_components(root, allow_missing_leaf=True, usage=True)
    return root


def ensure_no_symlink_components(
    path: Path,
    *,
    allow_missing_leaf: bool = False,
    usage: bool = False,
) -> None:
    """Reject a symlink in every existing component of an absolute path."""

    if not path.is_absolute():
        error = UsageError if usage else OperationError
        raise error(f"managed path must be absolute: {path}")
    current = Path(path.anchor)
    parts = path.parts[1:]
    for index, part in enumerate(parts):
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError as exc:
            if allow_missing_leaf and index == len(parts) - 1:
                return
            error = UsageError if usage else OperationError
            raise error(f"path component is missing: {current}") from exc
        if stat.S_ISLNK(mode):
            error = UsageError if usage else OperationError
            raise error(f"path contains a symbolic link: {current}")


def ensure_managed_components(root: Path, path: Path, label: str) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise OperationError(f"{label} escapes ROOT: {path}") from exc
    current = root
    for part in relative.parts:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError as exc:
            raise OperationError(f"{label} path is missing: {current}") from exc
        if stat.S_ISLNK(mode):
            raise OperationError(f"{label} contains a symbolic link: {current}")


def fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def state_path(root: Path) -> Path:
    return root / CONTROL_DIR / STATE_FILE


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def write_bytes_atomic(
    path: Path,
    content: bytes,
    *,
    mode: int = 0o600,
    replace: bool = True,
) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        if replace:
            os.replace(temporary, path)
        else:
            try:
                os.link(temporary, path, follow_symlinks=False)
            except FileExistsError as exc:
                raise OperationError(f"refusing to replace permanent file: {path}") from exc
            temporary.unlink()
        fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json_atomic(
    path: Path,
    value: Any,
    mode: int = 0o600,
    *,
    replace: bool = True,
) -> None:
    write_bytes_atomic(path, json_bytes(value), mode=mode, replace=replace)


def read_json(path: Path, *, design: bool = False) -> Any:
    try:
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
            kind = "design" if design else "workspace state"
            raise UsageError(f"{kind} is not a regular file: {path}")
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
            return json.load(stream)
    except FileNotFoundError as exc:
        kind = "design" if design else "workspace state"
        raise UsageError(f"{kind} file does not exist: {path}") from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        kind = "design" if design else "workspace state"
        raise UsageError(f"{kind} is not valid UTF-8 JSON: {path}") from exc
    except RecursionError as exc:
        kind = "design" if design else "workspace state"
        raise UsageError(f"{kind} is too deeply nested: {path}") from exc


def load_experiment(root: Path) -> dict[str, Any]:
    validate_custody_root(root)
    path = state_path(root)
    ensure_managed_components(root, path, "workspace state")
    if path.is_symlink() or not path.is_file():
        raise UsageError(f"workspace is not initialized: {root}")
    value = read_json(path)
    return validate_loaded_experiment(value)


def save_experiment(root: Path, experiment: dict[str, Any]) -> None:
    write_json_atomic(state_path(root), experiment)


def validate_custody_root(root: Path) -> None:
    ensure_no_symlink_components(root, usage=True)
    try:
        root_stat = root.lstat()
    except FileNotFoundError as exc:
        raise UsageError(f"workspace does not exist: {root}") from exc
    if not stat.S_ISDIR(root_stat.st_mode):
        raise UsageError(f"workspace is not a directory: {root}")
    if root_stat.st_uid != os.geteuid():
        raise UsageError("workspace must be owned by the current user")
    if stat.S_IMODE(root_stat.st_mode) & 0o077:
        raise UsageError("workspace custody requires ROOT mode 0700")
    control = root / CONTROL_DIR
    try:
        control_stat = control.lstat()
    except FileNotFoundError as exc:
        raise UsageError(f"workspace is not initialized: {root}") from exc
    if stat.S_ISLNK(control_stat.st_mode) or not stat.S_ISDIR(control_stat.st_mode):
        raise UsageError("private controller directory is not a regular directory")
    if control_stat.st_uid != os.geteuid() or stat.S_IMODE(control_stat.st_mode) & 0o077:
        raise UsageError("private controller directory custody is invalid")
    for relative in (
        f"{CONTROL_DIR}/mappings",
        f"{CONTROL_DIR}/records",
        f"{CONTROL_DIR}/judgments",
        f"{CONTROL_DIR}/staging",
        "workspaces",
        "review-material",
        "review-views",
    ):
        managed = root / relative
        try:
            ensure_managed_components(root, managed, "workspace structure")
            managed_stat = managed.lstat()
        except OperationError as exc:
            raise UsageError(f"workspace structure is invalid: {exc}") from exc
        if not stat.S_ISDIR(managed_stat.st_mode) or managed_stat.st_uid != os.geteuid():
            raise UsageError(f"workspace structure is invalid: {relative}")


@contextmanager
def workspace_lock(root: Path, *, exclusive: bool):
    validate_custody_root(root)
    lock_api = fcntl
    if lock_api is None:  # defensive for direct function use outside main()
        raise UsageError("this helper requires POSIX file custody and locking")
    path = root / CONTROL_DIR / LOCK_FILE
    ensure_managed_components(root, path, "workspace lock")
    flags = os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        lock_stat = os.fstat(descriptor)
        if not stat.S_ISREG(lock_stat.st_mode) or lock_stat.st_uid != os.geteuid():
            raise UsageError("workspace lock custody is invalid")
        operation = lock_api.LOCK_EX if exclusive else lock_api.LOCK_SH
        lock_api.flock(descriptor, operation)
        # A path swap while waiting must not move the operation to stale state.
        current = path.lstat()
        if (current.st_dev, current.st_ino) != (lock_stat.st_dev, lock_stat.st_ino):
            raise OperationError("workspace lock changed while waiting")
        yield
    finally:
        try:
            lock_api.flock(descriptor, lock_api.LOCK_UN)
        finally:
            os.close(descriptor)


def require_object(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise UsageError(f"{location} must be an object")
    return value


def require_list(value: Any, location: str) -> list[Any]:
    if not isinstance(value, list):
        raise UsageError(f"{location} must be an array")
    return value


def require_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise UsageError(f"{location} must be a nonempty string")
    return value


def reject_unknown(value: dict[str, Any], allowed: set[str], location: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise UsageError(f"{location} contains unknown field: {unknown[0]}")


def metadata(value: dict[str, Any], location: str) -> dict[str, Any]:
    result = value.get("metadata", {})
    if not isinstance(result, dict):
        raise UsageError(f"{location}.metadata must be an object")
    return result


def validate_design(raw: Any) -> dict[str, Any]:
    design = require_object(raw, "design")
    reject_unknown(
        design,
        {"schema_version", "round_id", "runs", "review_sets", "metadata"},
        "design",
    )
    if design.get("schema_version") != SCHEMA_VERSION:
        raise UsageError(f"design.schema_version must be {SCHEMA_VERSION}")
    round_id = require_string(design.get("round_id"), "design.round_id")
    design_metadata = metadata(design, "design")

    raw_runs = require_list(design.get("runs"), "design.runs")
    if not raw_runs:
        raise UsageError("design.runs must contain at least one run")
    runs: list[dict[str, Any]] = []
    run_ids: set[str] = set()
    for index, raw_run in enumerate(raw_runs):
        location = f"design.runs[{index}]"
        run = require_object(raw_run, location)
        reject_unknown(run, {"id", "condition", "case", "metadata"}, location)
        run_id = require_string(run.get("id"), f"{location}.id")
        if run_id in run_ids:
            raise UsageError(f"duplicate run id: {run_id}")
        run_ids.add(run_id)
        condition = require_string(run.get("condition"), f"{location}.condition")
        case = run.get("case")
        if case is not None and not isinstance(case, str):
            raise UsageError(f"{location}.case must be a string or null")
        runs.append(
            {
                "id": run_id,
                "condition": condition,
                "case": case,
                "metadata": metadata(run, location),
            }
        )

    raw_sets = require_list(design.get("review_sets"), "design.review_sets")
    review_sets: list[dict[str, Any]] = []
    set_ids: set[str] = set()
    for set_index, raw_set in enumerate(raw_sets):
        set_location = f"design.review_sets[{set_index}]"
        review_set = require_object(raw_set, set_location)
        reject_unknown(
            review_set, {"id", "candidates", "reviewers", "metadata"}, set_location
        )
        set_id = require_string(review_set.get("id"), f"{set_location}.id")
        if set_id in set_ids:
            raise UsageError(f"duplicate review set id: {set_id}")
        set_ids.add(set_id)

        raw_candidates = require_list(
            review_set.get("candidates"), f"{set_location}.candidates"
        )
        if not raw_candidates:
            raise UsageError(f"{set_location}.candidates must not be empty")
        candidates: list[dict[str, Any]] = []
        candidate_ids: set[str] = set()
        for candidate_index, raw_candidate in enumerate(raw_candidates):
            candidate_location = f"{set_location}.candidates[{candidate_index}]"
            candidate = require_object(raw_candidate, candidate_location)
            reject_unknown(candidate, {"id", "runs", "metadata"}, candidate_location)
            candidate_id = require_string(
                candidate.get("id"), f"{candidate_location}.id"
            )
            if candidate_id in candidate_ids:
                raise UsageError(
                    f"duplicate candidate id in review set {set_id}: {candidate_id}"
                )
            candidate_ids.add(candidate_id)
            candidate_runs = require_list(
                candidate.get("runs"), f"{candidate_location}.runs"
            )
            if not candidate_runs:
                raise UsageError(f"{candidate_location}.runs must not be empty")
            normalized_runs: list[str] = []
            for run_index, candidate_run in enumerate(candidate_runs):
                referenced = require_string(
                    candidate_run, f"{candidate_location}.runs[{run_index}]"
                )
                if referenced not in run_ids:
                    raise UsageError(f"unknown run in {candidate_location}: {referenced}")
                if referenced in normalized_runs:
                    raise UsageError(f"duplicate run in {candidate_location}: {referenced}")
                normalized_runs.append(referenced)
            candidates.append(
                {
                    "id": candidate_id,
                    "runs": normalized_runs,
                    "metadata": metadata(candidate, candidate_location),
                }
            )

        raw_reviewers = require_list(
            review_set.get("reviewers"), f"{set_location}.reviewers"
        )
        if not raw_reviewers:
            raise UsageError(f"{set_location}.reviewers must not be empty")
        reviewers: list[dict[str, Any]] = []
        reviewer_ids: set[str] = set()
        for reviewer_index, raw_reviewer in enumerate(raw_reviewers):
            reviewer_location = f"{set_location}.reviewers[{reviewer_index}]"
            reviewer = require_object(raw_reviewer, reviewer_location)
            reject_unknown(
                reviewer,
                {"id", "candidate_order", "metadata"},
                reviewer_location,
            )
            reviewer_id = require_string(
                reviewer.get("id"), f"{reviewer_location}.id"
            )
            if reviewer_id in reviewer_ids:
                raise UsageError(
                    f"duplicate reviewer id in review set {set_id}: {reviewer_id}"
                )
            reviewer_ids.add(reviewer_id)
            candidate_order = reviewer.get("candidate_order")
            if candidate_order is not None:
                candidate_order = require_list(
                    candidate_order, f"{reviewer_location}.candidate_order"
                )
                for order_index, candidate_id in enumerate(candidate_order):
                    require_string(
                        candidate_id,
                        f"{reviewer_location}.candidate_order[{order_index}]",
                    )
                if len(candidate_order) != len(candidate_ids) or set(
                    candidate_order
                ) != candidate_ids:
                    raise UsageError(
                        f"{reviewer_location}.candidate_order must be a full candidate permutation"
                    )
            reviewers.append(
                {
                    "id": reviewer_id,
                    "candidate_order": candidate_order,
                    "metadata": metadata(reviewer, reviewer_location),
                }
            )

        review_sets.append(
            {
                "id": set_id,
                "candidates": candidates,
                "reviewers": reviewers,
                "metadata": metadata(review_set, set_location),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "round_id": round_id,
        "runs": runs,
        "review_sets": review_sets,
        "metadata": design_metadata,
    }


def require_token(value: Any, location: str) -> str:
    result = require_string(value, location)
    if TOKEN_PATTERN.fullmatch(result) is None:
        raise UsageError(f"{location} must be a 32-character opaque token")
    return result


def require_digest(value: Any, location: str, *, optional: bool = False) -> Optional[str]:
    if value is None and optional:
        return None
    if not isinstance(value, str) or DIGEST_PATTERN.fullmatch(value) is None:
        raise UsageError(f"{location} must be a SHA-256 digest")
    return value


def require_exact_relative(value: Any, expected: str, location: str) -> str:
    if not isinstance(value, str) or value != expected:
        raise UsageError(f"{location} is not a valid managed path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise UsageError(f"{location} is not a valid managed path")
    return value


def validate_loaded_experiment(raw: Any) -> dict[str, Any]:
    experiment = require_object(raw, "workspace state")
    reject_unknown(experiment, {"schema_version", "rounds"}, "workspace state")
    if experiment.get("schema_version") != SCHEMA_VERSION:
        raise UsageError("workspace state has an unsupported schema")
    rounds = require_list(experiment.get("rounds"), "workspace state.rounds")
    round_ids: set[str] = set()
    opaque_tokens: set[str] = set()
    for round_index, raw_round in enumerate(rounds):
        location = f"workspace state.rounds[{round_index}]"
        round_record = require_object(raw_round, location)
        reject_unknown(
            round_record,
            {
                "round_id",
                "round_token",
                "state",
                "runs",
                "review_sets",
                "metadata",
                "mapping_rel",
                "mapping_sha256",
                "judgments_rel",
                "judgments_sha256",
            },
            location,
        )
        round_id = require_string(round_record.get("round_id"), f"{location}.round_id")
        if round_id in round_ids:
            raise UsageError(f"workspace state contains duplicate round: {round_id}")
        round_ids.add(round_id)
        round_token = require_token(
            round_record.get("round_token"), f"{location}.round_token"
        )
        if round_token in opaque_tokens:
            raise UsageError(f"workspace state reuses an opaque token: {round_token}")
        opaque_tokens.add(round_token)
        state = round_record.get("state")
        if state not in {"open", "anonymized", "revealed"}:
            raise UsageError(f"{location}.state is invalid")
        if not isinstance(round_record.get("metadata"), dict):
            raise UsageError(f"{location}.metadata must be an object")

        runs = require_list(round_record.get("runs"), f"{location}.runs")
        if not runs:
            raise UsageError(f"{location}.runs must not be empty")
        run_ids: set[str] = set()
        for run_index, raw_run in enumerate(runs):
            run_location = f"{location}.runs[{run_index}]"
            run = require_object(raw_run, run_location)
            reject_unknown(
                run,
                {
                    "id",
                    "condition",
                    "case",
                    "metadata",
                    "workspace_rel",
                    "record_rel",
                },
                run_location,
            )
            run_id = require_string(run.get("id"), f"{run_location}.id")
            if run_id in run_ids:
                raise UsageError(f"workspace state contains duplicate run: {run_id}")
            run_ids.add(run_id)
            require_string(run.get("condition"), f"{run_location}.condition")
            if run.get("case") is not None and not isinstance(run.get("case"), str):
                raise UsageError(f"{run_location}.case must be a string or null")
            if not isinstance(run.get("metadata"), dict):
                raise UsageError(f"{run_location}.metadata must be an object")
            workspace_rel = require_string(
                run.get("workspace_rel"), f"{run_location}.workspace_rel"
            )
            workspace_parts = Path(workspace_rel).parts
            if (
                len(workspace_parts) != 2
                or workspace_parts[0] != "workspaces"
                or TOKEN_PATTERN.fullmatch(workspace_parts[1]) is None
            ):
                raise UsageError(f"{run_location}.workspace_rel is not a valid managed path")
            workspace_token = workspace_parts[1]
            require_exact_relative(
                workspace_rel,
                f"workspaces/{workspace_token}",
                f"{run_location}.workspace_rel",
            )
            record_rel = require_string(
                run.get("record_rel"), f"{run_location}.record_rel"
            )
            record_parts = Path(record_rel).parts
            if (
                len(record_parts) != 3
                or record_parts[:2] != (CONTROL_DIR, "records")
                or TOKEN_PATTERN.fullmatch(record_parts[2]) is None
            ):
                raise UsageError(f"{run_location}.record_rel is not a valid managed path")
            require_exact_relative(
                record_rel,
                f"{CONTROL_DIR}/records/{record_parts[2]}",
                f"{run_location}.record_rel",
            )
            for opaque in (workspace_token, record_parts[2]):
                if opaque in opaque_tokens:
                    raise UsageError(f"workspace state reuses an opaque token: {opaque}")
                opaque_tokens.add(opaque)

        review_sets = require_list(
            round_record.get("review_sets"), f"{location}.review_sets"
        )
        review_set_ids: set[str] = set()
        for set_index, raw_set in enumerate(review_sets):
            set_location = f"{location}.review_sets[{set_index}]"
            review_set = require_object(raw_set, set_location)
            reject_unknown(
                review_set,
                {"id", "candidates", "reviewers", "metadata"},
                set_location,
            )
            set_id = require_string(review_set.get("id"), f"{set_location}.id")
            if set_id in review_set_ids:
                raise UsageError(f"workspace state contains duplicate review set: {set_id}")
            review_set_ids.add(set_id)
            if not isinstance(review_set.get("metadata"), dict):
                raise UsageError(f"{set_location}.metadata must be an object")
            candidates = require_list(
                review_set.get("candidates"), f"{set_location}.candidates"
            )
            if not candidates:
                raise UsageError(f"{set_location}.candidates must not be empty")
            candidate_ids: set[str] = set()
            for candidate_index, raw_candidate in enumerate(candidates):
                candidate_location = f"{set_location}.candidates[{candidate_index}]"
                candidate = require_object(raw_candidate, candidate_location)
                reject_unknown(
                    candidate,
                    {"id", "runs", "metadata"},
                    candidate_location,
                )
                candidate_id = require_string(
                    candidate.get("id"), f"{candidate_location}.id"
                )
                if candidate_id in candidate_ids:
                    raise UsageError(
                        f"workspace state contains duplicate candidate: {candidate_id}"
                    )
                candidate_ids.add(candidate_id)
                if not isinstance(candidate.get("metadata"), dict):
                    raise UsageError(f"{candidate_location}.metadata must be an object")
                candidate_runs = require_list(
                    candidate.get("runs"), f"{candidate_location}.runs"
                )
                if not candidate_runs:
                    raise UsageError(f"{candidate_location}.runs must not be empty")
                seen_candidate_runs: set[str] = set()
                for candidate_run in candidate_runs:
                    referenced = require_string(candidate_run, f"{candidate_location}.runs")
                    if referenced not in run_ids:
                        raise UsageError(
                            f"workspace state contains unknown run reference: {referenced}"
                        )
                    if referenced in seen_candidate_runs:
                        raise UsageError(
                            f"workspace state contains duplicate run reference: {referenced}"
                        )
                    seen_candidate_runs.add(referenced)
            reviewers = require_list(
                review_set.get("reviewers"), f"{set_location}.reviewers"
            )
            if not reviewers:
                raise UsageError(f"{set_location}.reviewers must not be empty")
            reviewer_ids: set[str] = set()
            for reviewer_index, raw_reviewer in enumerate(reviewers):
                reviewer_location = f"{set_location}.reviewers[{reviewer_index}]"
                reviewer = require_object(raw_reviewer, reviewer_location)
                reject_unknown(
                    reviewer,
                    {
                        "id",
                        "candidate_order",
                        "metadata",
                        "material_rel",
                        "view_rel",
                        "view_token",
                    },
                    reviewer_location,
                )
                reviewer_id = require_string(
                    reviewer.get("id"), f"{reviewer_location}.id"
                )
                if reviewer_id in reviewer_ids:
                    raise UsageError(
                        f"workspace state contains duplicate reviewer: {reviewer_id}"
                    )
                reviewer_ids.add(reviewer_id)
                if not isinstance(reviewer.get("metadata"), dict):
                    raise UsageError(f"{reviewer_location}.metadata must be an object")
                order = reviewer.get("candidate_order")
                if order is not None:
                    order = require_list(order, f"{reviewer_location}.candidate_order")
                    if (
                        len(order) != len(candidate_ids)
                        or any(not isinstance(item, str) for item in order)
                        or set(order) != candidate_ids
                    ):
                        raise UsageError(
                            f"{reviewer_location}.candidate_order is not a full permutation"
                        )
                view_token = require_token(
                    reviewer.get("view_token"), f"{reviewer_location}.view_token"
                )
                material_rel = require_string(
                    reviewer.get("material_rel"), f"{reviewer_location}.material_rel"
                )
                material_parts = Path(material_rel).parts
                if (
                    len(material_parts) != 2
                    or material_parts[0] != "review-material"
                    or TOKEN_PATTERN.fullmatch(material_parts[1]) is None
                ):
                    raise UsageError(
                        f"{reviewer_location}.material_rel is not a valid managed path"
                    )
                require_exact_relative(
                    material_rel,
                    f"review-material/{material_parts[1]}",
                    f"{reviewer_location}.material_rel",
                )
                require_exact_relative(
                    reviewer.get("view_rel"),
                    f"review-views/{round_token}/{view_token}",
                    f"{reviewer_location}.view_rel",
                )
                for opaque in (view_token, material_parts[1]):
                    if opaque in opaque_tokens:
                        raise UsageError(f"workspace state reuses an opaque token: {opaque}")
                    opaque_tokens.add(opaque)

        require_exact_relative(
            round_record.get("mapping_rel"),
            f"{CONTROL_DIR}/mappings/{round_token}.json",
            f"{location}.mapping_rel",
        )
        require_exact_relative(
            round_record.get("judgments_rel"),
            f"{CONTROL_DIR}/judgments/{round_token}.json",
            f"{location}.judgments_rel",
        )
        mapping_digest = require_digest(
            round_record.get("mapping_sha256"),
            f"{location}.mapping_sha256",
            optional=True,
        )
        judgment_digest = require_digest(
            round_record.get("judgments_sha256"),
            f"{location}.judgments_sha256",
            optional=True,
        )
        if state == "open" and (mapping_digest is not None or judgment_digest is not None):
            raise UsageError(f"{location} has digests inconsistent with open state")
        if state == "anonymized" and (
            mapping_digest is None or judgment_digest is not None
        ):
            raise UsageError(f"{location} has digests inconsistent with anonymized state")
        if state == "revealed" and (
            mapping_digest is None or judgment_digest is None
        ):
            raise UsageError(f"{location} has digests inconsistent with revealed state")
    return experiment


def token(existing: set[str]) -> str:
    while True:
        candidate = secrets.token_hex(16)
        if candidate not in existing:
            existing.add(candidate)
            return candidate


def experiment_tokens(experiment: dict[str, Any]) -> set[str]:
    results: set[str] = set()
    for round_record in experiment["rounds"]:
        results.add(round_record["round_token"])
        for run in round_record["runs"]:
            results.add(Path(run["workspace_rel"]).name)
            results.add(Path(run["record_rel"]).name)
        for review_set in round_record["review_sets"]:
            for reviewer in review_set["reviewers"]:
                results.add(reviewer["view_token"])
                results.add(Path(reviewer["material_rel"]).name)
    return results


def find_round(experiment: dict[str, Any], round_id: str) -> dict[str, Any]:
    for round_record in experiment["rounds"]:
        if round_record.get("round_id") == round_id:
            return round_record
    raise UsageError(f"round does not exist: {round_id}")


def init_workspace(root: Path) -> dict[str, Any]:
    if root.exists():
        if not root.is_dir():
            raise UsageError("ROOT must be a directory")
        if root.lstat().st_uid != os.geteuid():
            raise UsageError("ROOT must be owned by the current user")
        try:
            occupied = next(root.iterdir(), None)
        except OSError as exc:
            raise UsageError(f"cannot inspect ROOT: {root}") from exc
        if occupied is not None:
            raise UsageError("ROOT must be empty")
    else:
        parent = root.parent
        ensure_no_symlink_components(parent, usage=True)
        if not parent.is_dir():
            raise UsageError(f"ROOT parent does not exist: {parent}")
        root.mkdir(mode=0o700)
        fsync_directory(parent)
    os.chmod(root, 0o700)
    for relative in (
        CONTROL_DIR,
        f"{CONTROL_DIR}/mappings",
        f"{CONTROL_DIR}/records",
        f"{CONTROL_DIR}/judgments",
        f"{CONTROL_DIR}/staging",
        "workspaces",
        "review-material",
        "review-views",
    ):
        (root / relative).mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(root / relative, 0o700)
    lock_path = root / CONTROL_DIR / LOCK_FILE
    descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(descriptor)
    fsync_directory(lock_path.parent)
    experiment = {"schema_version": SCHEMA_VERSION, "rounds": []}
    save_experiment(root, experiment)
    fsync_directory(root)
    return {"schema_version": SCHEMA_VERSION, "root": str(root), "rounds": []}


def add_round(root: Path, design_path: Path) -> dict[str, Any]:
    experiment = load_experiment(root)
    design = validate_design(read_json(design_path, design=True))
    if any(item.get("round_id") == design["round_id"] for item in experiment["rounds"]):
        raise OperationError(f"round already exists: {design['round_id']}")

    used = experiment_tokens(experiment)
    round_token = token(used)
    runs: list[dict[str, Any]] = []
    for run in design["runs"]:
        run_token = token(used)
        record_token = token(used)
        runs.append(
            {
                **run,
                "workspace_rel": f"workspaces/{run_token}",
                "record_rel": f"{CONTROL_DIR}/records/{record_token}",
            }
        )

    review_sets: list[dict[str, Any]] = []
    for review_set in design["review_sets"]:
        reviewers: list[dict[str, Any]] = []
        for reviewer in review_set["reviewers"]:
            material_token = token(used)
            view_token = token(used)
            reviewers.append(
                {
                    **reviewer,
                    "material_rel": f"review-material/{material_token}",
                    "view_rel": f"review-views/{round_token}/{view_token}",
                    "view_token": view_token,
                }
            )
        review_sets.append({**review_set, "reviewers": reviewers})

    round_record = {
        "round_id": design["round_id"],
        "round_token": round_token,
        "state": "open",
        "runs": runs,
        "review_sets": review_sets,
        "metadata": design["metadata"],
        "mapping_rel": f"{CONTROL_DIR}/mappings/{round_token}.json",
        "mapping_sha256": None,
        "judgments_rel": f"{CONTROL_DIR}/judgments/{round_token}.json",
        "judgments_sha256": None,
    }

    created: list[Path] = []
    try:
        for run in runs:
            workspace = root / run["workspace_rel"]
            (workspace / "input").mkdir(mode=0o700, parents=True)
            (workspace / "artifact").mkdir(mode=0o700)
            record_dir = root / run["record_rel"]
            record_dir.mkdir(mode=0o700, parents=True)
            fsync_directory(workspace)
            fsync_directory(workspace.parent)
            fsync_directory(record_dir.parent)
            created.extend([workspace, record_dir])
        for review_set in review_sets:
            for reviewer in review_set["reviewers"]:
                material_dir = root / reviewer["material_rel"]
                material_dir.mkdir(mode=0o700, parents=True)
                fsync_directory(material_dir.parent)
                created.append(material_dir)
        experiment["rounds"].append(round_record)
        save_experiment(root, experiment)
    except Exception:
        for path in reversed(created):
            if path.exists():
                shutil.rmtree(path)
        raise

    return {
        "schema_version": SCHEMA_VERSION,
        "round_id": design["round_id"],
        "state": "open",
        "run_count": len(runs),
        "review_set_count": len(review_sets),
        "reviewer_count": sum(len(item["reviewers"]) for item in review_sets),
    }


def assignment_view(root: Path, round_record: dict[str, Any]) -> dict[str, Any]:
    reviews: list[dict[str, Any]] = []
    for review_set in round_record["review_sets"]:
        for reviewer in review_set["reviewers"]:
            reviews.append(
                {
                    "review_set_id": review_set["id"],
                    "reviewer_id": reviewer["id"],
                    "metadata": reviewer["metadata"],
                    "material_dir": str(root / reviewer["material_rel"]),
                    "view_dir": str(root / reviewer["view_rel"]),
                    "candidates": [
                        {
                            "id": candidate["id"],
                            "runs": list(candidate["runs"]),
                            "metadata": candidate["metadata"],
                        }
                        for candidate in review_set["candidates"]
                    ],
                }
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "round_id": round_record["round_id"],
        "state": round_record["state"],
        "mapping_path": str(root / round_record["mapping_rel"]),
        "judgments_path": str(root / round_record["judgments_rel"]),
        "runs": [
            {
                "id": run["id"],
                "condition": run["condition"],
                "case": run["case"],
                "metadata": run["metadata"],
                "workspace": str(root / run["workspace_rel"]),
                "record_dir": str(root / run["record_rel"]),
            }
            for run in round_record["runs"]
        ],
        "reviews": reviews,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    initial = path.lstat()
    if stat.S_ISLNK(initial.st_mode) or not stat.S_ISREG(initial.st_mode):
        raise OperationError(f"file is not a regular file: {path}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (initial.st_dev, initial.st_ino):
            raise OperationError(f"file changed while reading: {path}")
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        final = os.fstat(descriptor)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(opened, field) != getattr(final, field) for field in stable_fields):
            raise OperationError(f"file changed while reading: {path}")
    finally:
        os.close(descriptor)
    return digest.hexdigest()


def _tree_snapshot(
    entries: list[dict[str, Any]], *, format_version: str = "tree-v3"
) -> dict[str, Any]:
    encoded = json.dumps(
        entries, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return {
        "format": format_version,
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "file_count": sum(item["type"] != "directory" for item in entries),
        "entries": entries,
    }


def validate_contained_symlink(relative: str, target: str, label: str) -> None:
    """Require a relative link target that remains inside its copied tree."""

    if not target or Path(target).is_absolute():
        raise OperationError(f"{label} symlink target escapes copied tree: {target!r}")
    normalized = Path(os.path.normpath(str(Path(relative).parent / target)))
    if normalized.is_absolute() or normalized == Path("..") or (
        normalized.parts and normalized.parts[0] == ".."
    ):
        raise OperationError(f"{label} symlink target escapes copied tree: {target!r}")


def read_contained_symlink(
    path: Path,
    tree_root: Path,
    label: str,
) -> str:
    initial = path.lstat()
    if not stat.S_ISLNK(initial.st_mode):
        raise OperationError(f"source changed during anonymization: {path}")
    target = os.readlink(path)
    final = path.lstat()
    stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(initial, field) != getattr(final, field) for field in stable_fields):
        raise OperationError(f"source changed during anonymization: {path}")
    relative = path.relative_to(tree_root).as_posix()
    validate_contained_symlink(relative, target, label)
    return target


def scan_regular_tree(
    path: Path, label: str, root: Optional[Path] = None
) -> dict[str, Any]:
    if root is not None:
        ensure_managed_components(root, path, label)
    try:
        root_mode = path.lstat().st_mode
    except FileNotFoundError as exc:
        raise OperationError(f"{label} directory is missing: {path}") from exc
    if stat.S_ISLNK(root_mode):
        raise OperationError(f"{label} contains a symbolic link: {path}")
    if not stat.S_ISDIR(root_mode):
        raise OperationError(f"{label} directory is missing: {path}")
    entries: list[dict[str, Any]] = [
        {
            "path": ".",
            "type": "directory",
            "mode": stat.S_IMODE(root_mode),
        }
    ]
    def walk_error(error: OSError) -> None:
        raise OperationError(f"{label} cannot be read: {error.filename}") from error

    for current, directories, filenames in os.walk(
        path, followlinks=False, onerror=walk_error
    ):
        directories.sort(key=os.fsencode)
        filenames.sort(key=os.fsencode)
        current_path = Path(current)
        for name in directories:
            candidate = current_path / name
            mode = candidate.lstat().st_mode
            if stat.S_ISLNK(mode):
                entries.append(
                    {
                        "path": candidate.relative_to(path).as_posix(),
                        "type": "symlink",
                        "target": read_contained_symlink(candidate, path, label),
                    }
                )
                continue
            if not stat.S_ISDIR(mode):
                raise OperationError(f"{label} contains a special file: {candidate}")
            entries.append(
                {
                    "path": candidate.relative_to(path).as_posix(),
                    "type": "directory",
                    "mode": stat.S_IMODE(mode),
                }
            )
        for name in filenames:
            candidate = current_path / name
            mode = candidate.lstat().st_mode
            if stat.S_ISLNK(mode):
                entries.append(
                    {
                        "path": candidate.relative_to(path).as_posix(),
                        "type": "symlink",
                        "target": read_contained_symlink(candidate, path, label),
                    }
                )
                continue
            if not stat.S_ISREG(mode):
                raise OperationError(f"{label} contains a special file: {candidate}")
            entries.append(
                {
                    "path": candidate.relative_to(path).as_posix(),
                    "type": "file",
                    "mode": stat.S_IMODE(mode),
                    "sha256": sha256_file(candidate),
                }
            )
    entries[1:] = sorted(entries[1:], key=lambda item: os.fsencode(item["path"]))
    result = _tree_snapshot(entries)
    if result["file_count"] == 0:
        raise OperationError(f"{label} directory contains no artifact entries: {path}")
    return result


def legacy_file_hashes(snapshot: dict[str, Any]) -> dict[str, str]:
    if snapshot.get("format") in {"tree-v2", "tree-v3"}:
        return {
            item["path"]: item["sha256"]
            for item in snapshot["entries"]
            if item["type"] == "file"
        }
    return snapshot  # type: ignore[return-value]


def _copy_regular_file(source: Path, destination: Path, expected: dict[str, Any]) -> None:
    source_mode = source.lstat().st_mode
    if stat.S_ISLNK(source_mode) or not stat.S_ISREG(source_mode):
        raise OperationError(f"source changed during anonymization: {source}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    source_fd = os.open(source, flags)
    destination_fd: Optional[int] = None
    digest = hashlib.sha256()
    try:
        opened = os.fstat(source_fd)
        if not stat.S_ISREG(opened.st_mode):
            raise OperationError(f"source changed during anonymization: {source}")
        destination_fd = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        while True:
            chunk = os.read(source_fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            view = memoryview(chunk)
            while view:
                written = os.write(destination_fd, view)
                view = view[written:]
        final = os.fstat(source_fd)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(opened, field) != getattr(final, field) for field in stable_fields):
            raise OperationError(f"source changed during anonymization: {source}")
        if digest.hexdigest() != expected["sha256"]:
            raise OperationError(f"source changed during anonymization: {source}")
        os.fchmod(destination_fd, expected["mode"])
    finally:
        if destination_fd is not None:
            os.close(destination_fd)
        os.close(source_fd)


def copy_regular_tree(
    source: Path,
    destination: Path,
    expected: dict[str, Any],
    *,
    label: str,
    root: Path,
) -> dict[str, Any]:
    if expected.get("format") != "tree-v3":
        raise OperationError("cannot publish a legacy tree snapshot")
    destination.mkdir(mode=0o700)
    directories = [
        item for item in expected["entries"] if item["type"] == "directory"
    ]
    files = [item for item in expected["entries"] if item["type"] == "file"]
    symlinks = [item for item in expected["entries"] if item["type"] == "symlink"]
    for entry in sorted(
        (item for item in directories if item["path"] != "."),
        key=lambda item: (len(Path(item["path"]).parts), os.fsencode(item["path"])),
    ):
        (destination / entry["path"]).mkdir(mode=0o700)
    for entry in files:
        _copy_regular_file(source / entry["path"], destination / entry["path"], entry)
    for entry in symlinks:
        source_link = source / entry["path"]
        target = read_contained_symlink(source_link, source, label)
        if target != entry["target"]:
            raise OperationError(f"source changed during anonymization: {source_link}")
        destination_link = destination / entry["path"]
        os.symlink(target, destination_link)
        if os.readlink(destination_link) != target:
            raise OperationError(f"copied artifact changed during anonymization: {destination_link}")
    for entry in sorted(
        directories,
        key=lambda item: len(Path(item["path"]).parts),
        reverse=True,
    ):
        target = destination if entry["path"] == "." else destination / entry["path"]
        os.chmod(target, entry["mode"])
    source_after = scan_regular_tree(source, label, root)
    if source_after != expected:
        raise OperationError(f"source changed during anonymization: {source}")
    copied = scan_regular_tree(destination, "blinded copy", root)
    if copied != expected:
        raise OperationError(f"copied artifacts do not match source: {destination}")
    return copied


def candidate_label(index: int) -> str:
    label = ""
    value = index + 1
    while value:
        value, remainder = divmod(value - 1, 26)
        label = chr(ord("A") + remainder) + label
    return label


def review_set_uses_cases(
    review_set: dict[str, Any], run_by_id: dict[str, dict[str, Any]]
) -> bool:
    return any(
        run_by_id[run_id]["case"] is not None
        for candidate in review_set["candidates"]
        for run_id in candidate["runs"]
    )


def reviewer_samples(
    review_set: dict[str, Any],
    run_by_id: dict[str, dict[str, Any]],
    random: Any,
) -> dict[str, list[dict[str, str]]]:
    """Create reviewer-local labels without exposing declared case identities."""

    if not review_set_uses_cases(review_set, run_by_id):
        result: dict[str, list[dict[str, str]]] = {}
        for candidate in review_set["candidates"]:
            sample_runs = list(candidate["runs"])
            random.shuffle(sample_runs)
            result[candidate["id"]] = [
                {"label": f"S{index:03d}", "run_id": run_id}
                for index, run_id in enumerate(sample_runs, start=1)
            ]
        return result

    block_keys: list[tuple[str, ...]] = []
    seen_cases: set[str] = set()
    run_block: dict[tuple[str, str], tuple[str, ...]] = {}
    for candidate in review_set["candidates"]:
        candidate_id = candidate["id"]
        for run_id in candidate["runs"]:
            case = run_by_id[run_id]["case"]
            if case is None:
                block_key = ("occurrence", candidate_id, run_id)
                block_keys.append(block_key)
            else:
                block_key = ("case", case)
                if case not in seen_cases:
                    seen_cases.add(case)
                    block_keys.append(block_key)
            run_block[(candidate_id, run_id)] = block_key

    random.shuffle(block_keys)
    block_labels = {
        block_key: f"B{index:03d}"
        for index, block_key in enumerate(block_keys, start=1)
    }
    result = {}
    for candidate in review_set["candidates"]:
        candidate_id = candidate["id"]
        grouped: dict[tuple[str, ...], list[str]] = {}
        for run_id in candidate["runs"]:
            grouped.setdefault(run_block[(candidate_id, run_id)], []).append(run_id)
        samples: list[dict[str, str]] = []
        for block_key in block_keys:
            sample_runs = grouped.get(block_key)
            if sample_runs is None:
                continue
            random.shuffle(sample_runs)
            samples.extend(
                {
                    "label": f"{block_labels[block_key]}-S{index:03d}",
                    "run_id": run_id,
                }
                for index, run_id in enumerate(sample_runs, start=1)
            )
        result[candidate_id] = samples
    return result


def validate_sample_labels(
    presented: list[tuple[str, str, list[dict[str, Any]]]],
    review_set: dict[str, Any],
    run_by_id: dict[str, dict[str, Any]],
) -> None:
    labels = [
        sample["label"]
        for _, _, samples in presented
        for sample in samples
    ]
    uses_cases = review_set_uses_cases(review_set, run_by_id)
    legacy = all(LEGACY_SAMPLE_PATTERN.fullmatch(label) is not None for label in labels)
    if not uses_cases or legacy:
        for candidate_location, _, samples in presented:
            for sample_index, sample in enumerate(samples, start=1):
                if sample["label"] != f"S{sample_index:03d}":
                    raise UsageError(
                        f"{candidate_location}.samples[{sample_index - 1}].label is invalid"
                    )
        return

    if not all(BLOCK_SAMPLE_PATTERN.fullmatch(label) is not None for label in labels):
        raise UsageError("cased sample labels mix incompatible presentation formats")

    semantic_by_block: dict[int, tuple[str, ...]] = {}
    block_by_semantic: dict[tuple[str, ...], int] = {}
    suffixes: dict[tuple[str, int], list[int]] = {}
    block_numbers: set[int] = set()
    for candidate_location, candidate_id, samples in presented:
        coordinates: list[tuple[int, int]] = []
        for sample_index, sample in enumerate(samples):
            match = BLOCK_SAMPLE_PATTERN.fullmatch(sample["label"])
            assert match is not None
            block_number, sample_number = (int(value) for value in match.groups())
            coordinates.append((block_number, sample_number))
            block_numbers.add(block_number)
            run_id = sample["run_id"]
            case = run_by_id[run_id]["case"]
            semantic = (
                ("case", case)
                if case is not None
                else ("occurrence", candidate_id, run_id)
            )
            if semantic_by_block.setdefault(block_number, semantic) != semantic:
                raise UsageError("cased sample block joins unrelated occurrences")
            if block_by_semantic.setdefault(semantic, block_number) != block_number:
                raise UsageError("cased sample block does not preserve declared case alignment")
            suffixes.setdefault((candidate_id, block_number), []).append(sample_number)
        if coordinates != sorted(coordinates):
            raise UsageError(f"{candidate_location}.samples are not in opaque block order")

    expected_block_count = len(block_by_semantic)
    if block_numbers != set(range(1, expected_block_count + 1)):
        raise UsageError("cased sample block labels are not a dense opaque namespace")
    for (candidate_id, block_number), observed in suffixes.items():
        if observed != list(range(1, len(observed) + 1)):
            raise UsageError(
                f"cased sample repetitions are invalid for {candidate_id} block B{block_number:03d}"
            )


def validate_tree_snapshot(value: Any, location: str) -> dict[str, Any]:
    snapshot = require_object(value, location)
    format_version = snapshot.get("format")
    if format_version not in {"tree-v2", "tree-v3"}:
        # Version 1 mappings stored only regular-file content hashes. They remain
        # readable, but all newly published mappings use topology-aware trees.
        for relative, digest in snapshot.items():
            if (
                not isinstance(relative, str)
                or not relative
                or Path(relative).is_absolute()
                or ".." in Path(relative).parts
                or Path(relative).as_posix() != relative
            ):
                raise UsageError(f"{location} contains an invalid relative path")
            require_digest(digest, f"{location}.{relative}")
        if not snapshot:
            raise UsageError(f"{location} contains no regular files")
        return snapshot
    reject_unknown(
        snapshot,
        {"format", "sha256", "file_count", "entries"},
        location,
    )
    require_digest(snapshot.get("sha256"), f"{location}.sha256")
    file_count = snapshot.get("file_count")
    if not isinstance(file_count, int) or isinstance(file_count, bool) or file_count < 1:
        raise UsageError(f"{location}.file_count must be a positive integer")
    raw_entries = require_list(snapshot.get("entries"), f"{location}.entries")
    entries: list[dict[str, Any]] = []
    paths: set[str] = set()
    for index, raw_entry in enumerate(raw_entries):
        entry_location = f"{location}.entries[{index}]"
        entry = require_object(raw_entry, entry_location)
        entry_type = entry.get("type")
        allowed = {"path", "type"}
        if entry_type in {"file", "directory"}:
            allowed.add("executable_bits" if format_version == "tree-v2" else "mode")
        if entry_type == "file":
            allowed.add("sha256")
        if entry_type == "symlink":
            allowed.add("target")
        reject_unknown(entry, allowed, entry_location)
        relative = entry.get("path")
        if not isinstance(relative, str) or not relative:
            raise UsageError(f"{entry_location}.path must be a relative path")
        relative_path = Path(relative)
        if (
            (relative == "." and entry_type != "directory")
            or (relative != "." and relative_path.is_absolute())
            or ".." in relative_path.parts
            or relative_path.as_posix() != relative
        ):
            raise UsageError(f"{entry_location}.path is invalid")
        if relative in paths:
            raise UsageError(f"{location} contains duplicate path: {relative}")
        paths.add(relative)
        if entry_type not in {"file", "directory", "symlink"}:
            raise UsageError(f"{entry_location}.type is invalid")
        if entry_type in {"file", "directory"}:
            if format_version == "tree-v2":
                executable_bits = entry.get("executable_bits")
                if (
                    not isinstance(executable_bits, int)
                    or isinstance(executable_bits, bool)
                    or executable_bits < 0
                    or executable_bits & ~0o111
                ):
                    raise UsageError(f"{entry_location}.executable_bits is invalid")
            else:
                mode = entry.get("mode")
                if (
                    not isinstance(mode, int)
                    or isinstance(mode, bool)
                    or mode < 0
                    or mode & ~0o7777
                ):
                    raise UsageError(f"{entry_location}.mode is invalid")
        if entry_type == "file":
            require_digest(entry.get("sha256"), f"{entry_location}.sha256")
        if entry_type == "symlink":
            target = entry.get("target")
            if not isinstance(target, str):
                raise UsageError(f"{entry_location}.target must be a string")
            try:
                validate_contained_symlink(relative, target, entry_location)
            except OperationError as exc:
                raise UsageError(str(exc)) from exc
        entries.append(entry)
    if not entries or entries[0].get("path") != ".":
        raise UsageError(f"{location} is missing its root directory entry")
    if sum(item["type"] != "directory" for item in entries) != file_count:
        raise UsageError(f"{location}.file_count does not match entries")
    directories = {item["path"] for item in entries if item["type"] == "directory"}
    for entry in entries:
        if entry["path"] == ".":
            continue
        parent = Path(entry["path"]).parent.as_posix()
        if parent == "":
            parent = "."
        if parent not in directories:
            raise UsageError(f"{location} is missing parent directory: {parent}")
    canonical = _tree_snapshot(entries, format_version=format_version)
    if canonical["sha256"] != snapshot["sha256"]:
        raise UsageError(f"{location}.sha256 does not match entries")
    return snapshot


def validate_mapping(
    raw: Any,
    root: Path,
    round_record: dict[str, Any],
) -> dict[str, Any]:
    try:
        mapping = require_object(raw, "private mapping")
        reject_unknown(
            mapping,
            {"schema_version", "round_id", "reviews", "source_hashes", "copy_hashes"},
            "private mapping",
        )
        if mapping.get("schema_version") != SCHEMA_VERSION:
            raise UsageError("private mapping has an unsupported schema")
        if mapping.get("round_id") != round_record["round_id"]:
            raise UsageError("private mapping has the wrong round")
        source_hashes = require_object(mapping.get("source_hashes"), "source_hashes")
        reject_unknown(source_hashes, {"runs", "materials"}, "source_hashes")
        run_hashes = require_object(source_hashes.get("runs"), "source_hashes.runs")
        material_hashes = require_object(
            source_hashes.get("materials"), "source_hashes.materials"
        )
        run_ids = {run["id"] for run in round_record["runs"]}
        if set(run_hashes) != run_ids:
            raise UsageError("private mapping run hashes do not match round runs")
        for run_id, snapshot in run_hashes.items():
            validate_tree_snapshot(snapshot, f"source_hashes.runs.{run_id}")

        reviewers: dict[tuple[str, str], dict[str, Any]] = {}
        reviewer_by_token: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
        for review_set in round_record["review_sets"]:
            for reviewer in review_set["reviewers"]:
                reviewers[(review_set["id"], reviewer["id"])] = reviewer
                reviewer_by_token[reviewer["view_token"]] = (review_set, reviewer)
        if set(material_hashes) != set(reviewer_by_token):
            raise UsageError("private mapping material hashes do not match reviewers")
        for view_token, snapshot in material_hashes.items():
            validate_tree_snapshot(snapshot, f"source_hashes.materials.{view_token}")

        copy_hashes = require_object(mapping.get("copy_hashes"), "copy_hashes")
        if set(copy_hashes) != set(reviewer_by_token):
            raise UsageError("private mapping copy hashes do not match reviewers")
        for view_token, copied in copy_hashes.items():
            copied_object = require_object(copied, f"copy_hashes.{view_token}")
            if copied_object.get("format") in {"tree-v2", "tree-v3"} or all(
                isinstance(value, str) for value in copied_object.values()
            ):
                validate_tree_snapshot(copied_object, f"copy_hashes.{view_token}")
            else:
                reject_unknown(
                    copied_object,
                    {"brief", "candidates"},
                    f"copy_hashes.{view_token}",
                )
                validate_tree_snapshot(
                    copied_object.get("brief"), f"copy_hashes.{view_token}.brief"
                )
                validate_tree_snapshot(
                    copied_object.get("candidates"),
                    f"copy_hashes.{view_token}.candidates",
                )

        raw_reviews = require_list(mapping.get("reviews"), "private mapping.reviews")
        if len(raw_reviews) != len(reviewers):
            raise UsageError("private mapping review count does not match round")
        seen_reviews: set[tuple[str, str]] = set()
        for review_index, raw_review in enumerate(raw_reviews):
            review_location = f"private mapping.reviews[{review_index}]"
            review = require_object(raw_review, review_location)
            reject_unknown(
                review,
                {"review_set_id", "reviewer_id", "view_dir", "candidates"},
                review_location,
            )
            review_set_id = require_string(
                review.get("review_set_id"), f"{review_location}.review_set_id"
            )
            reviewer_id = require_string(
                review.get("reviewer_id"), f"{review_location}.reviewer_id"
            )
            key = (review_set_id, reviewer_id)
            if key not in reviewers or key in seen_reviews:
                raise UsageError(f"{review_location} does not match a configured reviewer")
            seen_reviews.add(key)
            reviewer = reviewers[key]
            review_set = next(
                item for item in round_record["review_sets"] if item["id"] == key[0]
            )
            if review.get("view_dir") != str(root / reviewer["view_rel"]):
                raise UsageError(f"{review_location}.view_dir is not the managed view")
            candidates = require_list(
                review.get("candidates"), f"{review_location}.candidates"
            )
            configured_candidates = {
                item["id"]: item for item in review_set["candidates"]
            }
            if len(candidates) != len(configured_candidates):
                raise UsageError(f"{review_location}.candidates has the wrong size")
            seen_candidates: set[str] = set()
            presented: list[tuple[str, str, list[dict[str, Any]]]] = []
            for candidate_index, raw_candidate in enumerate(candidates):
                candidate_location = f"{review_location}.candidates[{candidate_index}]"
                candidate = require_object(raw_candidate, candidate_location)
                reject_unknown(
                    candidate,
                    {"label", "candidate_id", "samples"},
                    candidate_location,
                )
                if candidate.get("label") != candidate_label(candidate_index):
                    raise UsageError(f"{candidate_location}.label is invalid")
                candidate_id = require_string(
                    candidate.get("candidate_id"), f"{candidate_location}.candidate_id"
                )
                if candidate_id not in configured_candidates or candidate_id in seen_candidates:
                    raise UsageError(f"{candidate_location}.candidate_id is invalid")
                seen_candidates.add(candidate_id)
                samples = require_list(candidate.get("samples"), f"{candidate_location}.samples")
                expected_runs = configured_candidates[candidate_id]["runs"]
                if len(samples) != len(expected_runs):
                    raise UsageError(f"{candidate_location}.samples has the wrong size")
                sample_runs: list[str] = []
                seen_labels: set[str] = set()
                normalized_samples: list[dict[str, Any]] = []
                for sample_index, raw_sample in enumerate(samples):
                    sample_location = f"{candidate_location}.samples[{sample_index}]"
                    sample = require_object(raw_sample, sample_location)
                    reject_unknown(sample, {"label", "run_id"}, sample_location)
                    label = sample.get("label")
                    if not isinstance(label, str) or not label or label in seen_labels:
                        raise UsageError(f"{sample_location}.label is invalid")
                    seen_labels.add(label)
                    run_id = sample.get("run_id")
                    if not isinstance(run_id, str):
                        raise UsageError(f"{sample_location}.run_id is invalid")
                    sample_runs.append(run_id)
                    normalized_samples.append({"label": label, "run_id": run_id})
                if len(set(sample_runs)) != len(sample_runs) or set(sample_runs) != set(
                    expected_runs
                ):
                    raise UsageError(f"{candidate_location}.samples do not match candidate runs")
                presented.append(
                    (candidate_location, candidate_id, normalized_samples)
                )
            validate_sample_labels(presented, review_set, {
                run["id"]: run for run in round_record["runs"]
            })
        return mapping
    except UsageError as exc:
        raise OperationError(f"private mapping is malformed: {exc}") from exc


def transaction_paths(root: Path, round_record: dict[str, Any]) -> tuple[Path, Path, Path]:
    round_token = round_record["round_token"]
    staging_root = root / CONTROL_DIR / "staging"
    return (
        staging_root / f"{round_token}.prepared",
        staging_root / f"{round_token}.transaction.json",
        root / "review-views" / round_token,
    )


def remove_tree_durable(path: Path) -> None:
    if path.is_symlink():
        raise OperationError(f"refusing to remove symbolic-link transaction path: {path}")
    if path.exists():
        if not path.is_dir():
            raise OperationError(f"transaction path is not a directory: {path}")
        shutil.rmtree(path)
        fsync_directory(path.parent)


def unlink_durable(path: Path) -> None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise OperationError(f"transaction file is not a regular file: {path}")
    path.unlink()
    fsync_directory(path.parent)


def validate_transaction(raw: Any, round_record: dict[str, Any]) -> dict[str, Any]:
    try:
        transaction = require_object(raw, "anonymize transaction")
        reject_unknown(
            transaction,
            {
                "schema_version",
                "kind",
                "round_token",
                "staging_rel",
                "final_rel",
                "mapping_rel",
                "mapping_sha256",
            },
            "anonymize transaction",
        )
        round_token = round_record["round_token"]
        if transaction.get("schema_version") != SCHEMA_VERSION:
            raise UsageError("anonymize transaction has an unsupported schema")
        if transaction.get("kind") != "anonymize":
            raise UsageError("anonymize transaction has an invalid kind")
        if transaction.get("round_token") != round_token:
            raise UsageError("anonymize transaction has the wrong round")
        require_exact_relative(
            transaction.get("staging_rel"),
            f"{CONTROL_DIR}/staging/{round_token}.prepared",
            "anonymize transaction.staging_rel",
        )
        require_exact_relative(
            transaction.get("final_rel"),
            f"review-views/{round_token}",
            "anonymize transaction.final_rel",
        )
        require_exact_relative(
            transaction.get("mapping_rel"),
            round_record["mapping_rel"],
            "anonymize transaction.mapping_rel",
        )
        require_digest(
            transaction.get("mapping_sha256"),
            "anonymize transaction.mapping_sha256",
        )
        return transaction
    except UsageError as exc:
        raise OperationError(f"anonymize transaction is malformed: {exc}") from exc


def recover_anonymize_transaction(
    root: Path,
    round_record: dict[str, Any],
    experiment: dict[str, Any],
) -> bool:
    staging, journal_path, final_round_views = transaction_paths(root, round_record)
    journal_exists = os.path.lexists(journal_path)
    if not journal_exists:
        if os.path.lexists(staging):
            remove_tree_durable(staging)
        return False

    ensure_managed_components(root, journal_path, "anonymize transaction")
    transaction = validate_transaction(read_json(journal_path), round_record)
    expected_mapping_digest = transaction["mapping_sha256"]
    mapping_path = root / round_record["mapping_rel"]
    mapping_exists = os.path.lexists(mapping_path)
    final_exists = os.path.lexists(final_round_views)

    if round_record["state"] == "open":
        if mapping_exists and final_exists:
            ensure_managed_components(root, mapping_path, "private mapping")
            ensure_managed_components(root, final_round_views, "review views")
            if sha256_file(mapping_path) != expected_mapping_digest:
                raise OperationError("prepared private mapping has an unexpected digest")
            mapping = validate_mapping(read_json(mapping_path), root, round_record)
            verify_mapping_integrity(root, round_record, mapping)
            old_state = round_record["state"]
            old_digest = round_record["mapping_sha256"]
            round_record["state"] = "anonymized"
            round_record["mapping_sha256"] = expected_mapping_digest
            try:
                save_experiment(root, experiment)
            except Exception:
                round_record["state"] = old_state
                round_record["mapping_sha256"] = old_digest
                raise
            remove_tree_durable(staging)
            unlink_durable(journal_path)
            return True
        if mapping_exists:
            ensure_managed_components(root, mapping_path, "private mapping")
            if sha256_file(mapping_path) != expected_mapping_digest:
                raise OperationError("prepared private mapping has an unexpected digest")
            unlink_durable(mapping_path)
        if final_exists:
            ensure_managed_components(root, final_round_views, "review views")
            remove_tree_durable(final_round_views)
        remove_tree_durable(staging)
        unlink_durable(journal_path)
        return False

    if not mapping_exists or not final_exists:
        raise OperationError("completed anonymization transaction is incomplete")
    ensure_managed_components(root, mapping_path, "private mapping")
    ensure_managed_components(root, final_round_views, "review views")
    mapping_digest = sha256_file(mapping_path)
    if (
        mapping_digest != expected_mapping_digest
        or mapping_digest != round_record["mapping_sha256"]
    ):
        raise OperationError("completed anonymization transaction digest is invalid")
    remove_tree_durable(staging)
    unlink_durable(journal_path)
    return False


def anonymize(
    root: Path,
    round_record: dict[str, Any],
    experiment: dict[str, Any],
) -> dict[str, Any]:
    recovered = recover_anonymize_transaction(root, round_record, experiment)
    if recovered:
        return {
            "schema_version": SCHEMA_VERSION,
            "round_id": round_record["round_id"],
            "state": "anonymized",
            "view_count": sum(
                len(review_set["reviewers"])
                for review_set in round_record["review_sets"]
            ),
        }
    if round_record["state"] != "open":
        raise OperationError(f"round is not open: {round_record['round_id']}")

    run_by_id = {run["id"]: run for run in round_record["runs"]}
    source_runs: dict[str, dict[str, Any]] = {}
    for run in round_record["runs"]:
        source_runs[run["id"]] = scan_regular_tree(
            root / run["workspace_rel"] / "artifact", "artifact", root
        )

    source_materials: dict[str, dict[str, Any]] = {}
    for review_set in round_record["review_sets"]:
        for reviewer in review_set["reviewers"]:
            source_materials[reviewer["view_token"]] = scan_regular_tree(
                root / reviewer["material_rel"], "review material", root
            )

    staging, journal_path, final_round_views = transaction_paths(root, round_record)
    mapping_path = root / round_record["mapping_rel"]
    for path, label in (
        (staging, "anonymization staging"),
        (journal_path, "anonymize transaction"),
        (final_round_views, "review views"),
        (mapping_path, "private mapping"),
    ):
        if os.path.lexists(path):
            raise OperationError(f"{label} already exists for this round")
    staging.mkdir(mode=0o700)
    fsync_directory(staging.parent)

    random = secrets.SystemRandom()
    mappings: list[dict[str, Any]] = []
    copy_hashes: dict[str, dict[str, Any]] = {}
    prepared = False
    try:
        for review_set in round_record["review_sets"]:
            candidate_by_id = {
                candidate["id"]: candidate for candidate in review_set["candidates"]
            }
            for reviewer in review_set["reviewers"]:
                view_token = reviewer["view_token"]
                staged_view = staging / view_token
                staged_view.mkdir(mode=0o700)
                material_source = root / reviewer["material_rel"]
                brief_copy = copy_regular_tree(
                    material_source,
                    staged_view / "brief",
                    source_materials[view_token],
                    label="review material",
                    root=root,
                )
                candidates_root = staged_view / "candidates"
                candidates_root.mkdir(mode=0o700)

                order = reviewer.get("candidate_order")
                if order is None:
                    order = list(candidate_by_id)
                    random.shuffle(order)
                samples_by_candidate = reviewer_samples(
                    review_set, run_by_id, random
                )
                mapped_candidates: list[dict[str, Any]] = []
                for candidate_index, candidate_id in enumerate(order):
                    label = candidate_label(candidate_index)
                    label_root = candidates_root / label
                    label_root.mkdir(mode=0o700)
                    samples: list[dict[str, str]] = []
                    for sample in samples_by_candidate[candidate_id]:
                        sample_label = sample["label"]
                        run_id = sample["run_id"]
                        artifact_source = root / run_by_id[run_id]["workspace_rel"] / "artifact"
                        copy_regular_tree(
                            artifact_source,
                            label_root / sample_label,
                            source_runs[run_id],
                            label="artifact",
                            root=root,
                        )
                        samples.append({"label": sample_label, "run_id": run_id})
                    mapped_candidates.append(
                        {
                            "label": label,
                            "candidate_id": candidate_id,
                            "samples": samples,
                        }
                    )
                mappings.append(
                    {
                        "review_set_id": review_set["id"],
                        "reviewer_id": reviewer["id"],
                        "view_dir": str(root / reviewer["view_rel"]),
                        "candidates": mapped_candidates,
                    }
                )
                copy_hashes[view_token] = {
                    "brief": brief_copy,
                    "candidates": scan_regular_tree(
                        candidates_root, "blinded candidates", root
                    ),
                }

        for run in round_record["runs"]:
            verify_hash_tree(
                root / run["workspace_rel"] / "artifact",
                source_runs[run["id"]],
                "source artifact",
                root,
            )
        for review_set in round_record["review_sets"]:
            for reviewer in review_set["reviewers"]:
                verify_hash_tree(
                    root / reviewer["material_rel"],
                    source_materials[reviewer["view_token"]],
                    "source review material",
                    root,
                )

        mapping = {
            "schema_version": SCHEMA_VERSION,
            "round_id": round_record["round_id"],
            "reviews": mappings,
            "source_hashes": {
                "runs": source_runs,
                "materials": source_materials,
            },
            "copy_hashes": copy_hashes,
        }
        validate_mapping(mapping, root, round_record)
        mapping_content = json_bytes(mapping)
        mapping_digest = hashlib.sha256(mapping_content).hexdigest()
        transaction = {
            "schema_version": SCHEMA_VERSION,
            "kind": "anonymize",
            "round_token": round_record["round_token"],
            "staging_rel": staging.relative_to(root).as_posix(),
            "final_rel": final_round_views.relative_to(root).as_posix(),
            "mapping_rel": round_record["mapping_rel"],
            "mapping_sha256": mapping_digest,
        }
        write_json_atomic(journal_path, transaction, replace=False)
        prepared = True
        os.rename(staging, final_round_views)
        fsync_directory(staging.parent)
        fsync_directory(final_round_views.parent)
        write_bytes_atomic(mapping_path, mapping_content, replace=False)
        old_state = round_record["state"]
        old_digest = round_record["mapping_sha256"]
        round_record["state"] = "anonymized"
        round_record["mapping_sha256"] = mapping_digest
        try:
            save_experiment(root, experiment)
        except Exception:
            round_record["state"] = old_state
            round_record["mapping_sha256"] = old_digest
            raise
        unlink_durable(journal_path)
    except Exception:
        if not prepared:
            remove_tree_durable(staging)
        raise

    return {
        "schema_version": SCHEMA_VERSION,
        "round_id": round_record["round_id"],
        "state": "anonymized",
        "view_count": len(mappings),
    }


def verify_hash_tree(
    path: Path,
    expected: dict[str, Any],
    label: str,
    root: Path,
) -> None:
    actual = scan_regular_tree(path, label, root)
    if expected.get("format") == "tree-v3":
        matches = actual == expected
    elif expected.get("format") == "tree-v2":
        # Existing mappings recorded only executable bits. Keep them
        # verifiable while all new mappings preserve complete POSIX modes.
        projected_entries: list[dict[str, Any]] = []
        for entry in actual["entries"]:
            projected = {
                key: value
                for key, value in entry.items()
                if key not in {"mode"}
            }
            if entry["type"] in {"file", "directory"}:
                projected["executable_bits"] = entry["mode"] & 0o111
            projected_entries.append(projected)
        matches = (
            _tree_snapshot(projected_entries, format_version="tree-v2") == expected
        )
    else:
        matches = legacy_file_hashes(actual) == expected
    if not matches:
        raise OperationError(f"{label} changed after anonymization: {path}")


def verify_mapping_integrity(
    root: Path,
    round_record: dict[str, Any],
    mapping: dict[str, Any],
) -> None:
    run_by_id = {run["id"]: run for run in round_record["runs"]}
    for run_id, expected in mapping["source_hashes"]["runs"].items():
        verify_hash_tree(
            root / run_by_id[run_id]["workspace_rel"] / "artifact",
            expected,
            "source artifact",
            root,
        )

    reviewer_by_token: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for review_set in round_record["review_sets"]:
        for reviewer in review_set["reviewers"]:
            reviewer_by_token[reviewer["view_token"]] = (review_set, reviewer)
    for view_token, expected in mapping["source_hashes"]["materials"].items():
        _, reviewer = reviewer_by_token[view_token]
        verify_hash_tree(
            root / reviewer["material_rel"],
            expected,
            "source review material",
            root,
        )
    for view_token, expected in mapping["copy_hashes"].items():
        _, reviewer = reviewer_by_token[view_token]
        view = root / reviewer["view_rel"]
        if "brief" in expected and "candidates" in expected:
            verify_hash_tree(
                view / "brief", expected["brief"], "blinded copy", root
            )
            verify_hash_tree(
                view / "candidates",
                expected["candidates"],
                "blinded copy",
                root,
            )
        else:
            actual: dict[str, str] = {}
            for subtree in ("brief", "candidates"):
                snapshot = scan_regular_tree(view / subtree, "blinded copy", root)
                for relative, digest in legacy_file_hashes(snapshot).items():
                    actual[f"{subtree}/{relative}"] = digest
            if actual != expected:
                raise OperationError(f"blinded copy changed after anonymization: {view}")


def read_regular_bytes(path: Path, label: str, root: Path) -> bytes:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as exc:
        raise OperationError(f"{label} is missing: {path}") from exc
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise OperationError(f"{label} must be a regular file: {path}")
    ensure_managed_components(root, path, label)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final = os.fstat(descriptor)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(opened, field) != getattr(final, field) for field in stable_fields):
            raise OperationError(f"{label} changed while reading: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def reveal(root: Path, round_record: dict[str, Any], experiment: dict[str, Any]) -> dict[str, Any]:
    recover_anonymize_transaction(root, round_record, experiment)
    if round_record["state"] not in {"anonymized", "revealed"}:
        raise OperationError(f"round is not anonymized: {round_record['round_id']}")
    mapping_path = root / round_record["mapping_rel"]
    ensure_managed_components(root, mapping_path, "private mapping")
    if mapping_path.is_symlink() or not mapping_path.is_file():
        raise OperationError("private mapping is missing")
    if sha256_file(mapping_path) != round_record.get("mapping_sha256"):
        raise OperationError("private mapping changed after anonymization")
    mapping = validate_mapping(read_json(mapping_path), root, round_record)
    verify_mapping_integrity(root, round_record, mapping)

    reviewer_by_token: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for review_set in round_record["review_sets"]:
        for reviewer in review_set["reviewers"]:
            reviewer_by_token[reviewer["view_token"]] = (review_set, reviewer)
    committed_judgments: list[dict[str, Any]] = []
    judgment_paths: list[Path] = []
    for view_token in mapping["copy_hashes"]:
        review_set, reviewer = reviewer_by_token[view_token]
        view = root / reviewer["view_rel"]
        judgment = view / "judgment.md"
        try:
            judgment_bytes = read_regular_bytes(judgment, "judgment", root)
        except FileNotFoundError as exc:
            raise OperationError(f"judgment is missing: {judgment}") from exc
        try:
            judgment_text = judgment_bytes.decode("utf-8")
        except UnicodeError as exc:
            raise OperationError(f"judgment must be UTF-8 text: {judgment}") from exc
        if not judgment_text.strip():
            raise OperationError(f"judgment is empty: {judgment}")
        committed_judgments.append(
            {
                "review_set_id": review_set["id"],
                "reviewer_id": reviewer["id"],
                "view_dir": str(view),
                "sha256": hashlib.sha256(judgment_bytes).hexdigest(),
                "text": judgment_text,
            }
        )
        judgment_paths.append(judgment)

    committed_judgments.sort(
        key=lambda item: (item["review_set_id"], item["reviewer_id"])
    )
    judgment_snapshot = {
        "schema_version": SCHEMA_VERSION,
        "round_id": round_record["round_id"],
        "reviews": committed_judgments,
    }
    judgments_path = root / round_record["judgments_rel"]
    if os.path.lexists(judgments_path):
        ensure_managed_components(root, judgments_path, "committed judgment snapshot")
        if judgments_path.is_symlink() or not judgments_path.is_file():
            raise OperationError("committed judgment snapshot is not a regular file")
        recorded_digest = round_record.get("judgments_sha256")
        existing_digest = sha256_file(judgments_path)
        if recorded_digest is not None and recorded_digest != existing_digest:
            raise OperationError("committed judgment snapshot changed after reveal")
        existing_snapshot = read_json(judgments_path)
        if existing_snapshot != judgment_snapshot:
            raise OperationError("judgment changed after commitment")
    else:
        write_json_atomic(judgments_path, judgment_snapshot, replace=False)
    judgments_digest = sha256_file(judgments_path)
    recorded_digest = round_record.get("judgments_sha256")
    if recorded_digest is not None and recorded_digest != judgments_digest:
        raise OperationError("committed judgment snapshot changed after reveal")

    if round_record["state"] != "revealed":
        round_record["state"] = "revealed"
        round_record["judgments_sha256"] = judgments_digest
        save_experiment(root, experiment)
        for judgment in judgment_paths:
            os.chmod(judgment, 0o444)
    return {
        "schema_version": SCHEMA_VERSION,
        "round_id": round_record["round_id"],
        "state": "revealed",
        "review_count": len(mapping["reviews"]),
        "mapping_path": str(mapping_path),
        "mapping_sha256": round_record["mapping_sha256"],
        "judgments_path": str(judgments_path),
        "judgments_sha256": judgments_digest,
    }


def status(root: Path, experiment: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "root": str(root),
        "rounds": [
            {
                "round_id": item["round_id"],
                "state": item["state"],
                "run_count": len(item["runs"]),
                "review_set_count": len(item["review_sets"]),
                "reviewer_count": sum(
                    len(review_set["reviewers"])
                    for review_set in item["review_sets"]
                ),
            }
            for item in experiment["rounds"]
        ],
    }


def emit(value: Any) -> None:
    json.dump(value, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")


def main(argv: list[str]) -> int:
    if not argv or argv == ["--help"] or argv == ["-h"]:
        print(HELP, end="")
        return 0
    command = argv[0]
    try:
        if command == "init":
            if len(argv) != 2:
                raise UsageError("init requires ROOT")
            root = absolute_root(argv[1])
            emit(init_workspace(root))
            return 0
        if command == "add-round":
            if len(argv) != 3:
                raise UsageError("add-round requires ROOT and DESIGN.json")
            root = absolute_root(argv[1])
            with workspace_lock(root, exclusive=True):
                emit(add_round(root, Path(argv[2])))
            return 0
        if command in {"assignments", "anonymize", "reveal"}:
            if len(argv) != 3:
                raise UsageError(f"{command} requires ROOT and ROUND_ID")
            root = absolute_root(argv[1])
            with workspace_lock(root, exclusive=command != "assignments"):
                experiment = load_experiment(root)
                round_record = find_round(experiment, argv[2])
                if command == "assignments":
                    emit(assignment_view(root, round_record))
                elif command == "anonymize":
                    emit(anonymize(root, round_record, experiment))
                else:
                    emit(reveal(root, round_record, experiment))
            return 0
        if command == "status":
            if len(argv) != 2:
                raise UsageError("status requires ROOT")
            root = absolute_root(argv[1])
            with workspace_lock(root, exclusive=False):
                emit(status(root, load_experiment(root)))
            return 0
        raise UsageError(f"unknown command: {command}")
    except UsageError as exc:
        return fail(str(exc), 2)
    except OperationError as exc:
        return fail(str(exc), 1)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        return fail(f"operation failed: {exc}", 1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
