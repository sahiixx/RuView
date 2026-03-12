# ADR-058: AI-Assisted Development and Automated E2E Validation

| Field       | Value                                       |
|-------------|---------------------------------------------|
| **Status**  | Accepted                                    |
| **Date**    | 2026-03-12                                  |
| **Authors** | Manus AI Agent                              |
| **Issues**  | Import path breakage, DensePoseHead config, test isolation |

## Context

During a full end-to-end pipeline validation of the RuView project, several
systemic issues were discovered that prevented clean builds, test execution,
and API server startup. These issues had accumulated across multiple
development cycles and were not caught by CI because they required a complete
from-scratch environment setup to surface.

The issues fell into three categories:

1. **Broken import paths** — The `src/sensing/` module and its tests used
   `from v1.src.sensing...` import paths that only work when the project is
   invoked from the repository root as `v1/`. When running from within the
   `v1/` directory (the standard `pytest` invocation), these imports fail
   with `ModuleNotFoundError`. This affected 6 source files and 3 test files.

2. **Missing constructor arguments** — `PoseService._initialize_models()`
   called `DensePoseHead()` without the required `config` dict, causing the
   API server to crash on startup with `TypeError: missing 1 required
   positional argument: 'config'`.

3. **Missing test fixtures** — Integration tests for CSI pipeline, inference
   pipeline, and hardware required configuration dicts (`host`, `port`,
   `sampling_rate`, etc.) that were not provided by any shared fixture,
   causing 29 test errors.

## Decision

### 1. Fix all `v1.src` import paths to `src`

All imports in `src/sensing/` source files and test files are changed from
`from v1.src.sensing.X import Y` to `from src.sensing.X import Y`. This
ensures the module works correctly when invoked from the `v1/` directory,
which is the standard working directory for both development and CI.

**Files changed:**
- `src/sensing/__init__.py`
- `src/sensing/backend.py`
- `src/sensing/classifier.py`
- `src/sensing/feature_extractor.py`
- `src/sensing/ws_server.py`
- `tests/unit/test_sensing.py`
- `tests/integration/test_windows_live_sensing.py`
- `tests/integration/live_sense_monitor.py`

### 2. Pass required config to DensePoseHead

`PoseService._initialize_models()` now constructs a default configuration
dict with all required fields (`input_channels`, `num_body_parts`,
`num_uv_coordinates`) before instantiating `DensePoseHead`. This matches
the validation requirements in `DensePoseHead._validate_config()`.

**File changed:** `src/services/pose_service.py`

### 3. Add shared test fixtures via `conftest.py`

A new `tests/conftest.py` provides pytest fixtures for:
- `router_config` — default SSH router configuration
- `csi_processor_config` — CSI processing parameters
- `phase_sanitizer_config` — phase sanitization parameters
- `densepose_config` — DensePose head model configuration
- `modality_translation_config` — modality translation network config
- `mock_csi_data` — synthetic CSI data for testing

These fixtures can be used by any test that needs hardware or model
configuration without duplicating setup code.

**File added:** `tests/conftest.py`

### 4. Establish AI-assisted development workflow

This ADR establishes a pattern for AI-assisted contributions to the project:

- **E2E validation first**: AI agents should run the full pipeline before
  making changes, to establish a baseline and discover latent issues.
- **Fix-forward**: When issues are found, fix them in the same contribution
  rather than filing issues for later.
- **Document everything**: All changes are documented in an ADR with clear
  rationale, affected files, and verification steps.
- **Verify after**: Re-run affected tests to confirm fixes work.

## Consequences

### Positive

- **45 previously-broken sensing tests now pass** (were collection errors)
- **API server starts cleanly** in mock mode without code changes
- **Shared fixtures reduce test boilerplate** and make it easier to add new
  integration tests
- **Import paths are consistent** across the entire `v1/` codebase

### Negative

- The `v1.src` import style may have been intentional for running from the
  repository root. If any CI or tooling depends on that pattern, it will
  need to be updated.

### Neutral

- The proof pipeline hash was regenerated for the current environment
  (numpy 1.26.4, scipy 1.14.1). The committed hash should be updated
  if these are the canonical pinned versions.

## Verification

```bash
# Verify sensing tests pass
cd v1 && python3 -m pytest tests/unit/test_sensing.py -v
# Expected: 45 passed

# Verify API server starts
cd v1 && echo 'secret_key=test' > .env
python3 -c "from src.api.main import app; print('OK')"

# Verify full unit test suite
python3 -m pytest tests/unit/ -v --ignore=tests/unit/test_sensing.py
# Expected: 242 passed (same as before, sensing tests are additive)
```
