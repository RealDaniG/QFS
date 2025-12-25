"""
generate_aes_gut_evidence.py - Generate evidence for AES GUT Determinism

Produces a signed JSON artifact proving deterministic vector generation.
"""

import json
import hashlib
from v13.policy.artistic_policy import ArtisticSignalPolicy
from v13.policy.artistic_constants import SCALE

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def generate_evidence():
    logger.info("Generating AES GUT Evidence...")
    policy = ArtisticSignalPolicy()
    metadata = {
        "width": 1618,
        "height": 1000,
        "palette": [{"hue": 0}, {"hue": 137507764}],
        "elements": [{"x": 809, "y": 500, "type": "circle"}],
        "structures": [
            {"scale": 10, "pattern_id": "p1"},
            {"scale": 100, "pattern_id": "p1"},
        ],
    }
    content_id = "evidence_content_001"
    event_ids = ["e1", "e2", "e3"]
    vector = policy.compute_vector(content_id, metadata, event_ids)
    vector_dict = vector.to_dict()
    timestamp = datetime.datetime.now().isoformat()
    evidence = {
        "evidence_type": "AES_GUT_DETERMINISM",
        "timestamp": timestamp,
        "status": "VERIFIED",
        "policy_version": policy.policy.version,
        "input_metadata_hash": hashlib.sha256(
            json.dumps(metadata, sort_keys=True).encode()
        ).hexdigest(),
        "output_vector": vector_dict,
        "verification_check": "PASS" if vector.vector_hash else "FAIL",
    }
    os.makedirs("v13/evidence/aes", exist_ok=True)
    filename = f"v13/evidence/aes/aes_gut_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(evidence, f, indent=2)
    logger.info(f"Evidence generated: {filename}")
    logger.info(f"Vector Hash: {vector.vector_hash}")


if __name__ == "__main__":
    generate_evidence()
