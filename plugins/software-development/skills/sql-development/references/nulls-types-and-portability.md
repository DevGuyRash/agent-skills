# SQL NULLs, Types, and Portability

Load this reference for NULL behavior, coercion, numeric or temporal data, text comparison, identifiers, or support across multiple relational engines.

## Three-Valued Logic

- Ordinary comparisons with NULL produce UNKNOWN, not TRUE or FALSE. Use `IS NULL`, `IS NOT NULL`, or a supported null-safe comparison.
- A filter retains TRUE and rejects FALSE and UNKNOWN. Check nullable predicates explicitly.
- A nullable value in a `NOT IN` input can make the result UNKNOWN. Use the form that expresses the intended anti-match and test NULL plus empty-set cases.
- `CHECK` constraints and joins also encounter UNKNOWN; do not assume filter behavior transfers unchanged.
- `COALESCE` changes meaning by replacing absence. Use it only when the replacement is a valid domain value.
- Check aggregate behavior on empty input and on groups containing only NULLs.

## Type Semantics

- Avoid implicit casts when precision, index use, collation, comparison, or portability matters.
- Choose exact versus approximate numeric types deliberately and define rounding at the correct boundary.
- Distinguish a timestamp/instant from local date-time, date, time-of-day, and duration. Define timezone conversion and daylight-saving behavior.
- Define text collation, case sensitivity, normalization, and locale requirements where equality or ordering is user-visible.
- Treat boolean, JSON, arrays, UUIDs, enums, binary data, and auto-generated identifiers as dialect-specific until verified.
- Test overflow, truncation, invalid dates, and conversion failures using the target engine's configured modes.

## Portability

- Port only across the database/version matrix the project actually supports.
- Isolate vendor syntax and functions where multiple engines must share a core, but do not sacrifice correctness for superficial textual similarity.
- Check identifier quoting, case folding, reserved words, maximum lengths, placeholder syntax, and statement delimiters.
- Check NULL uniqueness, NULL ordering, empty-string handling, upsert/merge behavior, generated values, and DDL transactional behavior per engine.
- Treat compatibility modes and session settings as part of the dialect profile.
- Verify on every claimed target rather than declaring portability from inspection alone.

Useful primary examples: [PostgreSQL comparison functions](https://www.postgresql.org/docs/current/functions-comparison.html), [MySQL SQL modes](https://dev.mysql.com/doc/refman/8.4/en/sql-mode.html), and [SQLite type affinity](https://www.sqlite.org/datatype3.html).
