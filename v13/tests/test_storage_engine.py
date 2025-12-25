"""
Tests for the StorageEngine implementation
"""

from libs.deterministic_helpers import (
    ZeroSimAbort,
    det_time_now,
    det_perf_counter,
    det_random,
    qnum,
)
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))
from StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath, BigNum128


class TestStorageEngine:
    """Test suite for StorageEngine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.cm = CertifiedMath()
        self.storage_engine = StorageEngine(self.cm)
        self.storage_engine.register_storage_node("node1", "192.168.1.1", 8080)
        self.storage_engine.register_storage_node("node2", "192.168.1.2", 8080)
        self.storage_engine.register_storage_node("node3", "192.168.1.3", 8080)
        self.storage_engine.register_storage_node("node4", "192.168.1.4", 8080)

    def test_register_storage_node(self):
        """Test registering storage nodes"""
        assert len(self.storage_engine.nodes) == 4
        assert "node1" in self.storage_engine.nodes
        assert self.storage_engine.nodes["node1"].host == "192.168.1.1"
        assert self.storage_engine.nodes["node1"].port == 8080

    def test_get_eligible_nodes(self):
        """Test getting eligible nodes"""
        eligible_nodes = self.storage_engine.get_eligible_nodes()
        assert len(eligible_nodes) == 4
        assert eligible_nodes == sorted(eligible_nodes)

    def test_put_content(self):
        """Test putting content"""
        object_id = "test_object_1"
        version = 1
        content = b"This is test content for storage engine testing."
        metadata = {"author": "test_user", "tags": ["test"], "created_at": "2025-12-14"}
        result = self.storage_engine.put_content(
            object_id, version, content, metadata, 1234567890
        )
        assert "hash_commit" in result
        assert "shard_ids" in result
        assert len(result["shard_ids"]) > 0
        object_key = f"{object_id}:{version}"
        assert object_key in self.storage_engine.objects
        for shard_id in result["shard_ids"]:
            assert shard_id in self.storage_engine.shards

    def test_get_content(self):
        """Test getting content"""
        object_id = "test_object_2"
        version = 1
        content = b"Another test content for retrieval testing."
        metadata = {"author": "test_user"}
        self.storage_engine.put_content(
            object_id, version, content, metadata, 1234567891
        )
        retrieved = self.storage_engine.get_content(object_id, version)
        assert retrieved["content_chunk"] == content
        assert "hash_commit" in retrieved
        assert "proofs" in retrieved

    def test_get_storage_proof(self):
        """Test getting storage proof"""
        object_id = "test_object_3"
        version = 1
        content = b"Content for proof testing."
        metadata = {"author": "test_user"}
        result = self.storage_engine.put_content(
            object_id, version, content, metadata, 1234567892
        )
        if result["shard_ids"]:
            shard_id = result["shard_ids"][0]
            proof = self.storage_engine.get_storage_proof(object_id, version, shard_id)
            assert "merkle_root" in proof
            assert "proof" in proof
            assert "assigned_nodes" in proof
            assert len(proof["assigned_nodes"]) == 3

    def test_list_objects(self):
        """Test listing objects"""
        content1 = b"First test object"
        metadata1 = {"author": "user1", "category": "test"}
        self.storage_engine.put_content("obj1", 1, content1, metadata1, 1234567893)
        content2 = b"Second test object"
        metadata2 = {"author": "user2", "category": "test"}
        self.storage_engine.put_content("obj2", 1, content2, metadata2, 1234567894)
        objects = self.storage_engine.list_objects()
        assert len(objects) == 2
        filtered_objects = self.storage_engine.list_objects({"category": "test"})
        assert len(filtered_objects) == 2
        filtered_objects = self.storage_engine.list_objects({"author": "user1"})
        assert len(filtered_objects) == 1
        assert filtered_objects[0]["object_id"] == "obj1"

    def test_deterministic_shard_assignment(self):
        """Test that shard assignment is deterministic"""
        object_id = "deterministic_test"
        version = 1
        content = b"Deterministic test content" * 100
        metadata = {"test": "deterministic"}
        result1 = self.storage_engine.put_content(
            object_id, version, content, metadata, 1234567895
        )
        result2 = self.storage_engine.put_content(
            object_id, version, content, metadata, 1234567895
        )
        assert result1["hash_commit"] == result2["hash_commit"]
        assert result1["shard_ids"] == result2["shard_ids"]

    def test_node_metrics_update(self):
        """Test that node metrics are updated correctly"""
        object_id = "metrics_test"
        version = 1
        content = b"Metrics test content"
        metadata = {"test": "metrics"}
        result = self.storage_engine.put_content(
            object_id, version, content, metadata, 1234567896
        )
        assert len(result["shard_ids"]) > 0
        shard_id = result["shard_ids"][0]
        assigned_nodes = self.storage_engine.shards[shard_id].assigned_nodes
        updated_node_found = False
        for node_id in sorted(assigned_nodes):
            if node_id in self.storage_engine.nodes:
                final_bytes = self.storage_engine.nodes[node_id].bytes_stored
                if final_bytes.value > 0:
                    updated_node_found = True
                    break
        assert updated_node_found, (
            f"No assigned nodes ({assigned_nodes}) had updated metrics"
        )


class TestStorageEngineDeterminism:
    """Test suite for StorageEngine determinism"""

    def setup_method(self):
        """Set up test fixtures"""
        self.cm = CertifiedMath()
        self.storage_engine = StorageEngine(self.cm)
        self.storage_engine.register_storage_node("node1", "192.168.1.1", 8080)
        self.storage_engine.register_storage_node("node2", "192.168.1.2", 8080)
        self.storage_engine.register_storage_node("node3", "192.168.1.3", 8080)
        self.storage_engine.register_storage_node("node4", "192.168.1.4", 8080)

    def test_deterministic_content_hash(self):
        """Test that content hashing is deterministic"""
        content = b"Test content for hashing"
        metadata = {"author": "test_user", "timestamp": "1234567890"}
        hash1 = self.storage_engine._compute_content_hash(content, metadata)
        hash2 = self.storage_engine._compute_content_hash(content, metadata)
        assert hash1 == hash2

    def test_deterministic_shard_id(self):
        """Test that shard ID computation is deterministic"""
        shard_id1 = self.storage_engine._compute_shard_id("test_object", 1, 0)
        shard_id2 = self.storage_engine._compute_shard_id("test_object", 1, 0)
        assert shard_id1 == shard_id2

    def test_deterministic_node_assignment(self):
        """Test that node assignment is deterministic"""
        shard_id = "test_shard_123"
        nodes1 = self.storage_engine._assign_nodes_to_shard(shard_id)
        nodes2 = self.storage_engine._assign_nodes_to_shard(shard_id)
        assert nodes1 == nodes2
        assert len(nodes1) == 3


class TestStorageEngineAEGISIntegration:
    """Test suite for StorageEngine AEGIS integration"""

    def setup_method(self):
        """Set up test fixtures"""
        self.cm = CertifiedMath()
        self.storage_engine = StorageEngine(self.cm)
        self.registry_snapshot = {
            "schema_version": "v1.0",
            "nodes": {
                "node_valid": {
                    "pqc_public_key": "0x1234567890abcdef",
                    "pqc_scheme": "Dilithium5",
                    "revoked": False,
                },
                "node_revoked": {
                    "pqc_public_key": "0xabcdef123456",
                    "pqc_scheme": "Dilithium5",
                    "revoked": True,
                    "revocation_reason": "Security violation",
                },
            },
        }
        self.telemetry_snapshot = {
            "schema_version": "v1.0",
            "telemetry_hash": "a" * 64,
            "block_height": 12345,
            "nodes": {
                "node_valid": {
                    "uptime_ratio": "0.95",
                    "health_score": "0.80",
                    "conflict_detected": False,
                },
                "node_revoked": {
                    "uptime_ratio": "0.95",
                    "health_score": "0.80",
                    "conflict_detected": False,
                },
            },
        }

    def test_node_registration_without_aegis(self):
        """Test node registration without AEGIS context"""
        result = self.storage_engine.register_storage_node(
            "test_node", "192.168.1.10", 8080
        )
        assert result == True
        assert "test_node" in self.storage_engine.nodes
        assert self.storage_engine.nodes["test_node"].is_aegis_verified == False

    def test_node_registration_with_aegis(self):
        """Test node registration with AEGIS context"""
        self.storage_engine.set_aegis_context(
            self.registry_snapshot, self.telemetry_snapshot
        )
        result = self.storage_engine.register_storage_node(
            "node_valid", "192.168.1.11", 8080
        )
        assert result == True
        assert "node_valid" in self.storage_engine.nodes
        assert self.storage_engine.nodes["node_valid"].is_aegis_verified == True

    def test_node_eligibility_without_aegis(self):
        """Test node eligibility without AEGIS context"""
        self.storage_engine.register_storage_node("node_a", "192.168.1.10", 8080)
        self.storage_engine.register_storage_node("node_b", "192.168.1.11", 8080)
        eligible_nodes = self.storage_engine.get_eligible_nodes()
        assert "node_a" in eligible_nodes
        assert "node_b" in eligible_nodes

    def test_node_eligibility_with_aegis(self):
        """Test node eligibility with AEGIS context"""
        self.storage_engine.set_aegis_context(
            self.registry_snapshot, self.telemetry_snapshot
        )
        self.storage_engine.register_storage_node("node_valid", "192.168.1.10", 8080)
        self.storage_engine.register_storage_node("node_revoked", "192.168.1.11", 8080)
        eligible_nodes = self.storage_engine.get_eligible_nodes()
        assert "node_valid" in eligible_nodes
        assert "node_revoked" not in eligible_nodes

    def test_epoch_advancement(self):
        """Test epoch advancement and node re-verification"""
        self.storage_engine.set_aegis_context(
            self.registry_snapshot, self.telemetry_snapshot
        )
        self.storage_engine.register_storage_node("node_valid", "192.168.1.10", 8080)
        assert self.storage_engine.current_epoch == 0
        assert self.storage_engine.nodes["node_valid"].aegis_verification_epoch == 0
        self.storage_engine.advance_epoch(1)
        assert self.storage_engine.current_epoch == 1
        assert self.storage_engine.nodes["node_valid"].aegis_verification_epoch == 1

    def test_node_unregistration(self):
        """Test node unregistration"""
        self.storage_engine.register_storage_node("test_node", "192.168.1.10", 8080)
        assert "test_node" in self.storage_engine.nodes
        result = self.storage_engine.unregister_storage_node("test_node")
        assert result == True
        assert "test_node" not in self.storage_engine.nodes
        result = self.storage_engine.unregister_storage_node("nonexistent_node")
        assert result == False

    def test_node_status_management(self):
        """Test node status management"""
        self.storage_engine.register_storage_node("test_node", "192.168.1.10", 8080)
        assert self.storage_engine.nodes["test_node"].status == "active"
        result = self.storage_engine.set_node_status("test_node", "inactive")
        assert result == True
        assert self.storage_engine.nodes["test_node"].status == "inactive"
        result = self.storage_engine.set_node_status("nonexistent_node", "inactive")
        assert result == False


class TestStorageEngineEconomics:
    """Test suite for StorageEngine economics functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        from v13.libs.CertifiedMath import CertifiedMath

        self.cm = CertifiedMath()
        self.storage_engine = StorageEngine(self.cm)
        self.storage_engine.register_storage_node("node1", "192.168.1.1", 8080)
        self.storage_engine.register_storage_node("node2", "192.168.1.2", 8080)
        self.storage_engine.register_storage_node("node3", "192.168.1.3", 8080)
        self.storage_engine.register_storage_node("node4", "192.168.1.4", 8080)
        for node_id in sorted(self.storage_engine.nodes):
            self.storage_engine.nodes[node_id].is_aegis_verified = True
            self.storage_engine.nodes[node_id].aegis_verification_epoch = 0

    def test_atr_storage_cost_calculation(self):
        """Test ATR storage cost calculation"""
        content = b"Simple test content"
        metadata = {"author": "test_user"}
        cost = self.storage_engine._calculate_atr_storage_cost(len(content), metadata)
        assert isinstance(cost, BigNum128)
        assert cost.value > 0
        large_content = b"Larger test content" * 100
        large_metadata = {"author": "test_user", "tags": ["test", "large"]}
        large_cost = self.storage_engine._calculate_atr_storage_cost(
            len(large_content), large_metadata
        )
        assert isinstance(large_cost, BigNum128)
        assert large_cost.value > cost.value

    def test_put_content_with_atr_cost(self):
        """Test putting content includes ATR cost calculation"""
        object_id = "test_object_economics"
        version = 1
        content = b"Economics test content"
        metadata = {"author": "test_user", "category": "economics"}
        result = self.storage_engine.put_content(
            object_id, version, content, metadata, 1234567890
        )
        assert "atr_cost" in result
        assert qnum(result["atr_cost"]) > 0
        assert self.storage_engine.total_atr_fees_collected.value > 0

    def test_nod_reward_calculation(self):
        """Test NOD reward calculation"""
        self.storage_engine.nodes["node1"].bytes_stored = BigNum128.from_int(1000000)
        self.storage_engine.nodes["node1"].uptime_bucket = 5
        self.storage_engine.nodes["node1"].proofs_verified = 10
        self.storage_engine.nodes["node2"].bytes_stored = BigNum128.from_int(2000000)
        self.storage_engine.nodes["node2"].uptime_bucket = 8
        self.storage_engine.nodes["node2"].proofs_verified = 15
        nod_rewards = self.storage_engine.calculate_nod_rewards(0)
        assert "node1" in nod_rewards
        assert "node2" in nod_rewards
        assert isinstance(nod_rewards["node1"], BigNum128)
        assert isinstance(nod_rewards["node2"], BigNum128)
        assert nod_rewards["node2"].value > nod_rewards["node1"].value

    def test_storage_economics_summary(self):
        """Test storage economics summary and conservation checks"""
        object_id = "test_object_conservation"
        version = 1
        content = b"Conservation test content" * 100
        metadata = {"author": "test_user"}
        self.storage_engine.put_content(
            object_id, version, content, metadata, 1234567890
        )
        self.storage_engine.nodes["node1"].bytes_stored = BigNum128.from_int(1000)
        self.storage_engine.nodes["node1"].uptime_bucket = 1
        self.storage_engine.nodes["node1"].proofs_verified = 1
        nod_rewards = self.storage_engine.calculate_nod_rewards(0)
        summary = self.storage_engine.get_storage_economics_summary()
        assert "total_atr_fees_collected" in summary
        assert "total_nod_rewards_distributed" in summary
        assert "conservation_difference" in summary
        assert "is_conservation_maintained" in summary
        assert "storage_event_count" in summary
        assert summary["is_conservation_maintained"] == True
        assert summary["storage_event_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
