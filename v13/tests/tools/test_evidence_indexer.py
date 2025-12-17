"""
Tests for the Evidence Indexer tool
"""
import json
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
from evidence_indexer import EvidenceIndexer

class TestEvidenceIndexer:
    """Test suite for EvidenceIndexer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.evidence_dir = os.path.join(self.test_dir, 'evidence')
        os.makedirs(self.evidence_dir)
        self._create_test_evidence_files()

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    def _create_test_evidence_files(self):
        """Create test evidence files"""
        phase1_dir = os.path.join(self.evidence_dir, 'phase1')
        os.makedirs(phase1_dir)
        with open(os.path.join(phase1_dir, 'test_evidence.json'), 'w') as f:
            json.dump({'test': 'data'}, f)
        with open(os.path.join(phase1_dir, 'test_report.md'), 'w') as f:
            f.write('# Test Report\n\nThis is a test report.')
        storage_dir = os.path.join(self.evidence_dir, 'storage')
        os.makedirs(storage_dir)
        with open(os.path.join(storage_dir, 'storage_metrics.json'), 'w') as f:
            json.dump({'metrics': 'data'}, f)
        with open(os.path.join(storage_dir, 'storage_summary.txt'), 'w') as f:
            f.write('Storage summary')

    def test_initialize_indexer(self):
        """Test that EvidenceIndexer initializes correctly"""
        indexer = EvidenceIndexer([self.evidence_dir])
        assert indexer.evidence_dirs == [self.evidence_dir]
        assert indexer.output_dir == 'docs/evidence'
        assert 'metadata' in indexer.index
        assert 'artifacts' in indexer.index
        assert 'summary' in indexer.index

    def test_scan_evidence_directories(self):
        """Test that evidence directories are scanned correctly"""
        indexer = EvidenceIndexer([self.evidence_dir])
        artifacts = indexer.scan_evidence_directories()
        assert len(artifacts) == 4
        artifact_names = [artifact['name'] for artifact in artifacts]
        assert 'test_evidence.json' in artifact_names
        assert 'test_report.md' in artifact_names
        assert 'storage_metrics.json' in artifact_names
        assert 'storage_summary.txt' in artifact_names

    def test_process_artifact(self):
        """Test that individual artifacts are processed correctly"""
        indexer = EvidenceIndexer([self.evidence_dir])
        test_file = Path(self.evidence_dir) / 'phase1' / 'test_evidence.json'
        artifact = indexer._process_artifact(test_file, self.evidence_dir)
        assert artifact is not None
        assert artifact['name'] == 'test_evidence.json'
        assert artifact['path'] == 'phase1/test_evidence.json'
        assert artifact['type'] == 'json'
        assert artifact['size_bytes'] > 0
        assert 'sha256_hash' in artifact
        assert 'component' in artifact
        assert 'phase' in artifact

    def test_calculate_file_hash(self):
        """Test that file hashes are calculated correctly"""
        indexer = EvidenceIndexer([self.evidence_dir])
        test_file = Path(self.evidence_dir) / 'phase1' / 'test_evidence.json'
        file_hash = indexer._calculate_file_hash(test_file)
        assert file_hash != 'ERROR_CALCULATING_HASH'
        assert len(file_hash) == 64
        assert all((c in '0123456789abcdef' for c in file_hash))

    def test_extract_tags_from_filename(self):
        """Test that tags are extracted from filenames correctly"""
        indexer = EvidenceIndexer([self.evidence_dir])
        assert 'test' in indexer._extract_tags_from_filename('test_evidence.json')
        assert 'report' in indexer._extract_tags_from_filename('phase1_final_report.md')
        assert 'evidence' in indexer._extract_tags_from_filename('storage_evidence.json')
        assert 'summary' in indexer._extract_tags_from_filename('performance_summary.txt')

    def test_generate_index(self):
        """Test that the complete index is generated correctly"""
        indexer = EvidenceIndexer([self.evidence_dir])
        index = indexer.generate_index()
        assert 'metadata' in index
        assert 'artifacts' in index
        assert 'summary' in index
        assert len(index['artifacts']) == 4
        assert index['summary']['total_artifacts'] == 4
        assert len(index['summary']['by_type']) > 0
        assert len(index['summary']['by_phase']) > 0

    def test_save_index(self):
        """Test that the index is saved correctly"""
        indexer = EvidenceIndexer([self.evidence_dir], self.test_dir)
        indexer.generate_index()
        output_path = indexer.save_index()
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            saved_index = json.load(f)
        assert 'metadata' in saved_index
        assert 'artifacts' in saved_index
        assert 'summary' in saved_index
        assert saved_index['summary']['total_artifacts'] == 4

def test_evidence_indexer():
    """Test the EvidenceIndexer implementation"""
    print('Testing EvidenceIndexer...')
    test_instance = TestEvidenceIndexer()
    test_instance.setup_method()
    try:
        test_instance.test_initialize_indexer()
        print('✓ test_initialize_indexer passed')
    finally:
        test_instance.teardown_method()
    test_instance.setup_method()
    try:
        test_instance.test_scan_evidence_directories()
        print('✓ test_scan_evidence_directories passed')
    finally:
        test_instance.teardown_method()
    test_instance.setup_method()
    try:
        test_instance.test_process_artifact()
        print('✓ test_process_artifact passed')
    finally:
        test_instance.teardown_method()
    test_instance.setup_method()
    try:
        test_instance.test_calculate_file_hash()
        print('✓ test_calculate_file_hash passed')
    finally:
        test_instance.teardown_method()
    test_instance.setup_method()
    try:
        test_instance.test_extract_tags_from_filename()
        print('✓ test_extract_tags_from_filename passed')
    finally:
        test_instance.teardown_method()
    test_instance.setup_method()
    try:
        test_instance.test_generate_index()
        print('✓ test_generate_index passed')
    finally:
        test_instance.teardown_method()
    test_instance.setup_method()
    try:
        test_instance.test_save_index()
        print('✓ test_save_index passed')
    finally:
        test_instance.teardown_method()
    print('EvidenceIndexer tests completed successfully')
if __name__ == '__main__':
    test_evidence_indexer()