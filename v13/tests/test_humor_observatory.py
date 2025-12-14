"""
Tests for the humor observatory module
"""

import sys
import os
import pytest

from v13.policy.humor_observatory import HumorSignalObservatory, HumorSignalSnapshot


class TestHumorObservatory:
    """Test suite for the humor observatory"""
    
    def setup_method(self):
        """Setup test environment"""
        self.observatory = HumorSignalObservatory()
    
    def test_record_signal_and_get_report(self):
        """Test recording signals and generating reports"""
        # Create test snapshots
        snapshots = [
            HumorSignalSnapshot(
                timestamp=1000 + i,
                content_id=f"content_{i}",
                dimensions={
                    "chronos": 0.8 - i * 0.1,
                    "lexicon": 0.6 + i * 0.05,
                    "surreal": 0.4 + i * 0.02,
                    "empathy": 0.9 - i * 0.1,
                    "critique": 0.7 + i * 0.03,
                    "slapstick": 0.3 + i * 0.04,
                    "meta": 0.5 - i * 0.05
                },
                confidence=0.85 - i * 0.05,
                bonus_factor=0.2 - i * 0.02,
                policy_version="v1.0.0"
            )
            for i in range(5)
        ]
        
        # Record snapshots
        for snapshot in snapshots:
            self.observatory.record_signal(snapshot)
        
        # Generate report
        report = self.observatory.get_observability_report()
        
        # Verify report structure
        assert report.total_signals_processed == 5
        assert report.average_confidence > 0.0
        assert len(report.dimension_averages) == 7
        assert len(report.bonus_statistics) >= 4
        assert isinstance(report.top_performing_content, list)
    
    def test_empty_observatory_report(self):
        """Test report generation with no data"""
        report = self.observatory.get_observability_report()
        
        # Verify empty report structure
        assert report.total_signals_processed == 0
        assert report.average_confidence == 0.0
        assert report.dimension_averages == {}
        assert report.bonus_statistics == {}
        assert report.top_performing_content == []
    
    def test_histogram_calculation(self):
        """Test histogram distribution calculation"""
        # Add simple test data
        snapshot = HumorSignalSnapshot(
            timestamp=1000,
            content_id="test_content",
            dimensions={"chronos": 0.8, "lexicon": 0.6},
            confidence=0.85,
            bonus_factor=0.2,
            policy_version="v1.0.0"
        )
        
        self.observatory.record_signal(snapshot)
        
        # Get report which should include distributions
        report = self.observatory.get_observability_report()
        
        # Verify distributions exist
        assert "chronos" in report.dimension_distributions
        assert "lexicon" in report.dimension_distributions
        assert isinstance(report.dimension_distributions["chronos"], dict)
    
    def test_dimension_correlations(self):
        """Test dimension correlation calculation"""
        # Add test data with clear correlations
        snapshots = [
            HumorSignalSnapshot(
                timestamp=1000 + i,
                content_id=f"content_{i}",
                dimensions={
                    "chronos": 0.5 + i * 0.1,
                    "lexicon": 0.5 + i * 0.1,  # Perfect positive correlation with chronos
                    "surreal": 0.5 - i * 0.1    # Perfect negative correlation with chronos
                },
                confidence=0.8,
                bonus_factor=0.1 + i * 0.02,
                policy_version="v1.0.0"
            )
            for i in range(10)
        ]
        
        # Record snapshots
        for snapshot in snapshots:
            self.observatory.record_signal(snapshot)
        
        # Calculate correlations
        correlations = self.observatory.get_dimension_correlations()
        
        # Verify correlations exist
        assert "chronos" in correlations
        assert "lexicon" in correlations["chronos"]
        assert "surreal" in correlations["chronos"]
        
        # Note: Actual correlation values would need more precise testing
        # but we're mainly testing that the structure works
    
    def test_top_performing_content(self):
        """Test top performing content identification"""
        # Add test data with varying bonus factors
        snapshots = [
            HumorSignalSnapshot(
                timestamp=1000 + i,
                content_id=f"content_{i}",
                dimensions={"chronos": 0.5, "lexicon": 0.5},
                confidence=0.8,
                bonus_factor=0.1 + i * 0.05,  # Increasing bonus factors
                policy_version="v1.0.0"
            )
            for i in range(10)
        ]
        
        # Record snapshots
        for snapshot in snapshots:
            self.observatory.record_signal(snapshot)
        
        # Get report
        report = self.observatory.get_observability_report()
        
        # Verify top performing content
        assert len(report.top_performing_content) <= 10
        if len(report.top_performing_content) > 1:
            # Check that content is sorted by bonus factor (descending)
            for i in range(len(report.top_performing_content) - 1):
                assert report.top_performing_content[i]["bonus_factor"] >= report.top_performing_content[i + 1]["bonus_factor"]
    
    def test_export_observability_data(self):
        """Test export of observability data"""
        # Add test data
        snapshot = HumorSignalSnapshot(
            timestamp=1000,
            content_id="test_content",
            dimensions={"chronos": 0.8, "lexicon": 0.6},
            confidence=0.85,
            bonus_factor=0.2,
            policy_version="v1.0.0"
        )
        
        self.observatory.record_signal(snapshot)
        
        # Export data
        export_data = self.observatory.export_observability_data()
        
        # Verify export structure
        assert "report" in export_data
        assert "dimension_distributions" in export_data
        assert "top_performing_content" in export_data
        assert "correlations" in export_data
        assert "raw_data_sample" in export_data
        
        # Verify report data
        assert "total_signals_processed" in export_data["report"]
        assert "average_confidence" in export_data["report"]
        assert "dimension_averages" in export_data["report"]


if __name__ == "__main__":
    pytest.main([__file__])