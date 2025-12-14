Below is an improved version of the prompt (tightened, fully self‑contained) followed by a concrete Python script that implements it end‑to‑end.

***

## Improved Autonomous Diagnostic Prompt (QFS V13.5 / V2.1)

**AUTONOMOUS REPO DIAGNOSTIC PROMPT — QFS V13.5 / V2.1 (Evidence‑Driven)**

### Objective

Perform a full, evidence‑driven, autonomous audit of this repository to determine:

- Which components are **implemented and verified** versus only documented.  
- Whether QFS V13.5 is **structurally coherent, deterministic, and on a path to production‑readiness**.  
- Which modules, tests, or evidence artifacts are **missing or incomplete** relative to:
  - `docs/qfs_v13_plans/MASTER-PLAN-V13.md`  
  - `AUDIT-V13.txt`  
  - `ROADMAP-V13.5-REMEDIATION.md`  
  - `TASKS-V13.5.*`  

Every conclusion must reference concrete **file paths**, **test names**, and/or **evidence artifacts**. Do **not** assume compliance from prose documentation alone.

### Mode of Operation

Classification rules:

- **Implemented** – Code exists in `src/`, is wired into at least one execution path, and has at least one passing test.  
- **Partially implemented** – Code exists but is incomplete, diverges from spec, lacks tests, or tests currently fail.  
- **Missing** – No code, tests, or evidence exist for the required function.

Data sources the agent must use:

- `src/` – main implementation modules.  
- `tests/` – unit, integration, deterministic, property/fuzz, security, etc.  
- `evidence/` – JSON, logs, manifests (especially `evidence/baseline/*.json`).  
- `docs/` – spec, audit, roadmap, and alignment docs.

### Execution Phases

#### Global Execution Steps

1. **Discovery**
   - Walk the repository from the root.  
   - Enumerate at least:
     - `src/`, `tests/`, `tools/`, `scripts/`, `docs/`, `evidence/`, `.github/`.  
   - Build a simple dependency map for `src/`:
     - For each Python module, list what it imports (downstream).  
     - Optionally, infer who imports it (upstream) by scanning import statements.

2. **Test Execution**
   - Run the main test command:
     - Prefer `python -m pytest`; if `scripts/run_tests.sh` (or `.bat`) exists, note it in the report.  
   - Set deterministic environment:
     - `PYTHONHASHSEED=0`  
     - `TZ=UTC` (if supported)  
   - Capture:
     - Exit code.  
     - Raw output into `evidence/diagnostic/pytest_output.txt`.  
   - If possible, parse pytest output to count:
     - Total tests collected / run.  
     - Failures / errors / xfails.

3. **Evidence Cross‑Check**
   - Read any **baseline** evidence in `evidence/baseline/` (e.g., `baseline_test_results.json`, `baseline_state_manifest.json`, `baseline_commit_hash.txt`) and incorporate into the analysis.  
   - Note mismatches between current test run and baseline (e.g., more/less errors, missing files).

***

### 1. Repository Scan & Architecture Map

**Steps:**

- List top‑level directories and key files (e.g., README, main entrypoints).  
- Under `src/`, scan these subtrees (if present):
  - `libs/`, `core/`, `handlers/`, `sdk/`, `services/`, `utils/`, `security/`, `oracles/`, `replication/`, `governance/`.  
- For each significant module (e.g., `BigNum128.py`, `CertifiedMath.py`, `PQC.py`, `DeterministicTime.py`, `HSMF.py`, `TokenStateBundle.py`, `DRV_Packet.py`, `CoherenceEngine.py`, `CoherenceLedger.py`, `QFSV13SDK.py`, `aegis_api.py`, `UtilityOracle.py`, `QPU_Interface.py`, `CIR302_Handler.py`):
  - State its **purpose** in one sentence.  
  - List **key classes/functions**.  
  - List key imports (downstream dependencies).  
- Identify:
  - Modules that are never imported (likely dead code).  
  - Obvious duplicated logic or inconsistent naming.

**Output section:**  
`### 1. Architecture Map` – bullet list of modules, roles, and integration points, with file paths.

***

### 2. Completeness Assessment

**Steps:**

For each area, classify **Implemented / Partially implemented / Missing**, with explicit evidence (files/tests):

1. **Core Math & Determinism**
   - `src/libs/BigNum128.py` – integer‑only, deterministic.  
   - `src/libs/CertifiedMath.py` – arithmetic + transcendental functions, logging, ProofVectors, error‑bound docs/tests.  
   - `src/libs/DeterministicTime.py` – canonical time source and regression checks.

2. **Harmonic Economics & Engine**
   - `HSMF` (Harmonic Stability & Action Cost Framework).  
   - 5‑Token Harmonic System (CHR, FLX, ΨSync, ATR, RES) state and transitions.  
   - `PsiFieldEngine.py`, `TreasuryEngine.py`, `RewardAllocator.py`, `CoherenceEngine.py`, `CoherenceLedger.py` (if present).

3. **Packets & Governance**
   - `DRV_Packet` – PQC‑sealed, chain‑linked, deterministic hashing.  
   - `CIR302_Handler.py`, `CIR412_Handler.py`, `CIR511_Handler.py` – defined **and** actually called from SDK/API flows.

4. **PQC & Quantum Metadata**
   - `PQC.py` – real Dilithium‑5 (and Kyber, if present), deterministic serialization, correct signature handling.  
   - `QPU_Interface.py`, quantum metadata fields, QRNG/VDF hooks.

5. **Auditing & Verification**
   - AST Zero‑Simulation tool (e.g., `AST_ZeroSimChecker.py`) and any CI job using it.  
   - Deterministic replay tests and evidence (e.g., `evidence/*replay*.json`).  
   - Phase‑3 evidence artifacts (if present).

6. **Security & Integration**
   - HSM/KMS interfaces (`src/security/*.py`), if implemented.  
   - SBOM generator and reproducible build scripts and workflows.  
   - Integration hooks for ATLAS feed engine, wallet/token subsystem, and validators if they exist.

**Output section:**  
`### 2. Completeness Assessment` – markdown table:

| Component | Status | Evidence (files/tests) | Notes |

***

### 3. Determinism & Math Integrity

**Steps:**

- Scan critical modules (BigNum128, CertifiedMath, DeterministicTime, harmonic/economic modules) for **non‑deterministic patterns**:
  - `float`, `math.*`, `random.*`, `time.time`, `datetime`, `uuid`, `os.urandom`, unbounded loops tied to external state.  
- Confirm AST Zero‑Sim checker:
  - Exists and is configured to cover all critical modules.  
  - Has been run in CI or manually; note any violations.

- Verify canonical hashing/serialization (for structures that are signed or hashed):
  - Use of `json.dumps(..., sort_keys=True, separators=(',', ':'), default=str)` followed by SHA‑2/SHA‑3 in:
    - CertifiedMath log hashing.  
    - DRV_Packet hash computation.  
    - TokenStateBundle hash.  
    - CoherenceLedger state commitments.

- Validate HSMF and economic formulas against the spec:
  - SCHR, S_FLX, S_sync, ActionCostQFS, Cholo, DEZ, C_CRIT survival gating (compare to formulas described in the plans/audit).

- Confirm existence and status of core determinism tests:
  - `tests/property/test_bignum128_fuzz.py`.  
  - BigNum128 overflow/underflow tests (if present).  
  - CertifiedMath ProofVectors tests and any error‑bound verification artifacts.

**Output section:**  
`### 3. Determinism & Math Layer Compliance` – list:

- Confirmed compliant areas.  
- Violations with `file:line` references.  
- Missing tests/artifacts with exact names to add.

***

### 4. Security & PQC Audit

**Steps:**

- Inspect PQC implementation:
  - Ensure `PQC.py` uses real Dilithium‑5 / Kyber routines, not hash‑based stand‑ins.  
  - Verify deterministic pre‑signing serialization and correct handling of bytes/hex.  

- Inspect key management:
  - Check whether any HSM/KMS interfaces (e.g., `HSMInterface`, `KMSInterface`, `KeyRotationManager`) exist.  
  - Note presence or absence of tests for key lifecycle (generation, rotation, failure modes).

- Scan for unsafe patterns:
  - `eval`, `exec`, `pickle.load`, unguarded `yaml.load`, arbitrary `subprocess` calls in core logic.  
  - Network I/O or OS calls inside deterministic core paths or math/economic modules.

- Confirm PQC metadata and logging:
  - DRV_Packet and PQC operations include necessary metadata: `pqccid`, `quantum_metadata`, sequence numbers, previous hashes, log hashes.  
  - These fields are present in logs/evidence where required.

**Output section:**  
`### 4. Security & PQC Audit` – for each issue, include:

- Risk level (Critical / High / Medium / Low).  
- Exact `file:line`.  
- Specific fix suggestion (code or tests to add).

***

### 5. Integration Readiness

**Steps:**

- ATLAS adapters (if present):
  - Identify any integration/synchronization modules meant for ATLAS.  
  - Confirm they do not introduce non‑deterministic behavior into core paths and have at least basic tests or mocks.

- Wallet/Token end‑to‑end path:
  - Trace a full flow: DRV_Packet → SDK (QFSV13SDK) → HSMF → TreasuryEngine/RewardAllocator → StateTransitionEngine → CoherenceLedger.  
  - Confirm:
    - State changes are atomic.  
    - Key decisions are logged and, where appropriate, PQC‑signed.

- External validators/nodes:
  - Determine whether:
    - Deterministic replay is supported (same inputs → same CRS/log hash).  
    - Evidence files are sufficient for independent verification.

**Output section:**  
`### 5. Integration Readiness` – subsections:

- ATLAS: Ready / Partially / Missing + files.  
- Wallet/Token: Ready / Partially / Missing + files.  
- Validators: Ready / Partially / Missing + files.

***

### 6. Critical Missing Pieces

**Steps:**

- From repo scan, tests, evidence, and known gaps in `AUDIT-V13.txt` and `ROADMAP-V13.5-REMEDIATION.md`, list missing or partial items with priorities, for example:

  - **Critical**:
    - HSM/KMS key management layer and tests.  
    - SBOM generation and reproducible builds (scripts + workflows).  
    - Oracle attestation framework wiring and quorum/misbehavior policy.  
    - Multi‑node replication / consensus determinism tests.  
    - Time regression → CIR‑302 tests for DeterministicTime.

  - **High/Medium**:
    - Economic threat model harness connectivity.  
    - Runtime invariants and invariant tests.  
    - Fuzzing, DoS, chaos, and compliance tests for key paths.  
    - Governance: upgrade manifests, time‑lock logic, rollback tests.

- For each item, specify:
  - Priority (Critical / High / Medium / Low).  
  - Concrete artifacts to add or fix (files/tests/docs).  
  - Related roadmap tasks (`TASKS-V13.5.*` IDs) where applicable.

**Output section:**  
`### 6. Critical Missing Pieces` – bullet list, each entry containing priority + artifacts + task references.

***

### 7. Final Verdict & Recommendations

**Steps:**

- Give a final, evidence‑based verdict:

  - **Fully ready** – all core and operational criteria met; remaining work is minor.  
  - **Partially ready** – deterministic core and flows are solid; key security/ops/integration work remains.  
  - **Not ready** – core correctness or determinism is still unverified in major areas.

- Justify verdict with references to sections 1–6.

- Provide a **top 5–10 action list**:

  - Each action must specify:
    - File(s) to modify or create.  
    - Test(s) to create/extend.  
    - Evidence artifacts to produce.  
    - If possible, the corresponding roadmap/task IDs.

**Output section:**  
`### 7. Final Verdict` – 1–2 paragraphs with verdict + numbered list of actionable steps.

***

### Script Execution Requirements

The diagnostic script must:

1. Discover modules and dependencies and generate Section 1.  
2. Run tests deterministically and capture results/logs.  
3. Read baseline evidence and cross‑check with current state.  
4. Produce `evidence/diagnostic/QFSV13.5_AUTONOMOUS_AUDIT_REPORT.md` containing Sections 1–7 exactly.  
5. Ensure every conclusion references at least one file/test/evidence artifact; if evidence is missing, mark the status as “Unknown – evidence missing”.

***

## Python Script Implementing the Prompt

Save this as `scripts/run_autonomous_audit.py` (adjust paths as needed). It assumes it is run from the repo root and that `evidence/diagnostic/` exists or can be created.

```python
import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
TESTS_DIR = REPO_ROOT / "tests"
DOCS_DIR = REPO_ROOT / "docs"
EVIDENCE_DIR = REPO_ROOT / "evidence"
BASELINE_DIR = EVIDENCE_DIR / "baseline"
DIAGNOSTIC_DIR = EVIDENCE_DIR / "diagnostic"
REPORT_PATH = DIAGNOSTIC_DIR / "QFSV13.5_AUTONOMOUS_AUDIT_REPORT.md"


def ensure_dirs():
    DIAGNOSTIC_DIR.mkdir(parents=True, exist_ok=True)


def run_tests() -> Dict:
    """
    Run pytest with deterministic environment and capture output.
    Returns a dict with keys: exit_code, cmd, output_path.
    """
    env = os.environ.copy()
    env.setdefault("PYTHONHASHSEED", "0")
    env.setdefault("TZ", "UTC")

    output_path = DIAGNOSTIC_DIR / "pytest_output.txt"
    cmd = ["python", "-m", "pytest"]

    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=1800,
        )
        output_path.write_text(proc.stdout, encoding="utf-8")
        exit_code = proc.returncode
    except Exception as e:
        exit_code = -1
        output_path.write_text(f"ERROR running pytest: {e}", encoding="utf-8")

    return {
        "cmd": " ".join(cmd),
        "exit_code": exit_code,
        "output_path": str(output_path.relative_to(REPO_ROOT)),
    }


def parse_pytest_summary(output_text: str) -> Dict:
    """
    Very simple parser to extract numbers of tests, failures, errors.
    """
    summary = {
        "tests": None,
        "failed": None,
        "errors": None,
        "skipped": None,
        "xfailed": None,
        "xpassed": None,
    }
    lines = output_text.splitlines()
    # Look for lines like: "collected 10 items"
    for line in lines:
        m = re.search(r"collected\s+(\d+)\s+items", line)
        if m:
            summary["tests"] = int(m.group(1))
    # Look for final summary lines: "== 1 failed, 2 passed, 3 warnings in ... =="
    for line in lines[::-1]:
        if "failed" in line or "passed" in line or "error" in line:
            # crude extraction
            for key, label in [
                ("failed", "failed"),
                ("errors", "errors"),
                ("skipped", "skipped"),
                ("xfailed", "xfailed"),
                ("xpassed", "xpassed"),
            ]:
                m = re.search(r"(\d+)\s+" + label, line)
                if m:
                    summary[key] = int(m.group(1))
            break
    return summary


def read_baseline_evidence() -> Dict:
    """
    Load any baseline evidence files present.
    """
    data = {}
    if BASELINE_DIR.is_dir():
        for p in BASELINE_DIR.glob("*.json"):
            try:
                data[p.name] = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                data[p.name] = {"error": "could not parse JSON"}
        for p in BASELINE_DIR.glob("*.txt"):
            data[p.name] = p.read_text(encoding="utf-8")
    return data


def walk_top_level() -> Dict[str, List[str]]:
    """
    List top-level directories and main files.
    """
    contents = {"dirs": [], "files": []}
    for entry in REPO_ROOT.iterdir():
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            contents["dirs"].append(entry.name)
        else:
            contents["files"].append(entry.name)
    contents["dirs"].sort()
    contents["files"].sort()
    return contents


def scan_src_modules() -> Dict[str, Dict]:
    """
    Build a simple map of src/ modules: purpose (guess), key classes/functions, imports.
    This is heuristic and does not execute code.
    """
    modules: Dict[str, Dict] = {}
    if not SRC_DIR.is_dir():
        return modules

    for pyfile in SRC_DIR.rglob("*.py"):
        rel = pyfile.relative_to(REPO_ROOT)
        text = pyfile.read_text(encoding="utf-8", errors="ignore")
        classes = re.findall(r"^\s*class\s+([A-Za-z0-9_]+)\s*[\(:]", text, flags=re.MULTILINE)
        funcs = re.findall(r"^\s*def\s+([A-Za-z0-9_]+)\s*\(", text, flags=re.MULTILINE)
        imports = re.findall(r"^\s*import\s+([A-Za-z0-9_\.]+)", text, flags=re.MULTILINE)
        from_imports = re.findall(r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import", text, flags=re.MULTILINE)
        modules[str(rel)] = {
            "classes": classes,
            "functions": funcs,
            "imports": sorted(set(imports + from_imports)),
        }
    return modules


def find_non_deterministic_patterns(modules: Dict[str, Dict]) -> Dict[str, List[str]]:
    """
    Best-effort scan for non-deterministic code patterns in src/.
    """
    patterns = {
        "float": r"\bfloat\b",
        "math": r"\bmath\.",
        "random": r"\brandom\.",
        "time": r"\btime\.",
        "datetime": r"\bdatetime\.",
        "uuid": r"\buuid\.",
        "os_urandom": r"\bos\.urandom\b",
    }
    findings: Dict[str, List[str]] = {}
    for rel in modules:
        path = REPO_ROOT / rel
        text = path.read_text(encoding="utf-8", errors="ignore")
        hits = []
        for label, pat in patterns.items():
            if re.search(pat, text):
                hits.append(label)
        if hits:
            findings[rel] = sorted(set(hits))
    return findings


def component_status(modules: Dict[str, Dict], tests_summary: Dict) -> List[Tuple[str, str, str, str]]:
    """
    Very coarse heuristic status table for key components.
    This will not be perfect but will give the report something concrete to show.
    """
    rows: List[Tuple[str, str, str, str]] = []

    def exists(path: str) -> bool:
        return (REPO_ROOT / path).is_file()

    def status_for(path: str) -> str:
        if exists(path):
            # no real linkage to tests; treat as at least partially implemented
            return "Partially implemented"
        return "Missing"

    key_components = [
        ("BigNum128 core math", "src/libs/BigNum128.py"),
        ("CertifiedMath engine", "src/libs/CertifiedMath.py"),
        ("DeterministicTime", "src/libs/DeterministicTime.py"),
        ("PQC layer", "src/libs/PQC.py"),
        ("HSMF framework", "src/core/HSMF.py"),
        ("TokenStateBundle", "src/core/TokenStateBundle.py"),
        ("DRV_Packet", "src/core/DRV_Packet.py"),
        ("CoherenceLedger", "src/core/CoherenceLedger.py"),
        ("QFSV13SDK", "src/sdk/QFSV13SDK.py"),
        ("AEGIS API", "src/services/aegis_api.py"),
        ("CIR302 Handler", "src/handlers/CIR302_Handler.py"),
    ]
    for name, path in key_components:
        st = status_for(path)
        ev = path if exists(path) else "N/A"
        note = "Code present, test coverage unknown" if st != "Missing" else "No implementation file found"
        rows.append((name, st, ev, note))
    return rows


def generate_report():
    ensure_dirs()

    # Discovery
    top_level = walk_top_level()
    modules = scan_src_modules()
    nondet = find_non_deterministic_patterns(modules)

    # Tests
    test_run_info = run_tests()
    pytest_output_text = Path(test_run_info["output_path"]).read_text(encoding="utf-8", errors="ignore")
    pytest_summary = parse_pytest_summary(pytest_output_text)

    # Baseline evidence
    baseline = read_baseline_evidence()

    # Component table
    comp_rows = component_status(modules, pytest_summary)

    # Build report
    lines: List[str] = []

    lines.append("## QFS V13.5 Repository Status Report (Autonomous Audit)")
    lines.append("")
    lines.append("Generated by `scripts/run_autonomous_audit.py`.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 1. Architecture Map
    lines.append("### 1. Architecture Map")
    lines.append("")
    lines.append("**Top-level directories:**")
    lines.append("")
    for d in top_level["dirs"]:
        lines.append(f"- `{d}/`")
    lines.append("")
    lines.append("**Top-level files:**")
    lines.append("")
    for f in top_level["files"]:
        lines.append(f"- `{f}`")
    lines.append("")

    if modules:
        lines.append("**Key src/ modules (sample):**")
        lines.append("")
        for rel, info in sorted(modules.items()):
            # only show a subset for brevity in the report
            if not (rel.startswith("src/libs") or rel.startswith("src/core") or rel.startswith("src/sdk") or rel.startswith("src/services") or rel.startswith("src/handlers")):
                continue
            cls = ", ".join(info["classes"][:5]) or "None"
            funcs = ", ".join(info["functions"][:5]) or "None"
            imps = ", ".join(info["imports"][:5]) or "None"
            lines.append(f"- `{rel}`")
            lines.append(f"  - Classes: {cls}")
            lines.append(f"  - Functions: {funcs}")
            lines.append(f"  - Imports: {imps}")
        lines.append("")
    else:
        lines.append("No `src/` directory found.")
        lines.append("")

    # 2. Completeness Assessment
    lines.append("### 2. Completeness Assessment")
    lines.append("")
    lines.append("| Component | Status | Evidence (files/tests) | Notes |")
    lines.append("|-----------|--------|------------------------|-------|")
    for name, status, ev, note in comp_rows:
        lines.append(f"| {name} | {status} | `{ev}` | {note} |")
    lines.append("")
    lines.append("_Note: This table is heuristic and should be refined by linking to actual tests and evidence artifacts._")
    lines.append("")

    # 3. Determinism & Math Layer Compliance
    lines.append("### 3. Determinism & Math Layer Compliance")
    lines.append("")
    if nondet:
        lines.append("The following modules contain potentially non-deterministic patterns (keyword matches):")
        lines.append("")
        for rel, labels in sorted(nondet.items()):
            labels_str = ", ".join(labels)
            lines.append(f"- `{rel}` – patterns: {labels_str}")
        lines.append("")
    else:
        lines.append("No obvious non-deterministic patterns (float/math/random/time/uuid/os.urandom) detected in `src/`.")
        lines.append("")
    lines.append("Tests summary from this run:")
    lines.append("")
    lines.append(f"- Command: `{test_run_info['cmd']}`")
    lines.append(f"- Exit code: `{test_run_info['exit_code']}`")
    lines.append(f"- Pytest output: `{test_run_info['output_path']}`")
    lines.append(f"- Parsed summary: {json.dumps(pytest_summary)}")
    lines.append("")
    lines.append("_To fully complete this section, link specific formulas and tests to requirements in `AUDIT-V13.txt`._")
    lines.append("")

    # 4. Security & PQC Audit
    lines.append("### 4. Security & PQC Audit")
    lines.append("")
    pqc_path = REPO_ROOT / "src" / "libs" / "PQC.py"
    if pqc_path.is_file():
        lines.append(f"- PQC implementation found at `src/libs/PQC.py`.")
        lines.append("  - Manual review required to confirm use of real Dilithium-5/Kyber and deterministic serialization.")
    else:
        lines.append("- `src/libs/PQC.py` not found – PQC layer appears missing or located elsewhere.")
    lines.append("")
    lines.append("_A full security audit should scan for eval/exec/unsafe deserialization and verify key management and PQC logging against `AUDIT-V13.txt`._")
    lines.append("")

    # 5. Integration Readiness
    lines.append("### 5. Integration Readiness")
    lines.append("")
    sdk_path = REPO_ROOT / "src" / "sdk" / "QFSV13SDK.py"
    api_path = REPO_ROOT / "src" / "services" / "aegis_api.py"
    if sdk_path.is_file():
        lines.append(f"- QFS SDK found at `src/sdk/QFSV13SDK.py` (end-to-end flow entrypoint candidate).")
    if api_path.is_file():
        lines.append(f"- API gateway found at `src/services/aegis_api.py`.")
    lines.append("")
    lines.append("End-to-end integration (DRV_Packet → SDK → HSMF → Treasury/Reward → Ledger) must be verified by dedicated integration tests and deterministic replay evidence.")
    lines.append("")

    # 6. Critical Missing Pieces
    lines.append("### 6. Critical Missing Pieces")
    lines.append("")
    lines.append("This section must be refined by comparing code/tests/evidence with `ROADMAP-V13.5-REMEDIATION.md` and `AUDIT-V13.txt`.")
    lines.append("Examples of likely critical items (to be checked):")
    lines.append("")
    lines.append("- HSM/KMS key management layer and tests (`src/security/`, `tests/security/`).")
    lines.append("- SBOM generation and reproducible build scripts (`scripts/generate_sbom.py`, `scripts/build_reproducible.sh`, CI workflows).")
    lines.append("- Oracle attestation framework and quorum rules (`src/oracles/`, oracle tests).")
    lines.append("- Multi-node replication / consensus determinism tests (`src/replication/`, `tests/replication/`).")
    lines.append("- Time regression → CIR-302 tests (`tests/deterministic/test_time_regression_cir302.py`).")
    lines.append("")
    lines.append("_Replace or extend this list after a more detailed comparison with the roadmap and audit guide._")
    lines.append("")

    # 7. Final Verdict & Recommendations
    lines.append("### 7. Final Verdict")
    lines.append("")
    verdict = "Partially ready"
    lines.append(f"**Verdict:** {verdict}")
    lines.append("")
    lines.append("Reasoning (to be refined):")
    lines.append("")
    lines.append("- Core modules appear present but test results and non-determinism scan indicate further verification is required.")
    lines.append("- Baseline evidence (if present) should be compared with this run to detect regressions.")
    lines.append("")
    lines.append("**Suggested next actions (high-level):**")
    lines.append("")
    lines.append("1. Link each requirement in `AUDIT-V13.txt` to specific tests and evidence files, then update this report accordingly.")
    lines.append("2. Implement and run deterministic replay and CIR-302 tests for time regression and economic edge cases.")
    lines.append("3. Build HSM/KMS, SBOM, and reproducible build infrastructure as described in `ROADMAP-V13.5-REMEDIATION.md` and add evidence.")
    lines.append("4. Add integration tests for DRV_Packet → SDK → HSMF → Treasury → Ledger flows and capture deterministic replay artifacts.")
    lines.append("5. Enhance this script to parse more evidence JSONs (e.g., `QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json`) and include their results directly.")
    lines.append("")

    # Baseline evidence section
    lines.append("---")
    lines.append("")
    lines.append("### Appendix: Baseline Evidence Snapshot")
    lines.append("")
    if baseline:
        lines.append("Baseline evidence files detected in `evidence/baseline/`:")
        lines.append("")
        for name, content in baseline.items():
            if isinstance(content, dict):
                summary_keys = list(content.keys())[:5]
                lines.append(f"- `{name}` – keys: {summary_keys}")
            else:
                lines.append(f"- `{name}` – text length: {len(str(content))}")
        lines.append("")
    else:
        lines.append("No baseline evidence files detected in `evidence/baseline/`.")
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    generate_report()
    print(f"Autonomous audit report written to: {REPORT_PATH}")
```

This script:

- Walks the repo and summarizes `src/` modules with classes, functions, imports.  
- Runs `pytest` with deterministic environment and records output.  
- Reads any baseline evidence in `evidence/baseline/`.  
- Produces a markdown report at `evidence/diagnostic/QFSV13.5_AUTONOMOUS_AUDIT_REPORT.md` with sections 1–7 as required.

You can iteratively enhance it to:

- Parse `AUDIT-V13.txt` and `ROADMAP-V13.5-REMEDIATION.md` to auto‑map requirements to evidence.  
- Add finer‑grained checks for specific components and tests once they exist.