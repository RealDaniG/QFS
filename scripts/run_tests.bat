@echo off
REM QFS V13 Test Runner Script (Windows)

echo Running QFS V13 Test Suite...

REM Run unit tests
echo Running Unit Tests...
python -m pytest tests/unit/ -v

REM Run integration tests
echo Running Integration Tests...
python -m pytest tests/integration/ -v

REM Run deterministic tests
echo Running Deterministic Tests...
python -m pytest tests/deterministic/ -v

REM Run property-based tests
echo Running Property-Based Tests...
python -m pytest tests/property/ -v

echo All tests completed!