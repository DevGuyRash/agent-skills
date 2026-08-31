//! Mechanical verification for caller-neutral comparative-evidence envelopes.

use anyhow::{bail, Context, Result};
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
use std::fs;
use std::path::Path;

const REQUEST_SCHEMA: &str = "comparative-evidence-request.v1";
const RESULT_SCHEMA: &str = "comparative-evidence-result.v1";

pub(crate) fn verify(request_path: &Path, result_path: &Path) -> Result<Value> {
    let request_bytes = fs::read(request_path)
        .with_context(|| format!("cannot read request: {}", request_path.display()))?;
    let result_bytes = fs::read(result_path)
        .with_context(|| format!("cannot read result: {}", result_path.display()))?;
    std::str::from_utf8(&request_bytes).context("request is not valid UTF-8")?;
    std::str::from_utf8(&result_bytes).context("result is not valid UTF-8")?;

    let request: Value =
        serde_json::from_slice(&request_bytes).context("request is not valid JSON")?;
    let result: Value =
        serde_json::from_slice(&result_bytes).context("result is not valid JSON")?;
    let request = object(&request, "request")?;
    let result = object(&result, "result")?;

    require_schema(request, REQUEST_SCHEMA, "request")?;
    require_schema(result, RESULT_SCHEMA, "result")?;
    require_fields(
        request,
        &[
            "schema",
            "claim_id",
            "target_ref",
            "authority_ref",
            "claim",
            "decision_context",
            "existing_evidence_refs",
            "closure_conditions",
            "unresolved_consequence",
            "prohibited_effects",
        ],
        "request",
    )?;
    require_fields(
        result,
        &[
            "schema",
            "claim_id",
            "request_digest",
            "tested_conditions",
            "conclusion",
            "closure_assessment",
            "evidence_refs",
            "scope_and_limits",
            "uncertainty",
            "reopening_conditions",
        ],
        "result",
    )?;

    let claim_id = nonempty_string(request, "claim_id", "request")?;
    let result_claim_id = nonempty_string(result, "claim_id", "result")?;
    if claim_id != result_claim_id {
        bail!("result claim_id does not match request claim_id");
    }
    let _ = nonempty_string(request, "claim", "request")?;
    require_array(request, "existing_evidence_refs", "request")?;
    require_array(result, "evidence_refs", "result")?;
    optional_object(request, "extensions", "request")?;
    optional_object(result, "extensions", "result")?;

    let request_ids = closure_condition_ids(request)?;
    let result_ids = closure_assessment_ids(result)?;
    if request_ids != result_ids {
        let missing = request_ids
            .difference(&result_ids)
            .cloned()
            .collect::<Vec<_>>();
        let unexpected = result_ids
            .difference(&request_ids)
            .cloned()
            .collect::<Vec<_>>();
        bail!(
            "closure assessment does not cover request exactly (missing: {}; unexpected: {})",
            display_ids(&missing),
            display_ids(&unexpected)
        );
    }

    let request_digest = format!("{:x}", Sha256::digest(&request_bytes));
    let supplied_digest = nonempty_string(result, "request_digest", "result")?;
    if supplied_digest != request_digest {
        bail!("result request_digest does not match exact request bytes");
    }

    Ok(json!({
        "schema": "comparative-evidence-exchange-verification.v1",
        "claim_id": claim_id,
        "request_digest": request_digest,
        "closure_condition_count": request_ids.len(),
        "verified": true
    }))
}

fn object<'a>(value: &'a Value, label: &str) -> Result<&'a Map<String, Value>> {
    value
        .as_object()
        .with_context(|| format!("{label} must be a JSON object"))
}

fn require_schema(object: &Map<String, Value>, expected: &str, label: &str) -> Result<()> {
    let actual = nonempty_string(object, "schema", label)?;
    if actual != expected {
        bail!("unsupported {label} schema: {actual}");
    }
    Ok(())
}

fn require_fields(object: &Map<String, Value>, fields: &[&str], label: &str) -> Result<()> {
    for field in fields {
        if !object.contains_key(*field) {
            bail!("{label} is missing required field: {field}");
        }
    }
    Ok(())
}

fn nonempty_string<'a>(
    object: &'a Map<String, Value>,
    field: &str,
    label: &str,
) -> Result<&'a str> {
    let value = object
        .get(field)
        .and_then(Value::as_str)
        .with_context(|| format!("{label}.{field} must be a string"))?;
    if value.is_empty() {
        bail!("{label}.{field} must not be empty");
    }
    Ok(value)
}

fn require_array<'a>(
    object: &'a Map<String, Value>,
    field: &str,
    label: &str,
) -> Result<&'a [Value]> {
    object
        .get(field)
        .and_then(Value::as_array)
        .map(Vec::as_slice)
        .with_context(|| format!("{label}.{field} must be an array"))
}

fn optional_object(object: &Map<String, Value>, field: &str, label: &str) -> Result<()> {
    if object.get(field).is_some_and(|value| !value.is_object()) {
        bail!("{label}.{field} must be an object when present");
    }
    Ok(())
}

fn closure_condition_ids(request: &Map<String, Value>) -> Result<BTreeSet<String>> {
    let conditions = require_array(request, "closure_conditions", "request")?;
    if conditions.is_empty() {
        bail!("request.closure_conditions must not be empty");
    }
    let mut ids = BTreeSet::new();
    for (index, condition) in conditions.iter().enumerate() {
        let condition = object(condition, &format!("closure condition {index}"))?;
        let id = nonempty_string(condition, "id", &format!("closure condition {index}"))?;
        let _ = nonempty_string(
            condition,
            "statement",
            &format!("closure condition {index}"),
        )?;
        if !ids.insert(id.to_owned()) {
            bail!("duplicate closure-condition id: {id}");
        }
    }
    Ok(ids)
}

fn closure_assessment_ids(result: &Map<String, Value>) -> Result<BTreeSet<String>> {
    let assessments = require_array(result, "closure_assessment", "result")?;
    if assessments.is_empty() {
        bail!("result.closure_assessment must not be empty");
    }
    let mut ids = BTreeSet::new();
    for (index, assessment) in assessments.iter().enumerate() {
        let assessment = object(assessment, &format!("closure assessment {index}"))?;
        let id = nonempty_string(
            assessment,
            "condition_id",
            &format!("closure assessment {index}"),
        )?;
        let status = nonempty_string(assessment, "status", &format!("closure assessment {index}"))?;
        if !matches!(status, "closes" | "narrows" | "does_not_resolve") {
            bail!("unsupported closure-assessment status: {status}");
        }
        if !ids.insert(id.to_owned()) {
            bail!("duplicate closure-assessment id: {id}");
        }
    }
    Ok(ids)
}

fn display_ids(ids: &[String]) -> String {
    if ids.is_empty() {
        "none".to_owned()
    } else {
        ids.join(", ")
    }
}
