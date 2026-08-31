---
name: sql-development
description: Use for relational SQL queries, schemas, constraints, transactions, isolation, migrations, or embedded SQL. Compose with host languages; exclude NoSQL and administration without SQL effects.
---

# SQL Development

## Purpose

Preserve query meaning, invariants, transactions, and construction in the repository's dialect.

## Compose Deliberately

- For engine-specific behavior, use an installed vendor skill; otherwise consult detected engine/version primary documentation and name assumptions or unverified semantics.
- Add `systematic-debugging` first for an unexplained slowdown. Add `performance-engineering` once the workload and criterion are explicit, or after diagnosis when validating a query, index, or data-structure change. Read [plans-and-indexes.md](<skills-file-root>/references/plans-and-indexes.md) for the SQL-specific plan, statistics, parameter-type, spill, and index evidence. Keep SQL correctness active whenever a query or schema changes.
- Add the host-language skill for embedded SQL or query-builder code.
- Add ORM/framework guidance for model APIs or generated SQL; retain this skill only for relational semantics.
- Exclude NoSQL, backups, replication, HA, and administration without SQL effects.

## Establish the Database Profile

Before editing:

1. Read repository instructions, nearby SQL, schema definitions, and migrations.
2. Identify engine/version matrix, extensions, compatibility modes, and consequential settings.
3. Identify migration tool, driver/ORM, pooling, placeholders, and query conventions.
4. Locate schema truth, fixtures, test databases, CI, and deployment order.
5. Define expected row shape, cardinality, ordering, duplicates, affected-row behavior, and error behavior.
6. Determine which environment can be queried or mutated and what authorization protects consequential operations.

Do not infer a dialect from `.sql`; if unknown, avoid dialect-sensitive edits and name missing evidence.

## Preserve Query Semantics

- Treat rows as unordered unless an explicit `ORDER BY` establishes order.
- Add deterministic tie-breakers when pagination, limits, windows, or external output require stable ordering.
- Model expected multiplicity across every join; do not use `DISTINCT` to conceal an accidental many-to-many result.
- Keep predicates on nullable outer-join sides from silently changing the join's meaning.
- Choose set, join, subquery, and existence forms from required semantics and target behavior.
- Define destructive DML scope and expected affected-row counts before execution.

Read [query-semantics.md](<skills-file-root>/references/query-semantics.md) for joins, aggregates, subqueries, set operations, windows, ordering, pagination, and DML scope.

## Encode Data Invariants

- Use supported and enforced keys, foreign keys, uniqueness, nullability, and checks for invariants the database should protect.
- Choose data types from domain range, precision, temporal, collation, and storage semantics rather than generic convenience.
- Treat keys, normalization, soft deletion, and audit fields as domain/deployment decisions.
- Preserve the repository's migration history and tool; do not rewrite an applied migration casually.
- Require explicit authority and recovery planning for destructive or irreversible changes.

Read [schema-and-migrations.md](<skills-file-root>/references/schema-and-migrations.md) for constraints, schema design, backfills, compatibility windows, and migration safety.

## Handle NULLs and Dialect Differences Explicitly

- Distinguish NULL from empty, zero, false, and an absent row.
- Use NULL predicates or supported null-safe comparison rather than ordinary equality.
- Account for three-valued logic in filters, checks, joins, and especially nullable `NOT IN` inputs.
- Avoid relying on implicit casts, default collation, timezone, precision, identifier folding, NULL ordering, or empty-string behavior.

Read [nulls-types-and-portability.md](<skills-file-root>/references/nulls-types-and-portability.md) when NULL, coercion, temporal data, numeric precision, text comparison, identifiers, or multiple engines are relevant.

## Protect Transaction and Security Boundaries

- Define each transaction around the invariant it protects and keep it no broader or longer than required.
- Select isolation and locking from the anomalies to prevent, not from isolation names alone.
- Account for autocommit, pooled state, savepoints, DDL, deadlocks, and retry safety.
- For embedded or streamed execution, own statement cancellation, cursor/result drainage or closure, transaction outcome, and sanitized connection return separately; a canceled caller does not prove server work stopped or pooled session state was reset.
- Bind data values through the repository's driver or prepared API.
- Allowlist and dialect-quote dynamic identifiers or SQL fragments that parameters cannot represent.
- Keep authorization, tenant isolation, and least privilege separate from input parameterization.

Read [transactions-and-concurrency.md](<skills-file-root>/references/transactions-and-concurrency.md) when atomicity, isolation, locks, retries, idempotency, or external effects drive the change. Read [parameters-and-security.md](<skills-file-root>/references/parameters-and-security.md) instead when query construction, dynamic identifiers, privileges, tenant boundaries, or sensitive data are the primary risk; load both only when both contracts materially interact.

## Verify Against the Real Contract

Use configured SQL tools, test databases, and CI. Do not invent a runner or connect to an unconfirmed target.

Run the narrowest safe existing checks for results, edge cases, constraints, affected rows, migration state, and relevant concurrency. Read [verification.md](<skills-file-root>/references/verification.md) when designing new database checks, applying a migration, validating concurrent behavior, executing consequential DML, or claiming behavior across engines or versions. For performance claims, distinguish result correctness from optimizer evidence and include representative data volume, distribution, parameter types, and write/storage tradeoffs. Report engine/version, settings, commands, outcomes, and untested production-scale or cross-engine behavior.

## Avoid Universal Mandates

Do not prescribe “ANSI SQL,” casing, naming, `SELECT *` bans, normalization, identifier strategy, soft deletes, procedures, ORMs, isolation, migration tools, blanket retries, or shape-only indexes. Never mutate an unknown or unauthorized database.
