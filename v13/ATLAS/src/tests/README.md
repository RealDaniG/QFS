# Testing Guide

## Running Tests

To run the full test suite, ensure your `PYTHONPATH` includes the root of the repository (`.../V13`).

### Unit/Regression Tests (Backend)

```bash
# On Windows
$env:PYTHONPATH = "path\to\V13"
python -m pytest v13/atlas/src/tests
```

### End-to-End Tests (Frontend)

```bash
cd v13/atlas
npm run test:e2e
```

## Known Issues

- `test_routes_v18.py` may fail if the environment lacks `v15` or `src` in `PYTHONPATH`.
- Ensure `QFS_FORCE_MOCK_PQC=1` is set for dev/test environments.
