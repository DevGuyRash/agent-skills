#!/usr/bin/env python3
"""--from-json ingest for report-friction.sh.

Reads one JSON payload (stdin or file), coerces deprecated shapes, validates
the current-write contract, redacts every user-supplied string with the same
rule list the shell sanitizer uses, and emits the parsed fields as
"name<TAB>base64(value)" lines. The shell consumes those with a read loop and
base64_decode - no shell evaluation of payload-derived text anywhere.

argv: <path|-> <scratch_dir> <temp_root> [pattern replacement]...
The trailing pairs are friction_redaction_rules() from _common.sh, written in
sed -E dialect; the POSIX character classes they use are translated to
Python re equivalents below so one rule list serves both engines.

Exit codes match the public contract: 2 for empty stdin, malformed JSON, or
an invalid payload (nothing filed); 0 with field lines on success.
"""

import base64
import json
import re
import sys
import tempfile

path = sys.argv[1]
scratch_dir = sys.argv[2]
temp_root = sys.argv[3]

rule_args = sys.argv[4:]
REDACTION_RULES = []
for i in range(0, len(rule_args) - 1, 2):
    pattern = (
        rule_args[i]
        .replace("[:alnum:]", "A-Za-z0-9")
        .replace("[:space:]", " \\t\\r\\n\\f\\v")
    )
    try:
        REDACTION_RULES.append((re.compile(pattern, re.M), rule_args[i + 1]))
    except re.error:
        continue


def redact(value):
    for compiled, replacement in REDACTION_RULES:
        value = compiled.sub(replacement, value)
    return value


if path == "-":
    raw = sys.stdin.read()
else:
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()

if raw.strip() == "":
    print("error: stdin was empty - NO event was filed.", file=sys.stderr)
    print("Common causes: a heredoc terminator mismatch, or a previous command", file=sys.stderr)
    print("consumed stdin. Re-run with:", file=sys.stderr)
    print("  printf '%s' '<json>' | sh .../report-friction.sh --from-json -", file=sys.stderr)
    print("or pass a file path: --from-json <path>", file=sys.stderr)
    sys.exit(2)


def hint_for(err_msg: str) -> str:
    msg = err_msg.lower()
    if "expecting property name enclosed in double quotes" in msg:
        return "Hint: check for trailing commas or single-quoted keys."
    if "unterminated string" in msg:
        return "Hint: a quoted string is not closed."
    if "expecting value" in msg:
        return "Hint: a value is missing or a trailing comma is present."
    return "Hint: provide one JSON object with double-quoted keys and values."


try:
    data = json.loads(raw)
except json.JSONDecodeError as exc:
    lines = raw.splitlines() or [raw]
    offending = lines[exc.lineno - 1] if 0 < exc.lineno <= len(lines) else ""
    pointer = " " * max(exc.colno - 1, 0) + "^"
    print("Invalid JSON input for --from-json - NO event was filed.", file=sys.stderr)
    print(f"Line {exc.lineno}, column {exc.colno}", file=sys.stderr)
    if offending:
        # Best-effort redaction: parsing failed, so schema-aware redaction is
        # unavailable and the excerpt must not echo raw secrets.
        print(redact(offending), file=sys.stderr)
        print(pointer, file=sys.stderr)
    if path == "-":
        try:
            target_dir = scratch_dir if scratch_dir else temp_root
            import os
            os.makedirs(target_dir, exist_ok=True)
            fd, bad_path = tempfile.mkstemp(prefix="invalid-stdin.", suffix=".json", dir=target_dir)
            with open(fd, "w", encoding="utf-8", closefd=True) as bad_fh:
                bad_fh.write(raw)
            print(f"Saved payload to: {bad_path}", file=sys.stderr)
            print(f"Edit and re-file: sh .../report-friction.sh --from-json {bad_path}", file=sys.stderr)
        except Exception as save_exc:
            print(f"Unable to save invalid stdin payload: {save_exc}", file=sys.stderr)
    print(hint_for(exc.msg), file=sys.stderr)
    sys.exit(2)

if not isinstance(data, dict):
    print("Invalid JSON input for --from-json - NO event was filed.", file=sys.stderr)
    print("Hint: the payload must be one JSON object.", file=sys.stderr)
    sys.exit(2)

VALID_SOURCE_KINDS = {
    "artifact", "instruction", "tool",
    "assumption", "memory", "observation", "other",
}
TYPE_TO_KIND = {
    "file": "artifact", "url": "artifact", "documentation": "artifact",
    "conversation": "instruction", "audio": "observation", "visual": "observation",
    "tool": "tool", "assumption": "assumption", "memory": "memory",
    "observation": "observation", "other": "other",
}

errors = []
notes = []

# --- Coerce deprecated top-level fields (accept + note, never reject) ---
if data.get("pivot_information") is None and isinstance(data.get("hindsight"), str):
    data["pivot_information"] = data["hindsight"]
    notes.append("coerced deprecated 'hindsight' to pivot_information")
if data.get("recurrence_key") is None and isinstance(data.get("fingerprint_key"), str):
    data["recurrence_key"] = data["fingerprint_key"]
    notes.append("coerced deprecated 'fingerprint_key' to recurrence_key")

# --- Tags: accept array or scalar; fold aliases in ---
tags = data.get("tags")
if isinstance(tags, str):
    tags = [t.strip() for t in tags.split(",") if t.strip()]
    notes.append("coerced tags string to array")
elif tags is None:
    tags = []
elif isinstance(tags, list):
    coerced = []
    for item in tags:
        if isinstance(item, str):
            coerced.append(item)
        else:
            coerced.append(str(item))
            notes.append("coerced non-string tag to string")
    tags = coerced
else:
    errors.append("tags must be an array or comma-separated string")
    tags = []

aliases = data.get("aliases")
if aliases is not None:
    if isinstance(aliases, str):
        alias_items = [a.strip() for a in aliases.split(",") if a.strip()]
    elif isinstance(aliases, list):
        alias_items = [str(a) for a in aliases if a]
    else:
        alias_items = []
    if alias_items:
        tags = tags + [a for a in alias_items if a not in tags]
        notes.append("folded deprecated 'aliases' into tags")

# --- Build sources array ---
sources = data.get("sources")
if isinstance(sources, dict):
    sources = [sources]
    notes.append("wrapped single sources object in an array")
if sources is not None:
    if not isinstance(sources, list):
        errors.append("field must be an array when present: sources")
        sources = []
    for i, src in enumerate(sources):
        if not isinstance(src, dict):
            errors.append(f"sources[{i}] must be an object")
            continue
        if not src.get("kind") and src.get("type"):
            mapped = TYPE_TO_KIND.get(str(src["type"]).lower(), "other")
            src["kind"] = mapped
            src.pop("type", None)
            notes.append(f"coerced sources[{i}].type to kind '{mapped}'")
        if not src.get("kind"):
            errors.append(f"sources[{i}].kind is required (one of: {', '.join(sorted(VALID_SOURCE_KINDS))})")
        elif src["kind"] not in VALID_SOURCE_KINDS:
            errors.append(
                f"sources[{i}].kind must be one of: {', '.join(sorted(VALID_SOURCE_KINDS))} (got '{src['kind']}')"
            )
        if not src.get("ref"):
            errors.append(f"sources[{i}].ref is required")
        if src.get("claim") is None and isinstance(src.get("excerpt"), str):
            src["claim"] = src.pop("excerpt")
            notes.append(f"coerced sources[{i}].excerpt to claim")
        claim = src.get("claim")
        if isinstance(claim, str) and len(claim) > 2000:
            src["claim"] = claim[:2000] + f"...[truncated {len(claim) - 2000} chars at filing]"
            notes.append(f"sources[{i}].claim truncated to 2000 chars")
        for int_key in ("line", "end_line"):
            val = src.get(int_key)
            if val is not None and not isinstance(val, int):
                try:
                    src[int_key] = int(val)
                    notes.append(f"coerced sources[{i}].{int_key} to integer")
                except (TypeError, ValueError):
                    errors.append(f"sources[{i}].{int_key} must be an integer")
else:
    errors.append("missing required field: sources")

# --- Validate required narrative fields ---
required_narrative = [
    "actual_outcome",
    "expected_outcome",
    "reading",
    "decision",
    "pivot_information",
]
for req_key in required_narrative:
    value = data.get(req_key)
    if value is None:
        if req_key == "pivot_information":
            errors.append(
                "missing required field: pivot_information - name the single piece of "
                "information that, visible before acting, would have changed the outcome "
                "(or, when caught before harm, the fact a future agent should check first; "
                "or: 'none - the outcome was unknowable in advance, because ...')"
            )
        elif req_key == "decision":
            errors.append(
                "missing required field: decision - what did you do about it: the options "
                "you saw, the ones you set aside, and the action you took (even 'continued "
                "unchanged'), plus what made any deviation feel permitted at the time. "
                "Past tense - history, not proposal."
            )
        else:
            errors.append(f"missing required field: {req_key}")
    elif not isinstance(value, str):
        errors.append(f"field must be a string: {req_key}")
    elif value.strip() == "":
        errors.append(f"field must not be blank: {req_key}")

impact_val = data.get("impact")
if impact_val is not None:
    if impact_val not in ("blocked", "degraded", "noisy", "continued"):
        errors.append(f"impact must be one of: blocked, degraded, noisy, continued (got '{impact_val}')")

if errors:
    print("Invalid friction payload for --from-json - NO event was filed.", file=sys.stderr)
    for item in errors:
        print(f"- {item}", file=sys.stderr)
    sys.exit(2)

# --- Redact every user-supplied string after validation, before emission ---
tags = [redact(t) for t in tags]
sources = sources or []
for src in sources:
    if isinstance(src, dict):
        for src_key, src_val in list(src.items()):
            if isinstance(src_val, str):
                src[src_key] = redact(src_val)


def normalize(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def emit(name, value):
    # Trailing newlines would be stripped by the shell's command substitution
    # at decode time anyway; strip them here so the behavior is defined.
    encoded = base64.b64encode(value.rstrip("\n").encode("utf-8")).decode("ascii")
    print(f"{name}\t{encoded}")


keys = [
    ("title", "title"),
    ("actual_outcome", "actual_outcome"),
    ("expected_outcome", "expected_outcome"),
    ("reading", "reading"),
    ("decision", "decision"),
    ("pivot_information", "pivot_information"),
    ("note", "note"),
    ("repo_root", "repo_root"),
    ("impact", "impact"),
    ("recurrence_key", "recurrence_key"),
]

for data_key, field_name in keys:
    value = normalize(data.get(data_key))
    if value is not None:
        emit(field_name, redact(value))

if tags:
    emit("tags_csv", ",".join(tags))

emit("sources_json", json.dumps(sources, ensure_ascii=False, separators=(",", ":")))
if notes:
    emit("notes", "\n".join("note: " + n for n in notes))
