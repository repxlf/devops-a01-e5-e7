# A01/B01 Contract Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the A01 contract package so the A01/B01 mock workflow enforces the agreed input, output, provenance, report, rejection, and end-to-end rules without implementing real BuildChecker, EChecker, DRAFT, or MDFixer services.

**Architecture:** Keep the repository contract-first. JSON Schema files document the wire contract; the dependency-free `scripts/validate.py` enforces the cross-field and artifact/report rules that JSON Schema cannot express locally. Examples and tests remain mock/contract fixtures and must carry explicit provenance.

**Tech Stack:** Python 3.10 standard library, JSON Schema documents, `unittest`, Markdown, Git.

**Spec:** B01 proposal set `b01-change-proposals.md` at commit `23c0699`, the existing A01 E2 contract package, and the agreed decisions in the preceding review: accept P-01, P-02, P-04 through P-09, P-11, P-12, P-15 through P-18; retain `CANCELLED` with a cancel endpoint; define `ERROR_REPORT` as a system-error artifact; define idempotency reuse/409 behavior; and represent declaration-style notes as `PATCH_NOTES`.

## Global Constraints

- E2 remains contract/mock work; no real service deployment or analyzer execution is added.
- `main` is protected; all changes stay on `feature/e2-contract`.
- All example outputs remain `MOCK_FIXTURE` or `CONTRACT_EXAMPLE`; no fabricated `REAL_TOOL_OUTPUT` is introduced.
- `INCREMENTAL_CHECK` requires a baseline commit and matching environment configuration.
- `REPAIR` consumes only an artifact URI for the MD report and requires the report to match the requested repository commit and configuration.
- Findings (`MISSING`/`REDUNDANT`) are analysis results, not execution errors; rejected repair candidates are successful jobs with `output.decision = REJECTED`.

## Review Focus

- A successful job with `output: null` must be rejected; test `validate_job`.
- A DRAFT missing `verify_command` or a REPAIR missing `target_file`/`environment` must be rejected; test `validate_request`.
- An incremental request missing `environment` or using a mismatched configuration must be rejected; test `validate_request`.
- A REPAIR report from another commit/configuration must be rejected; test report resolution and cross-field matching.
- A report or consistency result must not use repository-relative artifact paths; test report validation.

### Task 1: Add failing contract-hardening tests

**Files:**
- Create: `tests/test_contract_hardening.py`
- Modify: `tests/test_e2_contract.py` only if the resolved-finding representation changes from the current A01 fixture shape.

**Interfaces:**
- Consumes: existing `scripts.validate.load`, `validate_request`, and `validate_job`.
- Produces: executable expectations for request completeness, job output requirements, report validation, artifact metadata, response fixtures, and the B01 rejected repair case.

- [ ] **Step 1: Write the failing tests**

```python
def test_draft_requires_verify_command():
    request = validate.load("examples/draft/draft-request.json")
    request["input"]["build"].pop("verify_command")
    with self.assertRaises(ValueError):
        validate.validate_request(request)

def test_repair_report_must_match_repository_and_configuration():
    request = validate.load("examples/repair/repair-request.json")
    request["input"]["repository"]["commit"] = "...c1"
    with self.assertRaises(ValueError):
        validate.validate_request(request)

def test_succeeded_job_requires_output_object():
    job = validate.load("examples/e2-contract/full-check-success.json")
    job["output"] = None
    with self.assertRaises(ValueError):
        validate.validate_job(job)

def test_report_samples_and_consistency_report_are_valid():
    validate.validate_report(validate.load("examples/build-checker/md-rd-report-c0.json"))
    validate.validate_report(validate.load("examples/e-checker/consistency-report-c1.json"))
```

- [ ] **Step 2: Run the focused tests and verify they fail for missing contract behavior**

Run: `python -m unittest tests.test_contract_hardening -v`

Expected: failures for the missing request checks, missing `validate_report`, incomplete fixtures, and nullable successful output—not unrelated import or syntax errors.

### Task 2: Align request/job/artifact/report schemas and fixtures

**Files:**
- Modify: `schemas/job-request.schema.json`
- Modify: `schemas/task.schema.json`
- Modify: `schemas/artifact.schema.json`
- Modify: `schemas/finding.schema.json` only where the resolved-finding representation requires it.
- Create: `schemas/report.schema.json`
- Modify: `examples/draft/draft-request.json`, `examples/draft/draft-success.json`
- Modify: `examples/repair/repair-request.json`, `examples/repair/repair-result.json`
- Create: `examples/b01/repair-rejected.json`
- Create: `examples/e2-contract/full-check-created.json`
- Create: `examples/e2-contract/rejected-invalid-request.json`
- Modify: graph/report/job examples to carry commit/configuration metadata and `artifact://` references.

**Interfaces:**
- Consumes: the four request types and canonical Job envelope.
- Produces: a documented contract for type-specific input, successful output, report envelopes, PATCH_NOTES, cancel/rejection semantics, and artifact provenance.

- [ ] **Step 1: Add schema assertions to the focused tests**

Assert that the schema documents contain: conditional `required: ["output"]` for `SUCCEEDED`, required INCREMENTAL environment fields, required REPAIR environment/target fields, artifact `commit`/`configuration_id`, `PATCH_NOTES`, and report variants.

- [ ] **Step 2: Run the focused tests and verify they fail against the current schemas/fixtures**

Run: `python -m unittest tests.test_contract_hardening -v`

Expected: the new schema and fixture assertions fail before edits.

- [ ] **Step 3: Implement the minimal schema and fixture changes**

Use `build_command`/`verify_command` and `limits.max_iterations` consistently for DRAFT; require `environment` for INCREMENTAL_CHECK and REPAIR; require a non-null object output for successful jobs; retain `CANCELLED` and document `POST /v1/jobs/{job_id}/cancel`; add `PATCH_NOTES`; use `artifact://` for report references; and keep all new files marked as mock/contract examples.

- [ ] **Step 4: Run the focused tests and verify they pass**

Run: `python -m unittest tests.test_contract_hardening -v`

Expected: all new tests pass.

### Task 3: Implement dependency-free validation for cross-field rules

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_contract_hardening.py`

**Interfaces:**
- Consumes: request/job/report/artifact JSON fixtures.
- Produces: `validate_request`, `validate_job`, `validate_report`, and scenario checks that reject invalid inputs before a mock Job is created.

- [ ] **Step 1: Add tests for every rejected fixture**

Cover missing DRAFT verification, missing FULL_CHECK environment, missing REPAIR target/environment, mismatched REPAIR report commit/configuration, missing incremental environment, invalid report URI, and rejected-candidate semantics.

- [ ] **Step 2: Run the focused tests and verify each new case fails before implementation**

Run: `python -m unittest tests.test_contract_hardening -v`

Expected: each newly asserted gap fails with a `ValueError` expectation or missing validator function.

- [ ] **Step 3: Implement minimal validation**

Add type-specific required-field checks, mandatory incremental configuration matching, report lookup from the repository-relative `artifact://pair-A01-B01/job-.../<file>` fixture URI, REPAIR report commit/configuration matching, successful-output enforcement, artifact provenance checks, report envelope validation, and validation of the new 202/rejection fixtures.

- [ ] **Step 4: Run focused and full tests**

Run: `python -m unittest tests.test_contract_hardening -v` then `python -m unittest discover -s tests -v`.

Expected: the focused tests and the full suite pass with no failures.

### Task 4: Update API/workflow documentation and traceability

**Files:**
- Modify: `docs/API_CONTRACT.md`
- Modify: `docs/END_TO_END_FLOW.md`
- Modify: `docs/BACKLOG.md`
- Modify: `docs/ADR-002-artifact-uri.md`, `docs/ADR-003-findings-vs-system-errors.md`, `docs/ADR-004-incremental-baseline.md`
- Create: `docs/ADR-005-repair-report-source-match.md`
- Create: `CHANGELOG.md`
- Modify: `README.md`, `docs/E2_CHECKLIST.md`, `docs/GIT_TRACEABILITY.md`

**Interfaces:**
- Consumes: the finalized schemas and validator behavior.
- Produces: human-readable API/status/idempotency/cancel/rejection semantics, REPAIR/RECHECK ownership, artifact URI rules, and a dated change record.

- [ ] **Step 1: Add documentation assertions to tests**

Assert that the API document names the cancel endpoint, `400` rejection, idempotency reuse/409 behavior, and that the end-to-end document includes DRAFT and separates consistency evaluation from RECHECK.

- [ ] **Step 2: Run the focused documentation tests and verify they fail**

Run: `python -m unittest tests.test_contract_hardening -v`

Expected: the new text assertions fail against the current documents.

- [ ] **Step 3: Update the documents**

Record only decisions represented by the schemas/examples; keep unresolved classroom signature fields blank and mark every example as mock/contract data.

- [ ] **Step 4: Run all tests and contract checks**

Run: `python scripts/validate.py`, `python scripts/run_mock_flow.py`, and `python -m unittest discover -s tests -v`.

Expected: all commands exit 0 and the mock flow explicitly reports that no real build/analyzer executed.

### Task 5: Review, diff, commit, and push the feature branch

**Files:**
- Review: all changed files on `feature/e2-contract`.

- [ ] **Step 1: Run final structural checks**

Run: `git diff --check` and parse every `*.json` file with Python's standard `json` module.

- [ ] **Step 2: Inspect the staged diff for scope**

Confirm no credentials, real private URLs, generated caches, or changes to `main` are included.

- [ ] **Step 3: Commit the verified contract hardening changes**

Commit message: `feat: align A01 contract with B01 review`

- [ ] **Step 4: Push only the feature branch**

Run: `git push origin feature/e2-contract`; never use force push.
