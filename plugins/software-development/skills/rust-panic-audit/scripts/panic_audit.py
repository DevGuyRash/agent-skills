#!/usr/bin/env python3
"""Read-only Cargo/Clippy orchestrator for direct Rust panic-surface audits."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_INCOMPLETE = 2
SCHEMA_VERSION = "1.0"

CORE_LINTS = (
    "clippy::unwrap_used",
    "clippy::expect_used",
    "clippy::panic",
    "clippy::todo",
    "clippy::unimplemented",
    "clippy::unreachable",
)

STRICT_LINTS = (
    "clippy::indexing_slicing",
    "clippy::arithmetic_side_effects",
    "clippy::panic_in_result_fn",
    "clippy::unwrap_in_result",
)

ALWAYS_SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "target",
    "test",
    "tests",
    "testdata",
    "fixture",
    "fixtures",
}

CARGO_DEFAULT_ONLY_SKIP_DIRS = {
    "bench",
    "benches",
    "example",
    "examples",
}

RESIDUAL_RISK = (
    "dependency behavior",
    "indexing or custom trait behavior outside selected coverage",
    "allocation failure",
    "omitted features, targets, or cfg branches",
    "build scripts and procedural macros",
    "panicking destructors and unwinding interactions",
    "lock poisoning",
    "FFI unwind behavior",
    "runtime configuration",
    "unexercised paths",
    "conventional test-only paths and definitely test-only items remain outside "
    "lexical candidates even with --all-targets; these lexical exclusions are "
    "distinct from compiler target coverage",
)

ANSI_SGR = re.compile(r"\x1b\[[0-9;]*m")


@dataclass(frozen=True)
class Finding:
    source: str
    kind: str
    path: str
    line: int
    column: int
    message: str
    level: str = "review"


@dataclass(frozen=True)
class Expectation:
    path: str
    line: int
    lints: tuple[str, ...]
    reason: str | None


@dataclass
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


class AuditError(RuntimeError):
    """Expected failure that leaves the requested audit incomplete."""


def normalize_lint(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def short_text(value: str, limit: int = 600) -> str:
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "…"


def run_command(args: Sequence[str], cwd: Path) -> CommandResult:
    try:
        proc = subprocess.run(
            list(args),
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise AuditError(f"cannot execute {args[0]}: {exc}") from exc
    return CommandResult(list(args), proc.returncode, proc.stdout, proc.stderr)


def file_digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cargo_executable() -> str:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise AuditError("Cargo is unavailable on PATH")
    return cargo


def locate_workspace(manifest_path: Path, cargo: str = "cargo") -> Path:
    result = run_command(
        [
            cargo,
            "locate-project",
            "--workspace",
            "--message-format",
            "plain",
            "--manifest-path",
            str(manifest_path),
        ],
        manifest_path.parent,
    )
    if result.returncode != 0:
        raise AuditError(f"Cargo could not locate the workspace: {short_text(result.stderr or result.stdout)}")
    root_manifest = Path(result.stdout.strip())
    if not root_manifest.is_absolute():
        root_manifest = (manifest_path.parent / root_manifest).resolve()
    return root_manifest.parent


def tracked_status(root: Path) -> str | None:
    if shutil.which("git") is None:
        return None
    top_level = run_command(["git", "rev-parse", "--show-toplevel"], root)
    if top_level.returncode != 0 or not top_level.stdout.strip():
        return None
    repository_root = Path(top_level.stdout.strip())
    if not repository_root.is_absolute():
        repository_root = (root / repository_root).resolve()
    status = run_command(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=no"],
        repository_root,
    )
    tracked = run_command(
        ["git", "ls-files", "--full-name", "-z"], repository_root
    )
    if status.returncode != 0 or tracked.returncode != 0:
        return None
    snapshot = hashlib.sha256()
    snapshot.update(status.stdout.encode("utf-8", errors="replace"))
    for relative in tracked.stdout.split("\0"):
        if not relative:
            continue
        snapshot.update(b"\0path\0")
        snapshot.update(relative.encode("utf-8", errors="replace"))
        path = repository_root / relative
        try:
            if path.is_symlink():
                snapshot.update(b"\0symlink\0")
                snapshot.update(os.readlink(path).encode("utf-8", errors="surrogateescape"))
            elif path.is_file():
                snapshot.update(b"\0file\0")
                digest = file_digest(path)
                snapshot.update((digest or "missing").encode("ascii"))
            else:
                snapshot.update(b"\0missing\0")
        except OSError as exc:
            snapshot.update(b"\0unreadable\0")
            snapshot.update(str(exc).encode("utf-8", errors="replace"))
    return snapshot.hexdigest()


def cargo_scope_args(args: argparse.Namespace, manifest_path: Path) -> list[str]:
    result = ["--manifest-path", str(manifest_path)]
    if args.package:
        for package in args.package:
            result.extend(["--package", package])
    elif args.workspace:
        result.append("--workspace")
    if args.all_targets:
        result.append("--all-targets")
    if args.all_features:
        result.append("--all-features")
    elif args.features:
        result.extend(["--features", args.features])
    return result


def metadata_args(
    args: argparse.Namespace,
    manifest_path: Path,
    locked: bool,
    cargo: str = "cargo",
) -> list[str]:
    result = [
        cargo,
        "metadata",
        "--format-version",
        "1",
        "--no-deps",
        "--manifest-path",
        str(manifest_path),
    ]
    if locked:
        result.append("--locked")
    if args.all_features:
        result.append("--all-features")
    elif args.features:
        result.extend(["--features", args.features])
    return result


def load_metadata(
    args: argparse.Namespace,
    manifest_path: Path,
    cwd: Path,
    locked: bool,
    cargo: str = "cargo",
) -> dict[str, Any]:
    result = run_command(metadata_args(args, manifest_path, locked, cargo), cwd)
    if result.returncode != 0:
        raise AuditError(f"Cargo metadata failed: {short_text(result.stderr or result.stdout)}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AuditError(f"Cargo metadata returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise AuditError("Cargo metadata did not return an object")
    return payload


def select_packages(metadata: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    packages = [item for item in metadata.get("packages", []) if isinstance(item, dict)]
    by_id = {str(item.get("id")): item for item in packages}
    workspace_ids = [str(item) for item in metadata.get("workspace_members", [])]
    workspace_packages = [by_id[item] for item in workspace_ids if item in by_id]

    if args.package:
        requested = set(args.package)
        selected = [item for item in workspace_packages if str(item.get("name")) in requested]
        found = {str(item.get("name")) for item in selected}
        missing = sorted(requested - found)
        if missing:
            raise AuditError(f"requested package(s) not found in workspace: {', '.join(missing)}")
        return selected

    if args.workspace:
        return workspace_packages

    default_ids = [str(item) for item in metadata.get("workspace_default_members", [])]
    selected = [by_id[item] for item in default_ids if item in by_id]
    if selected:
        return selected

    root_id = metadata.get("resolve", {}).get("root") if isinstance(metadata.get("resolve"), dict) else None
    if root_id is not None and str(root_id) in by_id:
        return [by_id[str(root_id)]]
    return workspace_packages


def discover_lints(
    args: argparse.Namespace,
    manifest_path: Path,
    cwd: Path,
    locked: bool,
    cargo: str = "cargo",
) -> tuple[set[str], str | None]:
    command = [cargo, "clippy", *cargo_scope_args(args, manifest_path)]
    if locked:
        command.append("--locked")
    command.extend(["--message-format=json", "--", "-W", "help"])
    result = run_command(command, cwd)
    available = {
        normalize_lint(match.group(0))
        for match in re.finditer(r"clippy::[a-z0-9][a-z0-9_-]*", result.stdout + result.stderr)
    }
    if result.returncode != 0 and not available:
        return set(), f"Cargo Clippy lint discovery failed: {short_text(result.stderr or result.stdout)}"
    if not available:
        return set(), "Cargo Clippy returned no discoverable Clippy lints"
    return available, None


def is_lifetime_start(source: str, index: int) -> bool:
    if index + 1 >= len(source):
        return False
    following = source[index + 1]
    if not (following.isalpha() or following == "_"):
        return False
    cursor = index + 2
    while cursor < len(source) and (source[cursor].isalnum() or source[cursor] == "_"):
        cursor += 1
    return not (cursor < len(source) and source[cursor] == "'")


def raw_string_open(source: str, index: int) -> tuple[int, int] | None:
    cursor = index
    if source.startswith(("br", "cr"), cursor):
        cursor += 2
    elif source.startswith("r", cursor):
        cursor += 1
    else:
        return None
    hashes = 0
    while cursor < len(source) and source[cursor] == "#":
        hashes += 1
        cursor += 1
    if cursor < len(source) and source[cursor] == '"':
        return cursor + 1, hashes
    return None


def mask_non_code(source: str) -> str:
    """Replace comments and string/character contents with spaces, preserving lines."""
    output = list(source)
    index = 0
    block_depth = 0
    line_comment = False
    string_quote = False
    char_quote = False
    raw_hashes: int | None = None

    def blank(position: int) -> None:
        if output[position] != "\n":
            output[position] = " "

    while index < len(source):
        char = source[index]
        following = source[index + 1] if index + 1 < len(source) else "\0"

        if line_comment:
            if char == "\n":
                line_comment = False
            else:
                blank(index)
            index += 1
            continue

        if block_depth:
            blank(index)
            if char == "/" and following == "*":
                blank(index + 1)
                block_depth += 1
                index += 2
            elif char == "*" and following == "/":
                blank(index + 1)
                block_depth -= 1
                index += 2
            else:
                index += 1
            continue

        if raw_hashes is not None:
            blank(index)
            if char == '"' and source.startswith("#" * raw_hashes, index + 1):
                for offset in range(1, raw_hashes + 1):
                    blank(index + offset)
                index += raw_hashes + 1
                raw_hashes = None
            else:
                index += 1
            continue

        if string_quote:
            blank(index)
            if char == "\\" and index + 1 < len(source):
                blank(index + 1)
                index += 2
            else:
                if char == '"':
                    string_quote = False
                index += 1
            continue

        if char_quote:
            blank(index)
            if char == "\\" and index + 1 < len(source):
                blank(index + 1)
                index += 2
            else:
                if char == "'":
                    char_quote = False
                index += 1
            continue

        if char == "/" and following == "/":
            blank(index)
            blank(index + 1)
            line_comment = True
            index += 2
            continue
        if char == "/" and following == "*":
            blank(index)
            blank(index + 1)
            block_depth = 1
            index += 2
            continue

        raw_open = raw_string_open(source, index)
        if raw_open is not None:
            content_start, raw_hashes = raw_open
            for cursor in range(index, content_start):
                blank(cursor)
            index = content_start
            continue

        if char == '"':
            blank(index)
            string_quote = True
            index += 1
            continue
        if char == "'" and not is_lifetime_start(source, index):
            blank(index)
            char_quote = True
            index += 1
            continue
        index += 1

    return "".join(output)


def brace_delta(line: str) -> int:
    return line.count("{") - line.count("}")


def split_cfg_terms(expression: str) -> list[str]:
    terms: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(expression):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return []
        elif char == "," and depth == 0:
            terms.append(expression[start:index].strip())
            start = index + 1
    if depth != 0:
        return []
    tail = expression[start:].strip()
    if tail:
        terms.append(tail)
    return terms


def cfg_call(expression: str) -> tuple[str, list[str]] | None:
    compact = expression.strip()
    opening = compact.find("(")
    if opening <= 0 or not compact.endswith(")"):
        return None
    name = compact[:opening].strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return None
    depth = 0
    closing = -1
    for index, char in enumerate(compact[opening:], start=opening):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                closing = index
                break
            if depth < 0:
                return None
    if closing != len(compact) - 1:
        return None
    inner = compact[opening + 1 : closing]
    return name, split_cfg_terms(inner)


def cfg_boolean_tree(expression: str, unknown_count: list[int]) -> tuple[str, Any]:
    compact = expression.strip()
    if compact == "test":
        return "constant", False
    call = cfg_call(compact)
    if call is not None:
        name, terms = call
        if name in {"all", "any"}:
            return name, tuple(cfg_boolean_tree(term, unknown_count) for term in terms)
        if name == "not" and len(terms) == 1:
            return name, cfg_boolean_tree(terms[0], unknown_count)
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", compact):
        return "atom", compact
    key_value = re.fullmatch(
        r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*("(?:\\.|[^"\\])*")',
        compact,
    )
    if key_value:
        return "atom", f"{key_value.group(1)}={key_value.group(2)}"
    if compact:
        return "atom", compact
    unknown_count[0] += 1
    return "atom", f"\0unknown-{unknown_count[0]}"


def cfg_boolean_atoms(tree: tuple[str, Any]) -> set[str]:
    kind, value = tree
    if kind == "atom":
        return {value}
    if kind in {"all", "any"}:
        return set().union(*(cfg_boolean_atoms(term) for term in value))
    if kind == "not":
        return cfg_boolean_atoms(value)
    return set()


def cfg_boolean_value(tree: tuple[str, Any], assignment: dict[str, bool]) -> bool:
    kind, value = tree
    if kind == "constant":
        return value
    if kind == "atom":
        return assignment[value]
    if kind == "all":
        return all(cfg_boolean_value(term, assignment) for term in value)
    if kind == "any":
        return any(cfg_boolean_value(term, assignment) for term in value)
    return not cfg_boolean_value(value, assignment)


def cfg_possibilities_without_test(expression: str) -> tuple[bool, bool]:
    """Return whether a cfg may be false/true when the `test` term is false."""
    tree = cfg_boolean_tree(expression, [0])
    atoms = sorted(cfg_boolean_atoms(tree))
    if len(atoms) > 12:
        return True, True

    may_be_false = False
    may_be_true = False
    for bitset in range(1 << len(atoms)):
        assignment = {
            atom: bool(bitset & (1 << index))
            for index, atom in enumerate(atoms)
        }
        if cfg_boolean_value(tree, assignment):
            may_be_true = True
        else:
            may_be_false = True
        if may_be_false and may_be_true:
            break
    return may_be_false, may_be_true


def rust_attributes(text: str) -> list[str]:
    attributes: list[str] = []
    search_start = 0
    while True:
        start = text.find("#[", search_start)
        if start < 0:
            return attributes
        depth = 1
        cursor = start + 2
        while cursor < len(text) and depth > 0:
            if text[cursor] == "[":
                depth += 1
            elif text[cursor] == "]":
                depth -= 1
            cursor += 1
        if depth > 0:
            return attributes
        attributes.append(text[start:cursor])
        search_start = cursor


def definitely_test_attribute(attribute: str) -> bool:
    for candidate in rust_attributes(attribute):
        compact = "".join(candidate.split())
        body = compact[2:-1]
        if re.fullmatch(r"(?:[A-Za-z_][\w]*::)*test(?:\(.*\))?", body):
            return True
        call = cfg_call(body)
        if call is None:
            continue
        name, terms = call
        if name != "cfg" or len(terms) != 1:
            continue
        _, may_be_true_without_test = cfg_possibilities_without_test(terms[0])
        if not may_be_true_without_test:
            return True
    return False


def test_line_mask(sanitized_lines: Sequence[str]) -> list[bool]:
    """Mask conventional and definitely attributed test-only items."""
    mask = [False] * len(sanitized_lines)
    pending = False
    in_item = False
    item_depth = 0
    attribute_start: int | None = None
    attribute_text: list[str] = []
    bracket_depth = 0

    for line_index, line in enumerate(sanitized_lines):
        stripped = line.strip()
        if in_item:
            mask[line_index] = True
            item_depth += brace_delta(line)
            if item_depth <= 0:
                in_item = False
                item_depth = 0
            continue

        if attribute_start is not None or "#[" in line:
            if attribute_start is None:
                attribute_start = line_index
                attribute_text = []
                bracket_depth = 0
            attribute_text.append(line)
            bracket_depth += line.count("[") - line.count("]")
            if bracket_depth > 0:
                continue
            combined = "\n".join(attribute_text)
            if definitely_test_attribute(combined):
                for marked in range(attribute_start, line_index + 1):
                    mask[marked] = True
                pending = True
            attribute_start = None
            attribute_text = []
            trailing = line.rsplit("]", 1)[-1].strip()
            if not trailing:
                continue
            stripped = trailing

        if pending:
            mask[line_index] = True
            delta = brace_delta(stripped)
            if delta > 0:
                in_item = True
                item_depth = delta
                pending = False
            elif ";" in stripped or ("{" in stripped and delta <= 0):
                pending = False
            continue

    return mask


def expectation_records(path: Path, source: str, sanitized: str) -> list[Expectation]:
    records: list[Expectation] = []
    pattern = re.compile(r"#\s*\[\s*expect\s*\((.*?)\)\s*\]", re.DOTALL)
    for match in pattern.finditer(sanitized):
        raw = source[match.start() : match.end()]
        lints = tuple(
            sorted(
                {
                    normalize_lint(item.group(0))
                    for item in re.finditer(r"(?:clippy::)?[a-z][a-z0-9_-]*", match.group(1))
                    if item.group(0) not in {"reason"}
                }
            )
        )
        reason_match = re.search(r'reason\s*=\s*"((?:\\.|[^"\\])*)"', raw, re.DOTALL)
        reason = reason_match.group(1) if reason_match else None
        line = source.count("\n", 0, match.start()) + 1
        records.append(Expectation(str(path), line, lints, reason))
    return records


METHOD_PATTERN = re.compile(
    r"\.\s*(?P<name>unwrap(?:_err|_unchecked)?|expect(?:_err)?)\s*\("
)
MACRO_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?P<name>panic|todo|unimplemented|unreachable)\s*!\s*[({\[]"
)
ASSERT_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?P<name>(?:debug_)?assert(?:_eq|_ne)?)\s*!\s*[({\[]"
)


def scan_source(path: Path, profile: str) -> tuple[list[Finding], list[Expectation]]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AuditError(f"cannot read Rust source {path}: {exc}") from exc
    sanitized = mask_non_code(source)
    raw_lines = source.splitlines()
    sanitized_lines = sanitized.splitlines()
    if len(sanitized_lines) < len(raw_lines):
        sanitized_lines.extend([""] * (len(raw_lines) - len(sanitized_lines)))
    masked = test_line_mask(sanitized_lines)
    findings: list[Finding] = []

    patterns: list[tuple[re.Pattern[str], str]] = [
        (METHOD_PATTERN, "direct-method"),
        (MACRO_PATTERN, "direct-macro"),
    ]
    if profile == "strict-boundary":
        patterns.append((ASSERT_PATTERN, "assertion-candidate"))

    searchable_lines = [" " * len(line) if masked[index] else line for index, line in enumerate(sanitized_lines)]
    searchable = "\n".join(searchable_lines)
    for pattern, kind in patterns:
        for match in pattern.finditer(searchable):
            name = match.group("name")
            line = searchable.count("\n", 0, match.start()) + 1
            previous_newline = searchable.rfind("\n", 0, match.start())
            column = match.start() - previous_newline
            raw_line = raw_lines[line - 1] if line <= len(raw_lines) else ""
            findings.append(
                Finding(
                    source="lexical",
                    kind=kind,
                    path=str(path),
                    line=line,
                    column=column,
                    message=f"{name} candidate: {short_text(raw_line.strip(), 240)}",
                )
            )
    return findings, expectation_records(path, source, sanitized)


def rust_files(
    packages: Sequence[dict[str, Any]],
    target_directory: Path | None,
    all_targets: bool = False,
) -> list[Path]:
    roots: set[Path] = set()
    for package in packages:
        manifest = package.get("manifest_path")
        if manifest:
            try:
                roots.add(Path(str(manifest)).resolve().parent)
            except OSError as exc:
                raise AuditError(
                    f"cannot resolve package manifest for lexical scan {manifest}: {exc}"
                ) from exc
    files: set[Path] = set()
    try:
        target_resolved = target_directory.resolve() if target_directory else None
    except OSError as exc:
        raise AuditError(
            f"cannot resolve Cargo target directory for lexical scan {target_directory}: {exc}"
        ) from exc
    skipped_dirs = set(ALWAYS_SKIP_DIRS)
    if not all_targets:
        skipped_dirs.update(CARGO_DEFAULT_ONLY_SKIP_DIRS)
    for root in roots:
        if not root.is_dir():
            raise AuditError(f"package root is unavailable for lexical scan: {root}")

        def walk_error(error: OSError) -> None:
            gap = error.filename or root
            raise AuditError(
                f"cannot enumerate Rust sources for lexical scan at {gap}: {error}"
            ) from error

        for directory, dirnames, filenames in os.walk(
            root, topdown=True, onerror=walk_error, followlinks=False
        ):
            directory_path = Path(directory)
            retained_dirs: list[str] = []
            for dirname in dirnames:
                if dirname in skipped_dirs:
                    continue
                candidate = directory_path / dirname
                try:
                    resolved_directory = candidate.resolve()
                except OSError as exc:
                    raise AuditError(
                        f"cannot resolve directory for lexical scan {candidate}: {exc}"
                    ) from exc
                if target_resolved is not None and (
                    resolved_directory == target_resolved
                    or target_resolved in resolved_directory.parents
                ):
                    continue
                retained_dirs.append(dirname)
            dirnames[:] = retained_dirs

            for filename in filenames:
                if not filename.endswith(".rs"):
                    continue
                path = directory_path / filename
                try:
                    resolved = path.resolve()
                except OSError as exc:
                    raise AuditError(
                        f"cannot resolve Rust source for lexical scan {path}: {exc}"
                    ) from exc
                if target_resolved is not None and (
                    resolved == target_resolved or target_resolved in resolved.parents
                ):
                    continue
                files.add(resolved)
    return sorted(files)


def parse_compiler_messages(output: str, active_lints: set[str]) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    non_policy_errors: list[str] = []
    for line in output.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("reason") != "compiler-message":
            continue
        message = payload.get("message")
        if not isinstance(message, dict):
            continue
        level = str(message.get("level", "warning"))
        code_data = message.get("code")
        code = str(code_data.get("code")) if isinstance(code_data, dict) and code_data.get("code") else ""
        normalized = normalize_lint(code)
        spans = message.get("spans") if isinstance(message.get("spans"), list) else []
        primary = next((span for span in spans if isinstance(span, dict) and span.get("is_primary")), None)
        if normalized in active_lints:
            findings.append(
                Finding(
                    source="compiler",
                    kind=normalized,
                    path=str(primary.get("file_name", "")) if primary else "",
                    line=int(primary.get("line_start", 0)) if primary else 0,
                    column=int(primary.get("column_start", 0)) if primary else 0,
                    message=short_text(str(message.get("message", code)), 400),
                    level=level,
                )
            )
        elif level == "error":
            non_policy_errors.append(short_text(str(message.get("message", code or "compiler error")), 400))
    return findings, non_policy_errors


def cargo_build_success(output: str) -> bool | None:
    build_success: bool | None = None
    for line in output.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("reason") == "build-finished" and isinstance(payload.get("success"), bool):
            build_success = payload["success"]
    return build_success


def cargo_stdout_is_json(output: str) -> bool:
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            return False
        if not isinstance(payload, dict):
            return False
    return True


def clippy_stderr_is_cargo_progress(output: str) -> bool:
    progress = re.compile(
        r"\s*(?:"
        r"Blocking waiting for file lock on .+|"
        r"(?:Compiling|Checking|Fresh|Running|Dirty|Documenting|Finished|Updating|"
        r"Downloading|Downloaded|Locking|Adding|Removing|Downgrading) .+|"
        r"warning: build failed, waiting for other jobs to finish\.\.\.|"
        r"error: could not compile .+ due to \d+ previous errors?"
        r"(?:; \d+ warnings? emitted)?"
        r")\s*"
    )
    normalized = ANSI_SGR.sub("", output)
    return all(
        not line.strip() or progress.fullmatch(line)
        for line in normalized.splitlines()
    )


def nonzero_clippy_is_policy_only(
    result: CommandResult,
    findings: Sequence[Finding],
    non_policy_errors: Sequence[str],
) -> bool:
    if result.returncode == 0 or not findings or non_policy_errors:
        return False
    if not any(finding.level == "error" for finding in findings):
        return False
    if not cargo_stdout_is_json(result.stdout):
        return False
    if cargo_build_success(result.stdout) is not False:
        return False
    return clippy_stderr_is_cargo_progress(result.stderr)


def run_clippy(
    args: argparse.Namespace,
    manifest_path: Path,
    cwd: Path,
    locked: bool,
    active_lints: Sequence[str],
    cargo: str = "cargo",
) -> tuple[CommandResult, list[Finding], list[str]]:
    command = [cargo, "clippy", *cargo_scope_args(args, manifest_path)]
    if locked:
        command.append("--locked")
    command.append("--message-format=json")
    command.append("--")
    for lint in active_lints:
        command.extend(["-D", lint])
    result = run_command(command, cwd)
    findings, non_policy_errors = parse_compiler_messages(result.stdout, set(active_lints))
    return result, findings, non_policy_errors


def package_summary(packages: Sequence[dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    names: list[str] = []
    targets: list[dict[str, Any]] = []
    for package in packages:
        package_name = str(package.get("name", "unknown"))
        names.append(package_name)
        for target in package.get("targets", []):
            if not isinstance(target, dict):
                continue
            targets.append(
                {
                    "package": package_name,
                    "name": str(target.get("name", "")),
                    "kind": list(target.get("kind", [])),
                    "src_path": str(target.get("src_path", "")),
                }
            )
    return sorted(names), targets


def analyzed_target_summary(
    output: str, packages: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    package_ids = {
        str(package.get("id")): str(package.get("name", "unknown"))
        for package in packages
        if package.get("id") is not None
    }
    targets: dict[tuple[str, str, tuple[str, ...], str], dict[str, Any]] = {}
    for line in output.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("reason") not in {"compiler-artifact", "compiler-message"}:
            continue
        package_id = str(payload.get("package_id", ""))
        package_name = package_ids.get(package_id)
        target = payload.get("target")
        if package_name is None or not isinstance(target, dict):
            continue
        kinds = tuple(str(item) for item in target.get("kind", []) if isinstance(item, str))
        name = str(target.get("name", ""))
        src_path = str(target.get("src_path", ""))
        key = package_name, name, kinds, src_path
        targets[key] = {
            "package": package_name,
            "name": name,
            "kind": list(kinds),
            "src_path": src_path,
        }
    return [targets[key] for key in sorted(targets)]


def target_identity(target: dict[str, Any]) -> tuple[str, str, tuple[str, ...], str]:
    return (
        str(target.get("package", "")),
        str(target.get("name", "")),
        tuple(sorted(str(item) for item in target.get("kind", []))),
        str(target.get("src_path", "")),
    )


def requested_target_summary(
    declared_targets: Sequence[dict[str, Any]], all_targets: bool
) -> list[dict[str, Any]]:
    requested: list[dict[str, Any]] = []
    for target in declared_targets:
        kinds = {str(item) for item in target.get("kind", [])}
        if "custom-build" in kinds:
            continue
        if not all_targets and kinds.intersection({"test", "bench", "example"}):
            continue
        requested.append(target)
    return requested


def missing_requested_targets(
    declared_targets: Sequence[dict[str, Any]],
    analyzed_targets: Sequence[dict[str, Any]],
    all_targets: bool,
) -> list[dict[str, Any]]:
    analyzed = {target_identity(target) for target in analyzed_targets}
    return [
        target
        for target in requested_target_summary(declared_targets, all_targets)
        if target_identity(target) not in analyzed
    ]


def target_scope_label(target: dict[str, Any]) -> str:
    kinds = ", ".join(str(item) for item in target.get("kind", [])) or "unknown"
    return (
        f"{target.get('package', 'unknown')}::"
        f"{target.get('name', 'unknown')} [{kinds}]"
    )


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "Rust panic audit",
        f"status: {report['status']}",
        f"profile: {report['profile']}",
        f"manifest: {report['scope']['manifest_path']}",
        f"packages: {', '.join(report['scope']['packages']) or '(none)'}",
        f"target mode: {report['scope']['target_mode']}",
        f"features: {report['scope']['features']}",
    ]
    for label, targets in (
        ("declared targets", report["scope"]["declared_targets"]),
        ("analyzed targets", report["scope"]["analyzed_targets"]),
    ):
        lines.append(f"{label}:")
        if targets:
            lines.extend(
                f"- {target['package']}::{target['name']} "
                f"[{', '.join(target['kind']) or 'unknown'}] {target['src_path']}"
                for target in targets
            )
        else:
            lines.append("- (none)")
    lines.extend(["", f"compiler findings: {len(report['compiler_findings'])}"])
    for finding in report["compiler_findings"]:
        lines.append(
            f"- {finding['kind']} {finding['path']}:{finding['line']}:{finding['column']}: {finding['message']}"
        )
    lines.append(f"lexical candidates: {len(report['lexical_candidates'])}")
    for finding in report["lexical_candidates"]:
        lines.append(
            f"- {finding['kind']} {finding['path']}:{finding['line']}:{finding['column']}: {finding['message']}"
        )
    lines.append(f"intentional expectations: {len(report['intentional_expectations'])}")
    for expectation in report["intentional_expectations"]:
        reason = expectation["reason"] or "reason not captured"
        lines.append(
            f"- {expectation['path']}:{expectation['line']}: {', '.join(expectation['lints']) or '(unparsed)'} — {reason}"
        )
    lines.append(
        "unavailable lints: " + (", ".join(report["unavailable_lints"]) or "none")
    )
    if report["tooling_errors"]:
        lines.append("tooling errors:")
        lines.extend(f"- {item}" for item in report["tooling_errors"])
    lines.append("residual risk:")
    lines.extend(f"- {item}" for item in report["residual_risk"])
    if report["status"] == "clean":
        lines.extend(["", "Conclusion: no forbidden direct constructs found in the audited scope."])
    elif report["status"] == "incomplete":
        lines.extend(["", "Conclusion: audit incomplete; no panic-free claim is supported."])
    else:
        lines.extend(["", "Conclusion: direct violations or review candidates require disposition."])
    return "\n".join(lines) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit direct Rust panic surfaces without modifying tracked repository files."
    )
    parser.add_argument("--manifest-path", required=True, type=Path)
    parser.add_argument("--profile", required=True, choices=("core", "strict-boundary"))
    parser.add_argument("--workspace", action="store_true")
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--all-targets", action="store_true")
    feature_group = parser.add_mutually_exclusive_group()
    feature_group.add_argument("--all-features", action="store_true")
    feature_group.add_argument("--features")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parsed = parser.parse_args(argv)
    if parsed.features is not None and not any(item.strip() for item in parsed.features.split(",")):
        parser.error("--features requires at least one non-empty feature name")
    return parsed


def audit(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    manifest_path = args.manifest_path.expanduser().resolve()
    base_report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "incomplete",
        "profile": args.profile,
        "scope": {
            "manifest_path": str(manifest_path),
            "workspace": bool(args.workspace),
            "packages": [],
            "declared_targets": [],
            "analyzed_targets": [],
            "target_mode": "all-targets" if args.all_targets else "cargo-defaults",
            "all_targets": bool(args.all_targets),
            "features": "all" if args.all_features else (args.features or "Cargo defaults"),
        },
        "compiler_findings": [],
        "lexical_candidates": [],
        "intentional_expectations": [],
        "unavailable_lints": [],
        "tooling_errors": [],
        "residual_risk": list(RESIDUAL_RISK),
    }

    if not manifest_path.is_file():
        base_report["tooling_errors"].append(f"manifest does not exist: {manifest_path}")
        return base_report, EXIT_INCOMPLETE

    manifest_directory = manifest_path.parent
    try:
        cargo = cargo_executable()
        root = locate_workspace(manifest_path, cargo)
    except AuditError as exc:
        base_report["tooling_errors"].append(str(exc))
        return base_report, EXIT_INCOMPLETE

    lockfile = root / "Cargo.lock"
    initial_lock_digest = file_digest(lockfile)
    locked = initial_lock_digest is not None
    initial_status = tracked_status(root)

    try:
        metadata = load_metadata(args, manifest_path, manifest_directory, locked, cargo)
        packages = select_packages(metadata, args)
        package_names, targets = package_summary(packages)
        base_report["scope"]["packages"] = package_names
        base_report["scope"]["declared_targets"] = targets

        target_path = metadata.get("target_directory")
        target_directory = Path(str(target_path)) if target_path else None
        lexical: list[Finding] = []
        expectations: list[Expectation] = []
        for path in rust_files(packages, target_directory, args.all_targets):
            file_findings, file_expectations = scan_source(path, args.profile)
            lexical.extend(file_findings)
            expectations.extend(file_expectations)
        base_report["lexical_candidates"] = [asdict(item) for item in lexical]
        base_report["intentional_expectations"] = [asdict(item) for item in expectations]

        requested = list(CORE_LINTS)
        if args.profile == "strict-boundary":
            requested.extend(STRICT_LINTS)
        available, discovery_error = discover_lints(
            args, manifest_path, manifest_directory, locked, cargo
        )
        if discovery_error:
            base_report["unavailable_lints"] = requested
            base_report["tooling_errors"].append(discovery_error)
            return base_report, EXIT_INCOMPLETE
        active = [lint for lint in requested if normalize_lint(lint) in available]
        base_report["unavailable_lints"] = [lint for lint in requested if lint not in active]

        clippy_result, compiler_findings, non_policy_errors = run_clippy(
            args, manifest_path, manifest_directory, locked, active, cargo
        )
        base_report["compiler_findings"] = [asdict(item) for item in compiler_findings]
        analyzed_targets = analyzed_target_summary(
            clippy_result.stdout, packages
        )
        base_report["scope"]["analyzed_targets"] = analyzed_targets
        if non_policy_errors:
            base_report["tooling_errors"].extend(non_policy_errors)
        missing_targets = missing_requested_targets(
            targets, analyzed_targets, args.all_targets
        )
        policy_only = nonzero_clippy_is_policy_only(
            clippy_result, compiler_findings, non_policy_errors
        )
        if missing_targets:
            missing_names = ", ".join(
                target_scope_label(target) for target in missing_targets
            )
            if policy_only:
                base_report["tooling_errors"].append(
                    "Cargo Clippy stopped after policy findings before analyzing "
                    f"the full requested target scope: {missing_names}"
                )
            else:
                base_report["tooling_errors"].append(
                    "Cargo Clippy did not report analysis of the full requested "
                    f"target scope: {missing_names}"
                )
        if clippy_result.returncode != 0:
            if not policy_only:
                detail = short_text(clippy_result.stderr) or "non-policy or incomplete build failure"
                base_report["tooling_errors"].append(f"Cargo Clippy failed: {detail}")
                base_report["tooling_errors"].append(
                    "Cargo Clippy did not complete the requested audit scope"
                )

        final_status = tracked_status(root)
        if initial_status is not None and final_status is not None and final_status != initial_status:
            base_report["tooling_errors"].append(
                "tracked working-tree state changed while Cargo/Clippy ran; audit integrity is incomplete"
            )

        if base_report["tooling_errors"] or base_report["unavailable_lints"]:
            return base_report, EXIT_INCOMPLETE
        if compiler_findings or lexical:
            base_report["status"] = "findings"
            return base_report, EXIT_FINDINGS
        base_report["status"] = "clean"
        return base_report, EXIT_CLEAN
    except AuditError as exc:
        base_report["tooling_errors"].append(str(exc))
        return base_report, EXIT_INCOMPLETE
    finally:
        if initial_lock_digest is None and lockfile.is_file():
            try:
                lockfile.unlink()
            except OSError as exc:
                base_report["tooling_errors"].append(f"could not remove Cargo.lock created by Cargo: {exc}")
        elif initial_lock_digest is not None and file_digest(lockfile) != initial_lock_digest:
            base_report["tooling_errors"].append("Cargo.lock changed despite the locked audit")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report, exit_code = audit(args)
    if report["tooling_errors"]:
        report["status"] = "incomplete"
        exit_code = EXIT_INCOMPLETE
    report["exit_code"] = exit_code
    if args.json_output:
        print(json.dumps(report, indent=2, sort_keys=False))
    else:
        sys.stdout.write(render_text(report))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
