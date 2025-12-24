import pytest
import json
import os
import sys
from io import StringIO
from unittest.mock import patch

# Add tool path to sys.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tools/github"))
)

import github_import_contributions


def test_importer_determinism(tmp_path):
    """
    Verify that the importer produces identical output for identical inputs.
    """
    output_file_1 = tmp_path / "ledger1.json"
    output_file_2 = tmp_path / "ledger2.json"

    # Mock args
    username = "testuser"
    repo = "testauth/repo"

    # Run 1
    with patch(
        "sys.argv",
        [
            "script",
            "--username",
            username,
            "--repo",
            repo,
            "--output",
            str(output_file_1),
        ],
    ):
        github_import_contributions.main()

    # Run 2
    with patch(
        "sys.argv",
        [
            "script",
            "--username",
            username,
            "--repo",
            repo,
            "--output",
            str(output_file_2),
        ],
    ):
        github_import_contributions.main()

    # Compare files
    with open(output_file_1, "r") as f1, open(output_file_2, "r") as f2:
        content1 = f1.read()
        content2 = f2.read()

    assert content1 == content2

    # Verify Content Structure
    data = json.loads(content1)
    assert data["username"] == username
    assert data["repo"] == repo
    assert "ledger_hash" in data
    assert data["importer_version"] == "0.1.0"
    assert data["generated_at_sequence"] == 0
