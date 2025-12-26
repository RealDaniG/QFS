"""
Device Fingerprinting - Coarse, Deterministic, Low-Entropy
Used for device binding, NOT tracking.
"""

import hashlib
from typing import Tuple


def compute_device_hash(os_family: str, cpu_arch: str, app_uuid: str) -> str:
    """
    Compute deterministic device hash from coarse attributes.

    Args:
        os_family: Coarse OS family (e.g., "Windows", "Darwin", "Linux")
        cpu_arch: CPU architecture (e.g., "x86_64", "arm64")
        app_uuid: Application install UUID (stable per install)

    Returns:
        64-character hex device hash

    Privacy Note:
        Uses only coarse-grained, non-PII data.
        Hash is deterministic but not reversible.
    """
    # Normalize inputs
    os_family = os_family.lower().strip()
    cpu_arch = cpu_arch.lower().strip()
    app_uuid = app_uuid.strip()

    # Construct deterministic input
    input_data = f"{os_family}|{cpu_arch}|{app_uuid}"

    # BLAKE3 for speed (or SHA3-256 for consistency)
    # Using SHA3 for consistency with rest of codebase
    device_hash = hashlib.sha3_256(input_data.encode("utf-8")).hexdigest()

    return device_hash


def get_device_info() -> Tuple[str, str, str]:
    """
    Gather device information for hashing.

    Returns:
        (os_family, cpu_arch, app_uuid)
    """
    import platform
    import uuid
    import os

    # OS family
    os_family = platform.system()

    # CPU architecture
    cpu_arch = platform.machine()

    # App UUID (persistent per install)
    # For now, use a node-specific identifier
    # In production, this should be stored in config/evidence
    app_uuid_file = os.path.join(os.path.expanduser("~"), ".qfs_app_uuid")

    if os.path.exists(app_uuid_file):
        with open(app_uuid_file, "r", encoding="utf-8") as f:
            app_uuid = f.read().strip()
    else:
        app_uuid = str(uuid.uuid4())
        with open(app_uuid_file, "w", encoding="utf-8") as f:
            f.write(app_uuid)

    return (os_family, cpu_arch, app_uuid)
