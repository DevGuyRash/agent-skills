#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "packaging" / "skills.toml"
TOOLCHAIN_PATH = REPO_ROOT / "rust-toolchain.toml"
ROOT_WATCH_PATHS = [
    Path("packaging/skills.toml"),
    Path("scripts/package_skills.py"),
    Path("Cargo.toml"),
    Path("Cargo.lock"),
    Path("rust-toolchain.toml"),
]


def load_config() -> dict[str, dict[str, object]]:
    with open(CONFIG_PATH, "rb") as fh:
        data = tomllib.load(fh)
    return data["skills"]


def load_vendor_copies() -> list[dict[str, object]]:
    with open(CONFIG_PATH, "rb") as fh:
        data = tomllib.load(fh)
    vendor = data.get("vendor", {})
    copies = vendor.get("copies", [])
    if not isinstance(copies, list):
        raise SystemExit("packaging config error: vendor.copies must be an array of tables")
    return copies


def vendor_copies(check_only: bool) -> None:
    """Materialize (or verify) committed copies of shared skill scripts.

    Skills are self-contained distribution units on every harness, so shared
    scripts are vendored as real files rather than referenced across skill
    directories. Source of truth is vendor.copies[].source; drift between a
    source and its targets fails the check."""
    copies = load_vendor_copies()
    if not copies:
        print("no vendor copies configured")
        return
    drift: list[str] = []
    for entry in copies:
        source = REPO_ROOT / str(entry["source"])
        if not source.is_file():
            raise SystemExit(f"vendor source missing: {source}")
        src_bytes = source.read_bytes()
        targets = entry.get("targets", [])
        if not isinstance(targets, list) or not targets:
            raise SystemExit(f"vendor entry for {entry['source']} has no targets")
        for raw_target in targets:
            target = REPO_ROOT / str(raw_target)
            if check_only:
                if not target.is_file() or target.read_bytes() != src_bytes:
                    drift.append(f"{raw_target} (from {entry['source']})")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(src_bytes)
                shutil.copymode(source, target)
                print(f"vendored {entry['source']} -> {raw_target}")
    if check_only:
        if drift:
            listing = "\n  ".join(drift)
            raise SystemExit(
                "vendored copies out of sync (run: python3 scripts/package_skills.py vendor --sync):\n  "
                + listing
            )
        print(f"vendor check ok ({len(copies)} sources)")


def load_toml(path: Path) -> dict[str, object]:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def host_platform_id() -> str:
    sys_name = sys.platform
    machine = platform.machine().lower()

    if not sys_name.startswith("linux"):  # pragma: no cover - explicit failure path
        raise SystemExit(f"unsupported host platform: {sys_name}; only Linux packaging is supported")

    aliases = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "arm64": "aarch64",
        "aarch64": "aarch64",
    }
    try:
        arch = aliases[machine]
    except KeyError as exc:  # pragma: no cover - explicit failure path
        raise SystemExit(f"unsupported host architecture: {machine}") from exc

    return f"linux-{arch}"


def target_config(skill: dict[str, object], platform_id: str) -> dict[str, object]:
    raw_targets = skill.get("targets")
    if raw_targets is None:
        return {}
    if not isinstance(raw_targets, dict):
        raise SystemExit("targets must be a table of per-platform settings")
    target = raw_targets.get(platform_id)
    if target is None:
        return {}
    if not isinstance(target, dict):
        raise SystemExit(f"target config for {platform_id} must be a table")
    return target


def binary_name(skill: dict[str, object], platform_id: str) -> str:
    target = target_config(skill, platform_id)
    artifact = target.get("artifact")
    if artifact is None:
        return str(skill["binary"])
    if not isinstance(artifact, str) or not artifact.strip():
        raise SystemExit(f"artifact for {platform_id} must be a non-empty string")
    return artifact


def toolchain_channel() -> str:
    with open(TOOLCHAIN_PATH, "rb") as fh:
        data = tomllib.load(fh)
    toolchain = data.get("toolchain")
    if not isinstance(toolchain, dict) or not isinstance(toolchain.get("channel"), str):
        raise SystemExit("rust-toolchain.toml must define [toolchain].channel")
    return toolchain["channel"]


def remap_prefixes() -> list[tuple[Path, str]]:
    prefixes: list[tuple[Path, str]] = [(REPO_ROOT, "/workspace")]

    cargo_home = Path(os.environ.get("CARGO_HOME", str(Path.home() / ".cargo"))).resolve()
    rustup_home = Path(os.environ.get("RUSTUP_HOME", str(Path.home() / ".rustup"))).resolve()

    prefixes.append((cargo_home, "/cargo-home"))
    prefixes.append((rustup_home, "/rustup-home"))
    return prefixes


def build_env() -> dict[str, str]:
    return build_env_for_root(REPO_ROOT)


def build_env_for_root(repo_root: Path, cargo_target: str | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["RUSTFLAGS"] = release_rustflags_for_target(repo_root, cargo_target)
    env.pop("CARGO_ENCODED_RUSTFLAGS", None)
    env["PATH"] = strip_dev_cache_intercepts(env.get("PATH", ""))
    env["CARGO_INCREMENTAL"] = "0"
    env["SOURCE_DATE_EPOCH"] = "1"
    env["TZ"] = "UTC"
    env["LC_ALL"] = "C"
    return env


def release_rustflags_for_target(repo_root: Path, cargo_target: str | None) -> str:
    return release_rustflags(
        repo_root=str(repo_root),
        cargo_home=str(remap_prefixes()[1][0]),
        rustup_home=str(remap_prefixes()[2][0]),
        cargo_target=cargo_target,
    )


def release_rustflags(
    *,
    repo_root: str,
    cargo_home: str,
    rustup_home: str,
    cargo_target: str | None,
) -> str:
    remap_flags = [
        f"--remap-path-prefix={source}={dest}"
        for source, dest in [
            (repo_root, "/workspace"),
            (cargo_home, "/cargo-home"),
            (rustup_home, "/rustup-home"),
        ]
    ]
    flags = [
        *remap_flags,
        "-Cstrip=symbols",
        "-Cdebuginfo=0",
        "-Ccodegen-units=1",
    ]
    if cargo_target and cargo_target.endswith("-windows-msvc"):
        flags.extend(
            [
                "-Clink-arg=/Brepro",
                "-Clink-arg=/DEBUG:NONE",
                "-Clink-arg=/timestamp:1",
            ]
        )
    return " ".join(flags)


def strip_dev_cache_intercepts(path_value: str) -> str:
    entries = [entry for entry in path_value.split(os.pathsep) if entry]
    filtered = [entry for entry in entries if "/dev-cache/intercepts" not in entry]
    return os.pathsep.join(filtered)


def run(cmd: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd or REPO_ROOT, check=True, env=env)


def docker_available() -> bool:
    """Whether Docker can actually run a container, not merely whether it is installed.

    An installed binary is not a working daemon. A kernel update that has not been
    rebooted into leaves the running kernel without its modules directory, so Docker
    starts and answers but cannot create a container's veth pair. Probing `docker info`
    catches that and every other broken-daemon case; checking PATH does not, and turns
    a recoverable condition into a hard failure halfway through a build.
    """
    if shutil.which("docker") is None:
        return False
    try:
        probe = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return probe.returncode == 0


def env_value(name: str, *, deprecated: str | None = None, default: str = "") -> str:
    value = os.environ.get(name)
    if value:
        return value
    if deprecated:
        legacy = os.environ.get(deprecated)
        if legacy:
            return legacy
    return default


def dist_build_mode() -> str:
    mode = env_value(
        "AGENT_TOOLING_DIST_BUILD_MODE",
        deprecated="AGENT_SKILLS_DIST_BUILD_MODE",
        default="auto",
    ).strip().lower()
    if mode not in {"auto", "container", "host"}:
        raise SystemExit(
            "AGENT_TOOLING_DIST_BUILD_MODE must be one of: auto, container, host"
        )
    return mode


def use_container_build(platform_id: str) -> bool:
    if platform_id != "linux-x86_64":
        return False

    mode = dist_build_mode()
    if mode == "host":
        return False
    if mode == "container":
        if not docker_available():
            raise SystemExit(
                "AGENT_TOOLING_DIST_BUILD_MODE=container, but docker cannot run a container.\n"
                "Run `docker info` to see why. An installed docker with a kernel that has been\n"
                "updated but not rebooted into is the common case: the daemon answers but has\n"
                "no veth module to build a container network with."
            )
        return True
    return docker_available()


def container_image() -> str:
    return env_value(
        "AGENT_TOOLING_RUST_IMAGE",
        deprecated="AGENT_SKILLS_RUST_IMAGE",
        default=f"rust:{toolchain_channel()}",
    )


def container_rustflags() -> str:
    remap_flags = [
        "--remap-path-prefix=/work=/workspace",
        "--remap-path-prefix=/usr/local/cargo=/cargo-home",
        "--remap-path-prefix=/usr/local/rustup=/rustup-home",
    ]
    rustflags = os.environ.get("RUSTFLAGS", "").strip()
    return " ".join([*remap_flags, rustflags]).strip()


def install_dist_binary(skill: dict[str, object], platform_id: str, src: Path) -> None:
    skill_dir = REPO_ROOT / str(skill["skill_dir"])
    dist_dir = skill_dir / "dist" / platform_id
    dist_dir.mkdir(parents=True, exist_ok=True)
    target_name = binary_name(skill, platform_id)
    dst = dist_dir / target_name
    shutil.copy2(src, dst)
    mode = os.stat(dst).st_mode
    os.chmod(dst, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def stage_host_native(selected: list[tuple[str, dict[str, object]]], platform_id: str) -> None:
    packages = []
    for _, skill in selected:
        packages.extend(["-p", str(skill["package"])])
    run(["cargo", "build", "--workspace", "--release", "--locked", *packages], env=build_env())

    for _, skill in selected:
        target_name = binary_name(skill, platform_id)
        src = REPO_ROOT / "target" / "release" / target_name
        install_dist_binary(skill, platform_id, src)


def stage_host_container(selected: list[tuple[str, dict[str, object]]], platform_id: str) -> None:
    packages = []
    for _, skill in selected:
        packages.extend(["-p", str(skill["package"])])

    create = subprocess.run(
        [
            "docker",
            "create",
            "-v",
            f"{REPO_ROOT}:/work:ro",
            "-w",
            "/work",
            "-e",
            "CARGO_TARGET_DIR=/tmp/target",
            "-e",
            f"RUSTFLAGS={container_rustflags()}",
            container_image(),
            "cargo",
            "build",
            "--workspace",
            "--release",
            "--locked",
            *packages,
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    container_id = create.stdout.strip()
    if not container_id:
        raise SystemExit("docker create did not return a container id")

    extract_dir = Path(tempfile.mkdtemp(prefix="package-skills-container-"))
    try:
        subprocess.run(["docker", "start", "-a", container_id], cwd=REPO_ROOT, check=True)
        for _, skill in selected:
            target_name = binary_name(skill, platform_id)
            extracted = extract_dir / target_name
            subprocess.run(
                ["docker", "cp", f"{container_id}:/tmp/target/release/{target_name}", str(extracted)],
                cwd=REPO_ROOT,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            install_dist_binary(skill, platform_id, extracted)
    finally:
        subprocess.run(
            ["docker", "rm", "-f", container_id],
            cwd=REPO_ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        shutil.rmtree(extract_dir, ignore_errors=True)


def selected_skill_entries(
    config: dict[str, dict[str, object]],
    skill_names: list[str] | None = None,
) -> list[tuple[str, dict[str, object]]]:
    if not skill_names:
        return list(config.items())

    selected: list[tuple[str, dict[str, object]]] = []
    seen: set[str] = set()
    unknown: list[str] = []
    for skill_name in skill_names:
        if skill_name in seen:
            continue
        seen.add(skill_name)
        skill = config.get(skill_name)
        if skill is None:
            unknown.append(skill_name)
            continue
        selected.append((skill_name, skill))
    if unknown:
        choices = ", ".join(sorted(config))
        missing = ", ".join(sorted(unknown))
        raise SystemExit(f"unknown packaged skill(s): {missing}; expected one of: {choices}")
    return selected


def dependency_tables(manifest: dict[str, object]) -> list[dict[str, object]]:
    tables: list[dict[str, object]] = []
    for key in ("dependencies", "dev-dependencies", "build-dependencies"):
        raw = manifest.get(key)
        if isinstance(raw, dict):
            tables.append(raw)

    for table_name, table_value in manifest.items():
        if not isinstance(table_name, str) or not table_name.startswith("target."):
            continue
        if not isinstance(table_value, dict):
            continue
        for key in ("dependencies", "dev-dependencies", "build-dependencies"):
            raw = table_value.get(key)
            if isinstance(raw, dict):
                tables.append(raw)
    return tables


def discover_workspace_manifests() -> list[Path]:
    manifests: list[Path] = []
    for path in sorted(REPO_ROOT.rglob("Cargo.toml")):
        rel_parts = path.relative_to(REPO_ROOT).parts
        if "target" in rel_parts or ".git" in rel_parts:
            continue
        if any(part.startswith(".local") for part in rel_parts):
            continue
        manifests.append(path)
    return manifests


def manifest_dependency_dirs(manifest_path: Path, manifest: dict[str, object]) -> list[Path]:
    deps: list[Path] = []
    for table in dependency_tables(manifest):
        for spec in table.values():
            if not isinstance(spec, dict):
                continue
            raw_path = spec.get("path")
            if not isinstance(raw_path, str) or not raw_path.strip():
                continue
            dep_path = (manifest_path.parent / raw_path).resolve()
            dep_manifest = dep_path / "Cargo.toml" if dep_path.is_dir() else dep_path
            if dep_manifest.name != "Cargo.toml":
                dep_manifest = dep_manifest / "Cargo.toml"
            if dep_manifest.is_file():
                deps.append(dep_manifest.parent.resolve())
    return deps


def cargo_package_graph() -> tuple[dict[str, Path], dict[Path, list[Path]]]:
    package_dirs: dict[str, Path] = {}
    dependency_dirs: dict[Path, list[Path]] = {}

    for manifest_path in discover_workspace_manifests():
        manifest = load_toml(manifest_path)
        crate_dir = manifest_path.parent.resolve()
        dependency_dirs[crate_dir] = manifest_dependency_dirs(manifest_path, manifest)
        package = manifest.get("package")
        if not isinstance(package, dict):
            continue
        name = package.get("name")
        if isinstance(name, str) and name.strip():
            package_dirs[name] = crate_dir

    return package_dirs, dependency_dirs


def path_within_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
        return True
    except ValueError:
        return False


def package_source_dirs(
    config: dict[str, dict[str, object]],
    skill_names: list[str] | None = None,
) -> list[Path]:
    selected = selected_skill_entries(config, skill_names)
    package_dirs, dependency_dirs = cargo_package_graph()

    queue: list[Path] = []
    missing_packages: list[str] = []
    for _, skill in selected:
        package_name = str(skill["package"])
        crate_dir = package_dirs.get(package_name)
        if crate_dir is None:
            missing_packages.append(package_name)
            continue
        queue.append(crate_dir)

    if missing_packages:
        missing = ", ".join(sorted(missing_packages))
        raise SystemExit(f"packaged skill crate(s) not found in workspace: {missing}")

    ordered: list[Path] = []
    seen: set[Path] = set()
    while queue:
        crate_dir = queue.pop(0)
        if crate_dir in seen or not path_within_repo(crate_dir):
            continue
        seen.add(crate_dir)
        ordered.append(crate_dir)
        for dep_dir in dependency_dirs.get(crate_dir, []):
            if dep_dir not in seen:
                queue.append(dep_dir)

    return ordered


def normalize_repo_path(path: str) -> str:
    trimmed = path.strip().replace("\\", "/")
    while trimmed.startswith("./"):
        trimmed = trimmed[2:]
    return trimmed.strip("/")


def watched_repo_paths(
    config: dict[str, dict[str, object]],
    skill_names: list[str] | None = None,
    *,
    include_tests: bool = False,
) -> list[str]:
    selected = selected_skill_entries(config, skill_names)
    watched: list[str] = [path.as_posix() for path in ROOT_WATCH_PATHS]

    for crate_dir in package_source_dirs(config, skill_names):
        watched.append(crate_dir.relative_to(REPO_ROOT).as_posix())

    for _, skill in selected:
        skill_dir = REPO_ROOT / str(skill["skill_dir"])
        launcher = skill_dir / str(skill["launcher"])
        watched.append(launcher.relative_to(REPO_ROOT).as_posix())
        watched.append((skill_dir / "dist").relative_to(REPO_ROOT).as_posix())
        if include_tests:
            watched.append((skill_dir / "tests").relative_to(REPO_ROOT).as_posix())

    deduped: list[str] = []
    seen: set[str] = set()
    for path in watched:
        normalized = normalize_repo_path(path)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def path_matches_watch_list(changed_path: str, watched_paths: list[str]) -> bool:
    normalized = normalize_repo_path(changed_path)
    if not normalized:
        return False
    for watched in watched_paths:
        if normalized == watched or normalized.startswith(f"{watched}/"):
            return True
    return False


def matches_changed_files(
    changed_files: list[str],
    config: dict[str, dict[str, object]],
    skill_names: list[str] | None = None,
    *,
    include_tests: bool = False,
) -> bool:
    watched = watched_repo_paths(config, skill_names, include_tests=include_tests)
    for changed in changed_files:
        if path_matches_watch_list(changed, watched):
            return True
    return False


def load_changed_files(path: Path) -> list[str]:
    return [
        normalize_repo_path(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if normalize_repo_path(line)
    ]


def skill_platforms(skill: dict[str, object], key: str) -> list[str]:
    raw = skill.get(key)
    if raw is None:
        return []
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise SystemExit(f"{key} must be a list of platform ids")
    return list(raw)


def selected_platforms(config: dict[str, dict[str, object]], platform_set: str) -> list[str]:
    if platform_set == "host":
        return [host_platform_id()]

    ordered: list[str] = []
    seen: set[str] = set()
    manifest_keys = {
        "required": ("required_platforms",),
        "ci": ("ci_platforms", "required_platforms"),
        "all": ("ci_platforms", "required_platforms"),
    }
    keys = manifest_keys[platform_set]
    for skill in config.values():
        for key in keys:
            for platform_id in skill_platforms(skill, key):
                if platform_id in seen:
                    continue
                seen.add(platform_id)
                ordered.append(platform_id)
    if ordered:
        return ordered
    return [host_platform_id()]


def skill_declares_platform(skill: dict[str, object], platform_id: str) -> bool:
    return any(platform_id in skill_platforms(skill, key) for key in ("required_platforms", "ci_platforms"))


def selected_skill_targets(
    config: dict[str, dict[str, object]],
    platform_set: str,
    skill_names: list[str] | None = None,
) -> list[tuple[str, dict[str, object], str]]:
    selected = selected_skill_entries(config, skill_names)
    if platform_set == "host":
        platform_id = host_platform_id()
        return [
            (skill_name, skill, platform_id)
            for skill_name, skill in selected
            if skill_declares_platform(skill, platform_id)
        ]

    manifest_keys = {
        "required": ("required_platforms",),
        "ci": ("ci_platforms", "required_platforms"),
        "all": ("ci_platforms", "required_platforms"),
    }
    keys = manifest_keys[platform_set]
    targets: list[tuple[str, dict[str, object], str]] = []
    for skill_name, skill in selected:
        seen: set[str] = set()
        for key in keys:
            for platform_id in skill_platforms(skill, key):
                if platform_id in seen:
                    continue
                seen.add(platform_id)
                targets.append((skill_name, skill, platform_id))
    return targets


def dist_path_for_skill(skill: dict[str, object], platform_id: str) -> Path:
    skill_dir = REPO_ROOT / str(skill["skill_dir"])
    return skill_dir / "dist" / platform_id / binary_name(skill, platform_id)


def tracked_dist_paths(
    config: dict[str, dict[str, object]],
    platform_spec: str | list[str],
    skill_names: list[str] | None = None,
) -> list[Path]:
    paths: list[Path] = []
    if isinstance(platform_spec, str):
        for _, skill, platform_id in selected_skill_targets(config, platform_spec, skill_names):
            paths.append(dist_path_for_skill(skill, platform_id))
        return paths
    for skill_name, skill in selected_skill_entries(config, skill_names):
        for platform_id in platform_spec:
            if skill_declares_platform(skill, platform_id):
                paths.append(dist_path_for_skill(skill, platform_id))
    return paths


def repo_dist_payload_roots(
    config: dict[str, dict[str, object]] | None = None,
    skill_names: list[str] | None = None,
) -> list[Path]:
    roots: set[Path] = set()
    if config is None:
        config = load_config()
    for _, skill in selected_skill_entries(config, skill_names):
        roots.add(REPO_ROOT / str(skill["skill_dir"]) / "dist")
    if skill_names is None:
        for path in REPO_ROOT.glob("plugins/*/skills/*/dist"):
            roots.add(path)
        for path in REPO_ROOT.glob("skills/*/dist"):
            roots.add(path)
    return sorted(roots)


def repo_dist_payload_paths(
    config: dict[str, dict[str, object]] | None = None,
    skill_names: list[str] | None = None,
) -> list[Path]:
    paths: list[Path] = []
    for dist_root in repo_dist_payload_roots(config, skill_names):
        if not dist_root.exists():
            continue
        for path in sorted(dist_root.glob("**/*")):
            if path.is_file() or path.is_symlink():
                paths.append(path)
    return paths


def stale_dist_paths(
    expected_paths: list[Path],
    config: dict[str, dict[str, object]] | None = None,
    skill_names: list[str] | None = None,
) -> list[Path]:
    expected = {path.resolve() for path in expected_paths}
    stale: list[Path] = []
    for path in repo_dist_payload_paths(config, skill_names):
        if path.resolve() in expected:
            continue
        stale.append(path)
    return stale


def bootstrap() -> None:
    run(["cargo", "fetch", "--locked"])


def stage_host(skill_names: list[str] | None = None) -> None:
    config = load_config()
    selected = selected_skill_entries(config, skill_names)
    platform_id = host_platform_id()
    if use_container_build(platform_id):
        stage_host_container(selected, platform_id)
        return

    # A host build against the local toolchain and linker will not reproduce the
    # committed bytes, so say so rather than let non-reproducible payloads look
    # like a normal result. Only worth saying where a container was the default.
    if platform_id == "linux-x86_64" and dist_build_mode() == "auto":
        print(
            "warning: docker is unavailable; building on the host instead.\n"
            "         Host-built binaries will not match the committed payloads, which are\n"
            "         built against a pinned toolchain. Do not commit the result.",
            file=sys.stderr,
        )
    stage_host_native(selected, platform_id)


def verify_host() -> None:
    vendor_copies(check_only=True)
    config = load_config()
    platform_id = host_platform_id()
    stage_host()
    relevant = [str(path.relative_to(REPO_ROOT)) for path in tracked_dist_paths(config, [platform_id])]
    result = subprocess.run(
        ["git", "status", "--short", "--", *relevant],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        print(result.stdout, end="")
        raise SystemExit("packaged binaries changed; refresh and commit the staged dist outputs")


def ensure_tracked(paths: list[Path]) -> None:
    missing = []
    untracked = []
    for path in paths:
        if not path.exists() or path.is_symlink():
            missing.append(path)
            continue
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            untracked.append(path)
    if missing:
        for path in missing:
            print(f"missing dist payload: {path.relative_to(REPO_ROOT)}")
        raise SystemExit("required packaged dist outputs are missing")
    if untracked:
        for path in untracked:
            print(f"untracked dist payload: {path.relative_to(REPO_ROOT)}")
        raise SystemExit("required packaged dist outputs must be committed to git")


def verify_complete(platform_set: str, skill_names: list[str] | None = None) -> None:
    config = load_config()
    ensure_tracked(tracked_dist_paths(config, platform_set, skill_names))


def artifact_source_path(artifacts_root: Path, rel_path: Path) -> Path | None:
    direct = artifacts_root / rel_path
    if direct.is_file():
        return direct
    if not artifacts_root.exists():
        return None
    for child in sorted(artifacts_root.iterdir()):
        candidate = child / rel_path
        if candidate.is_file():
            return candidate
    return None


def compare_artifacts(
    artifacts_root: Path,
    platform_set: str,
    skill_names: list[str] | None = None,
) -> None:
    config = load_config()
    expected_paths = tracked_dist_paths(config, platform_set, skill_names)
    mismatches = False
    for target in expected_paths:
        rel_path = target.relative_to(REPO_ROOT)
        source = artifact_source_path(artifacts_root, rel_path)
        if source is None:
            print(f"missing artifact payload: {rel_path}")
            mismatches = True
            continue
        if not target.exists():
            print(f"repository is missing payload: {rel_path}")
            mismatches = True
            continue
        if not filecmp.cmp(source, target, shallow=False):
            print(f"artifact payload differs: {rel_path}")
            mismatches = True
    for stale_path in stale_dist_paths(expected_paths, config, skill_names):
        print(f"stale dist payload: {stale_path.relative_to(REPO_ROOT)}")
        mismatches = True
    if mismatches:
        raise SystemExit("artifact payloads do not match the committed dist tree")


def sync_artifacts(
    artifacts_root: Path,
    platform_set: str,
    skill_names: list[str] | None = None,
) -> None:
    config = load_config()
    expected_paths = tracked_dist_paths(config, platform_set, skill_names)
    source_map: dict[Path, Path] = {}
    for target in expected_paths:
        rel_path = target.relative_to(REPO_ROOT)
        source = artifact_source_path(artifacts_root, rel_path)
        if source is None:
            raise SystemExit(f"missing artifact payload: {rel_path}")
        source_map[target] = source

    roots = repo_dist_payload_roots(config, skill_names)
    staged_roots: list[tuple[Path, Path]] = []
    changed: list[Path] = []
    try:
        for dist_root in roots:
            desired_paths: dict[Path, Path] = {}
            for target, source in source_map.items():
                try:
                    rel_under_root = target.relative_to(dist_root)
                except ValueError:
                    continue
                desired_paths[rel_under_root] = source

            if not desired_paths and not dist_root.exists():
                continue

            staged_root = Path(tempfile.mkdtemp(prefix=f"{dist_root.name}-sync-", dir=dist_root.parent))
            staged_roots.append((dist_root, staged_root))
            for rel_under_root, source in desired_paths.items():
                destination = staged_root / rel_under_root
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                mode = os.stat(destination).st_mode
                os.chmod(destination, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            current_files = {}
            if dist_root.exists():
                current_files = {
                    path.relative_to(dist_root): path
                    for path in dist_root.glob("**/*")
                    if path.is_file() or path.is_symlink()
                }
            desired_files = set(desired_paths)
            for rel_under_root in sorted(set(current_files) ^ desired_files):
                changed.append((dist_root / rel_under_root).relative_to(REPO_ROOT))
            for rel_under_root, source in desired_paths.items():
                current = current_files.get(rel_under_root)
                if current is None or not filecmp.cmp(source, current, shallow=False):
                    rel_path = (dist_root / rel_under_root).relative_to(REPO_ROOT)
                    if rel_path not in changed:
                        changed.append(rel_path)

        if not changed:
            return

        backups: list[Path] = []
        for dist_root, staged_root in staged_roots:
            backup_root = dist_root.with_name(f"{dist_root.name}.bak-package-skills")
            if backup_root.exists():
                shutil.rmtree(backup_root)
            if dist_root.exists():
                dist_root.rename(backup_root)
                backups.append(backup_root)
            staged_root.rename(dist_root)
        for backup_root in backups:
            shutil.rmtree(backup_root, ignore_errors=True)
    finally:
        for _, staged_root in staged_roots:
            if staged_root.exists():
                shutil.rmtree(staged_root, ignore_errors=True)
    for rel_path in changed:
        print(rel_path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def head_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def git_index_tree() -> str:
    result = subprocess.run(
        ["git", "write-tree", "--missing-ok"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tree = result.stdout.strip()
    if not tree:
        raise SystemExit("git write-tree did not return an index tree")
    return tree


def export_frozen_index_tree(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "checkout-index", "--all", f"--prefix={destination}/"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def cargo_target_triple(skill: dict[str, object], platform_id: str) -> str | None:
    raw = target_config(skill, platform_id).get("cargo_target")
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw.strip():
        raise SystemExit(f"cargo_target for {platform_id} must be a non-empty string")
    return raw


def target_recipe(skill: dict[str, object], platform_id: str) -> str:
    raw = target_config(skill, platform_id).get("recipe", "cargo-release")
    if not isinstance(raw, str) or not raw.strip():
        raise SystemExit(f"recipe for {platform_id} must be a non-empty string")
    return raw


def target_recipe_version(skill: dict[str, object], platform_id: str) -> str:
    raw = target_config(skill, platform_id).get("recipe_version")
    if not isinstance(raw, str) or not raw.strip():
        raise SystemExit(f"recipe_version for {platform_id} must be a non-empty string")
    return raw


def cargo_release_dir(frozen_root: Path, cargo_target: str | None) -> Path:
    if cargo_target:
        return frozen_root / "target" / cargo_target / "release"
    return frozen_root / "target" / "release"


def build_command(skill: dict[str, object], platform_id: str) -> list[str]:
    recipe = target_recipe(skill, platform_id)
    cargo_target = cargo_target_triple(skill, platform_id)
    if cargo_target is None:
        raise SystemExit(f"cargo_target is required for reproducible release target {platform_id}")
    common = [
        "--release",
        "--frozen",
        "-p",
        str(skill["package"]),
        "--target",
        cargo_target,
    ]
    if recipe == "cargo-zigbuild":
        return ["cargo", "zigbuild", *common]
    if recipe == "cargo-xwin":
        return ["cargo", "xwin", "build", *common]
    raise SystemExit(f"unsupported build recipe for {platform_id}: {recipe}")


def command_version(command: list[str], label: str) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"{label} is unavailable; install the pinned release tool") from error
    return (result.stdout or result.stderr).strip()


def verify_release_tool(skill: dict[str, object], platform_id: str) -> None:
    target = target_config(skill, platform_id)
    recipe = target_recipe(skill, platform_id)
    version = target_recipe_version(skill, platform_id)
    if recipe == "cargo-zigbuild":
        actual = command_version(["cargo-zigbuild", "--version"], "cargo-zigbuild")
        if version not in actual:
            raise SystemExit(f"cargo-zigbuild version mismatch; expected {version}, got {actual}")
        zig_version = target.get("zig_version")
        if not isinstance(zig_version, str) or not zig_version:
            raise SystemExit(f"zig_version is required for {platform_id}")
        actual_zig = command_version(["zig", "version"], "Zig")
        if actual_zig != zig_version:
            raise SystemExit(f"Zig version mismatch; expected {zig_version}, got {actual_zig}")
    elif recipe == "cargo-xwin":
        actual = command_version(["cargo-xwin", "--version"], "cargo-xwin")
        if version not in actual:
            raise SystemExit(f"cargo-xwin version mismatch; expected {version}, got {actual}")
        llvm_version = target.get("llvm_version")
        if not isinstance(llvm_version, str) or not llvm_version:
            raise SystemExit(f"llvm_version is required for {platform_id}")
        actual_llvm = command_version(["clang", "--version"], "LLVM/Clang")
        if llvm_version not in actual_llvm.splitlines()[0]:
            raise SystemExit(
                f"LLVM/Clang version mismatch; expected {llvm_version}, got {actual_llvm.splitlines()[0]}"
            )
        if shutil.which("lld-link") is None:
            raise SystemExit("lld-link is unavailable; install the pinned LLVM toolchain")
    else:
        raise SystemExit(f"unsupported build recipe for {platform_id}: {recipe}")


def stage_from_frozen_index(
    selected_targets: list[tuple[str, dict[str, object], str]],
    frozen_root: Path,
    artifacts_root: Path,
) -> None:
    for _, skill, platform_id in selected_targets:
        verify_release_tool(skill, platform_id)
        cargo_target = cargo_target_triple(skill, platform_id)
        run(
            build_command(skill, platform_id),
            cwd=frozen_root,
            env=build_env_for_root(frozen_root, cargo_target),
        )
        source = cargo_release_dir(frozen_root, cargo_target) / binary_name(skill, platform_id)
        if not source.is_file():
            raise SystemExit(f"build did not produce {source}")
        destination = artifacts_root / str(skill["skill_dir"]) / "dist" / platform_id / binary_name(skill, platform_id)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        mode = os.stat(destination).st_mode
        os.chmod(destination, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def dev_cache_artifact_put(path: Path) -> str:
    result = subprocess.run(
        ["dev-cache", "artifacts", "put", "--json", str(path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    cas_digest = payload.get("digest")
    if not isinstance(cas_digest, str) or not cas_digest.strip():
        raise SystemExit("dev-cache artifacts put --json did not return digest")
    return cas_digest


def dev_cache_temp_root() -> Path:
    try:
        result = subprocess.run(
            ["dev-cache", "path", "temp", "--repo", str(REPO_ROOT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        raise SystemExit("dev-cache temp routing is unavailable for the release build") from error
    raw_path = payload.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise SystemExit("dev-cache path temp --json did not return a path")
    path = Path(raw_path)
    if not path.is_absolute():
        raise SystemExit("dev-cache returned a non-absolute temp path")
    path.mkdir(parents=True, exist_ok=True)
    return path


def dist_source_paths(skill: dict[str, object]) -> list[Path]:
    raw = skill.get("dist_sources")
    if not isinstance(raw, list) or not raw:
        raise SystemExit("release-enabled skills must define a non-empty dist_sources list")
    paths: list[Path] = []
    for value in raw:
        if not isinstance(value, str) or not value:
            raise SystemExit("dist_sources entries must be non-empty strings")
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise SystemExit(f"dist_sources path must stay inside the repository: {value}")
        paths.append(path)
    return sorted(set(paths))


def selected_source_entries(skill: dict[str, object], source_root: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for configured in dist_source_paths(skill):
        path = source_root / configured
        if not path.exists() and not path.is_symlink():
            raise SystemExit(f"release source is missing: {configured.as_posix()}")
        candidates = [path]
        if path.is_dir():
            candidates = [item for item in sorted(path.rglob("*")) if item.is_file() or item.is_symlink()]
        for candidate in candidates:
            relative = candidate.relative_to(source_root).as_posix()
            metadata = os.lstat(candidate)
            executable = bool(metadata.st_mode & 0o111)
            if candidate.is_symlink():
                entries.append(
                    {
                        "path": relative,
                        "kind": "symlink",
                        "target": os.readlink(candidate),
                    }
                )
            elif candidate.is_file():
                entries.append(
                    {
                        "path": relative,
                        "kind": "file",
                        "sha256": sha256_file(candidate),
                        "executable": executable,
                    }
                )
    entries.sort(key=lambda item: str(item["path"]))
    return entries


def json_digest(value: object) -> str:
    material = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return f"sha256:{hashlib.sha256(material).hexdigest()}"


def source_receipt(skill: dict[str, object], source_root: Path) -> dict[str, object]:
    return {
        "digest": json_digest(selected_source_entries(skill, source_root)),
        "cargo_lock_digest": sha256_file(source_root / "Cargo.lock"),
        "rust_toolchain_digest": sha256_file(source_root / "rust-toolchain.toml"),
        "packaging_config_digest": sha256_file(source_root / "packaging/skills.toml"),
    }


def build_recipe_digest(skill: dict[str, object], platforms: list[str]) -> str:
    material = {
        "commands": {platform_id: build_command(skill, platform_id) for platform_id in sorted(platforms)},
        "targets": {platform_id: target_config(skill, platform_id) for platform_id in sorted(platforms)},
        "rustflags": {
            platform_id: release_rustflags(
                repo_root="<frozen-root>",
                cargo_home="<cargo-home>",
                rustup_home="<rustup-home>",
                cargo_target=cargo_target_triple(skill, platform_id),
            )
            for platform_id in sorted(platforms)
        },
        "environment": {
            "CARGO_INCREMENTAL": "0",
            "SOURCE_DATE_EPOCH": "1",
            "TZ": "UTC",
            "LC_ALL": "C",
        },
    }
    return json_digest(material)


def dist_receipt_path(skill: dict[str, object], root: Path | None = None) -> Path:
    resolved_root = REPO_ROOT if root is None else root
    return resolved_root / str(skill["skill_dir"]) / "dist" / "receipt.json"


def build_receipt(
    skill_name: str,
    skill: dict[str, object],
    platforms: list[str],
    source_root: Path,
    artifacts_root: Path,
) -> dict[str, object]:
    artifacts: list[dict[str, object]] = []
    for platform_id in sorted(platforms):
        artifact_path = (
            artifacts_root
            / str(skill["skill_dir"])
            / "dist"
            / platform_id
            / binary_name(skill, platform_id)
        )
        artifacts.append(
            {
                "platform": platform_id,
                "artifact": binary_name(skill, platform_id),
                "cargo_target": cargo_target_triple(skill, platform_id),
                "recipe": target_recipe(skill, platform_id),
                "recipe_version": target_recipe_version(skill, platform_id),
                "output_digest": sha256_file(artifact_path),
                "dev_cache_cas_digest": dev_cache_artifact_put(artifact_path),
            }
        )
    return {
        "schema": "agent-tooling-skill-dist-receipt.v2",
        "skill": skill_name,
        "source": source_receipt(skill, source_root),
        "toolchain": {"channel": toolchain_channel_from(source_root)},
        "build_recipe_digest": build_recipe_digest(skill, platforms),
        "artifacts": artifacts,
    }


def toolchain_channel_from(root: Path) -> str:
    with open(root / "rust-toolchain.toml", "rb") as fh:
        data = tomllib.load(fh)
    toolchain = data.get("toolchain")
    if not isinstance(toolchain, dict) or not isinstance(toolchain.get("channel"), str):
        raise SystemExit("rust-toolchain.toml must define [toolchain].channel")
    return toolchain["channel"]


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    material = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        handle.write(material)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def compare_built_artifacts(
    first: Path,
    second: Path,
    selected_targets: list[tuple[str, dict[str, object], str]],
) -> None:
    for _, skill, platform_id in selected_targets:
        relative = Path(str(skill["skill_dir"])) / "dist" / platform_id / binary_name(skill, platform_id)
        first_path = first / relative
        second_path = second / relative
        if not first_path.is_file() or not second_path.is_file():
            raise SystemExit(f"reproducibility build is missing {relative}")
        if not filecmp.cmp(first_path, second_path, shallow=False):
            raise SystemExit(f"non-reproducible release artifact: {relative}")


def export_source(destination: Path, source: str) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if source == "index":
        export_frozen_index_tree(destination)
        return
    if not source.startswith("commit:") or len(source) <= len("commit:"):
        raise SystemExit("source must be index or commit:<git-object>")
    revision = source.split(":", 1)[1]
    archive = destination.parent / "source.tar"
    subprocess.run(
        ["git", "archive", "--format=tar", "-o", str(archive), revision],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    with tarfile.open(archive, "r") as bundle:
        for member in bundle.getmembers():
            member_path = Path(member.name)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise SystemExit("git archive contains an escaping path")
        bundle.extractall(destination, filter="data")


def selected_targets_by_skill(
    targets: list[tuple[str, dict[str, object], str]],
) -> dict[str, tuple[dict[str, object], list[str]]]:
    grouped: dict[str, tuple[dict[str, object], list[str]]] = {}
    for skill_name, skill, platform_id in targets:
        if skill_name not in grouped:
            grouped[skill_name] = (skill, [])
        grouped[skill_name][1].append(platform_id)
    return grouped


def dist_refresh(
    source: str,
    platform_set: str,
    *,
    skill_names: list[str] | None = None,
    git_stage: bool = False,
) -> list[str]:
    if source != "index":
        raise SystemExit("dist-refresh currently supports only --source=index")
    config = load_config()
    selected_targets = selected_skill_targets(config, platform_set, skill_names)
    with tempfile.TemporaryDirectory(
        prefix="package-skills-dist-refresh-",
        dir=dev_cache_temp_root(),
    ) as temp_dir:
        temp_root = Path(temp_dir)
        first_source = temp_root / "source-a"
        second_source = temp_root / "source-b"
        first_artifacts = temp_root / "artifacts-a"
        second_artifacts = temp_root / "artifacts-b"
        export_source(first_source, "index")
        export_source(second_source, "index")
        first_artifacts.mkdir(parents=True, exist_ok=True)
        second_artifacts.mkdir(parents=True, exist_ok=True)
        stage_from_frozen_index(selected_targets, first_source, first_artifacts)
        stage_from_frozen_index(selected_targets, second_source, second_artifacts)
        compare_built_artifacts(first_artifacts, second_artifacts, selected_targets)
        sync_artifacts(first_artifacts, platform_set, skill_names)
        receipts = {
            skill_name: build_receipt(skill_name, skill, platforms, first_source, REPO_ROOT)
            for skill_name, (skill, platforms) in selected_targets_by_skill(selected_targets).items()
        }
        for skill_name, payload in receipts.items():
            write_json_atomic(dist_receipt_path(config[skill_name]), payload)
    changed_paths: list[str] = []
    release_paths = tracked_dist_paths(config, platform_set, skill_names)
    release_paths.extend(
        dist_receipt_path(skill)
        for _, (skill, _) in selected_targets_by_skill(selected_targets).items()
    )
    for path in release_paths:
        result = subprocess.run(
            ["git", "status", "--short", "--", str(path.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            changed_paths.append(str(path.relative_to(REPO_ROOT)))
    if git_stage and changed_paths:
        subprocess.run(
            ["git", "add", "--", *changed_paths],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    return changed_paths


def verify_dist_receipt(
    platform_set: str,
    *,
    source: str = "index",
    skill_names: list[str] | None = None,
) -> None:
    with tempfile.TemporaryDirectory(prefix="package-skills-verify-dist-") as temp_dir:
        frozen_root = Path(temp_dir) / "source"
        export_source(frozen_root, source)
        config_path = frozen_root / "packaging/skills.toml"
        with open(config_path, "rb") as handle:
            config = tomllib.load(handle)["skills"]
        selected_targets = selected_skill_targets(config, platform_set, skill_names)
        for skill_name, (skill, platforms) in selected_targets_by_skill(selected_targets).items():
            receipt_path = dist_receipt_path(skill, frozen_root)
            try:
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                raise SystemExit(f"missing or invalid committed dist receipt: {receipt_path}") from error
            if receipt.get("schema") != "agent-tooling-skill-dist-receipt.v2":
                raise SystemExit(f"unsupported dist receipt schema for {skill_name}")
            if receipt.get("skill") != skill_name:
                raise SystemExit(f"dist receipt skill mismatch for {skill_name}")
            if receipt.get("source") != source_receipt(skill, frozen_root):
                raise SystemExit(f"dist receipt source digest mismatch for {skill_name}")
            expected_toolchain = {"channel": toolchain_channel_from(frozen_root)}
            if receipt.get("toolchain") != expected_toolchain:
                raise SystemExit(f"dist receipt toolchain mismatch for {skill_name}")
            if receipt.get("build_recipe_digest") != build_recipe_digest(skill, platforms):
                raise SystemExit(f"dist receipt build recipe mismatch for {skill_name}")
            artifacts = receipt.get("artifacts")
            if not isinstance(artifacts, list):
                raise SystemExit(f"dist receipt artifacts are invalid for {skill_name}")
            expected_platforms = sorted(platforms)
            actual_platforms = sorted(
                item.get("platform") for item in artifacts if isinstance(item, dict)
            )
            if actual_platforms != expected_platforms:
                raise SystemExit(f"dist receipt target matrix mismatch for {skill_name}")
            for item in artifacts:
                if not isinstance(item, dict):
                    raise SystemExit(f"dist receipt artifact is invalid for {skill_name}")
                platform_id = item.get("platform")
                if not isinstance(platform_id, str):
                    raise SystemExit(f"dist receipt artifact platform is invalid for {skill_name}")
                artifact = frozen_root / str(skill["skill_dir"]) / "dist" / platform_id / binary_name(skill, platform_id)
                if not artifact.is_file() or item.get("output_digest") != sha256_file(artifact):
                    raise SystemExit(f"dist receipt artifact digest mismatch: {artifact.relative_to(frozen_root)}")
                expected_fields = {
                    "artifact": binary_name(skill, platform_id),
                    "cargo_target": cargo_target_triple(skill, platform_id),
                    "recipe": target_recipe(skill, platform_id),
                    "recipe_version": target_recipe_version(skill, platform_id),
                }
                if any(item.get(key) != value for key, value in expected_fields.items()):
                    raise SystemExit(f"dist receipt artifact metadata mismatch for {platform_id}")
                cache_digest = item.get("dev_cache_cas_digest")
                if not isinstance(cache_digest, str) or not cache_digest.strip():
                    raise SystemExit(f"dist receipt dev-cache CAS digest is missing for {platform_id}")


def verify_target_matrix(platform_set: str) -> None:
    config = load_config()
    targets = selected_skill_targets(config, platform_set)
    tracked = {path.relative_to(REPO_ROOT).as_posix() for path in tracked_dist_paths(config, platform_set)}
    if len(tracked) != len(tracked_dist_paths(config, platform_set)):
        raise SystemExit("duplicate tracked dist paths in target matrix")
    for _, skill, platform_id in targets:
        if not binary_name(skill, platform_id):
            raise SystemExit(f"missing artifact name for {platform_id}")
        if "dist_sources" not in skill:
            continue
        target_recipe_version(skill, platform_id)
        target = target_config(skill, platform_id)
        recipe = target_recipe(skill, platform_id)
        if recipe == "cargo-zigbuild" and not isinstance(target.get("zig_version"), str):
            raise SystemExit(f"zig_version is required for {platform_id}")
        if recipe == "cargo-xwin" and not isinstance(target.get("llvm_version"), str):
            raise SystemExit(f"llvm_version is required for {platform_id}")


def smoke_launchers() -> None:
    config = load_config()
    for skill in config.values():
        launcher = REPO_ROOT / str(skill["skill_dir"]) / str(skill["launcher"])
        smoke_args = [str(arg) for arg in skill.get("smoke_args", [])]
        run([str(launcher), *smoke_args])


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("bootstrap")
    refresh = sub.add_parser("dist-refresh")
    refresh.add_argument("--source", choices=["index"], default="index")
    refresh.add_argument("--platform-set", choices=["host", "required", "ci", "all"], default="required")
    refresh.add_argument("--skill", action="append", default=[])
    refresh.add_argument("--stage", action="store_true")
    receipt = sub.add_parser("verify-dist-receipt")
    receipt.add_argument("--platform-set", choices=["host", "required", "ci", "all"], default="required")
    receipt.add_argument("--source", default="index")
    receipt.add_argument("--skill", action="append", default=[])
    matrix = sub.add_parser("verify-target-matrix")
    matrix.add_argument("--platform-set", choices=["host", "required", "ci", "all"], default="required")
    stage = sub.add_parser("stage-host")
    stage.add_argument("--skill", action="append", default=[])
    sub.add_parser("verify-host")
    complete = sub.add_parser("verify-complete")
    complete.add_argument("--platform-set", choices=["host", "required", "ci", "all"], default="required")
    compare = sub.add_parser("compare-artifacts")
    compare.add_argument("--artifacts-root", required=True)
    compare.add_argument("--platform-set", choices=["host", "required", "ci", "all"], default="ci")
    sync = sub.add_parser("sync-artifacts")
    sync.add_argument("--artifacts-root", required=True)
    sync.add_argument("--platform-set", choices=["host", "required", "ci", "all"], default="ci")
    sub.add_parser("smoke-launchers")
    sub.add_parser("launcher-smoke")
    vendor = sub.add_parser("vendor")
    vendor.add_argument("--sync", action="store_true")
    watch = sub.add_parser("watch-paths")
    watch.add_argument("--skill", action="append", default=[])
    watch.add_argument("--include-tests", action="store_true")
    match = sub.add_parser("matches-changed-files")
    match.add_argument("--skill", action="append", default=[])
    match.add_argument("--include-tests", action="store_true")
    match.add_argument("--changed-files-file", required=True)
    args = parser.parse_args()

    if args.cmd == "bootstrap":
        bootstrap()
    elif args.cmd == "dist-refresh":
        dist_refresh(args.source, args.platform_set, skill_names=args.skill, git_stage=args.stage)
    elif args.cmd == "verify-dist-receipt":
        verify_dist_receipt(
            args.platform_set,
            source=args.source,
            skill_names=args.skill,
        )
    elif args.cmd == "verify-target-matrix":
        verify_target_matrix(args.platform_set)
    elif args.cmd == "stage-host":
        stage_host(args.skill)
    elif args.cmd == "verify-host":
        verify_host()
    elif args.cmd == "verify-complete":
        verify_complete(args.platform_set)
    elif args.cmd == "compare-artifacts":
        compare_artifacts(Path(args.artifacts_root), args.platform_set)
    elif args.cmd == "sync-artifacts":
        sync_artifacts(Path(args.artifacts_root), args.platform_set)
    elif args.cmd in {"smoke-launchers", "launcher-smoke"}:
        smoke_launchers()
    elif args.cmd == "vendor":
        vendor_copies(check_only=not args.sync)
    elif args.cmd == "watch-paths":
        for path in watched_repo_paths(load_config(), args.skill, include_tests=args.include_tests):
            print(path)
    elif args.cmd == "matches-changed-files":
        changed_files = load_changed_files(Path(args.changed_files_file))
        changed = matches_changed_files(
            changed_files,
            load_config(),
            args.skill,
            include_tests=args.include_tests,
        )
        print("true" if changed else "false")
    else:  # pragma: no cover
        raise SystemExit(f"unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
