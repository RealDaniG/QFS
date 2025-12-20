"""
Metrics API endpoints for the ATLAS system.

Provides Prometheus-compatible monitoring endpoints and storage metrics.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from ..dependencies import get_qfs_client_dependency
from ...qfs_client import QFSClient
logger = logging.getLogger(__name__)
router = APIRouter(prefix='/metrics', tags=['metrics'])

def get_storage_engine():
    """Get storage engine instance."""
    try:
        from v13.libs.CertifiedMath import CertifiedMath
        from v13.core.StorageEngine import StorageEngine
    except Exception as e:
        raise RuntimeError(f'StorageEngine not available in this environment: {e}')
    cm = CertifiedMath()
    storage_engine = StorageEngine(cm)
    return storage_engine

@router.get('/storage')
async def get_storage_metrics():
    """
    Get storage engine metrics.
    
    Returns:
        Dict with storage metrics including node counts, object counts, etc.
    """
    try:
        storage_engine = get_storage_engine()
        metrics = {'nodes_registered': len(storage_engine.nodes), 'objects_stored': len(storage_engine.objects), 'shards_created': len(storage_engine.shards), 'eligible_nodes': len(storage_engine.get_eligible_nodes()), 'current_epoch': storage_engine.current_epoch, 'total_atr_fees_collected': str(storage_engine.total_atr_fees_collected.value) if hasattr(storage_engine, 'total_atr_fees_collected') else '0', 'total_nod_rewards_distributed': str(storage_engine.total_nod_rewards_distributed.value) if hasattr(storage_engine, 'total_nod_rewards_distributed') else '0', 'storage_events_logged': len(storage_engine.storage_event_log) if hasattr(storage_engine, 'storage_event_log') else 0}
        return metrics
    except Exception as e:
        logger.error(f'Error retrieving storage metrics: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to retrieve storage metrics')

@router.get('/storage/nodes')
async def get_storage_node_metrics():
    """
    Get detailed metrics for all storage nodes.
    
    Returns:
        Dict with node-specific metrics
    """
    try:
        storage_engine = get_storage_engine()
        node_metrics = {}
        for node_id, node in storage_engine.nodes.items():
            node_metrics[node_id] = {'host': node.host, 'port': node.port, 'status': node.status, 'is_aegis_verified': node.is_aegis_verified, 'aegis_verification_epoch': node.aegis_verification_epoch, 'bytes_stored': str(node.bytes_stored.value) if hasattr(node, 'bytes_stored') else '0', 'uptime_bucket': node.uptime_bucket, 'proofs_verified': node.proofs_verified}
        return {'nodes': node_metrics, 'total_nodes': len(node_metrics)}
    except Exception as e:
        logger.error(f'Error retrieving node metrics: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to retrieve node metrics')

@router.get('/storage/economics')
async def get_storage_economics_summary():
    """
    Get storage economics summary.
    
    Returns:
        Dict with economics metrics including ATR fees, NOD rewards, conservation status
    """
    try:
        storage_engine = get_storage_engine()
        if hasattr(storage_engine, 'get_storage_economics_summary'):
            summary = storage_engine.get_storage_economics_summary()
        else:
            summary = {'total_atr_fees_collected': '0', 'total_nod_rewards_distributed': '0', 'conservation_difference': '0', 'is_conservation_maintained': True, 'storage_event_count': 0}
        return summary
    except Exception as e:
        logger.error(f'Error retrieving economics metrics: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to retrieve economics metrics')

@router.get('/prometheus')
async def get_prometheus_metrics():
    """
    Get Prometheus-compatible metrics.
    
    Returns:
        Plain text metrics in Prometheus format
    """
    try:
        storage_engine = get_storage_engine()
        node_count = len(storage_engine.nodes)
        object_count = len(storage_engine.objects)
        shard_count = len(storage_engine.shards)
        eligible_node_count = len(storage_engine.get_eligible_nodes())
        metrics_lines = ['# HELP qfs_storage_nodes_registered Total number of registered storage nodes', '# TYPE qfs_storage_nodes_registered gauge', f'qfs_storage_nodes_registered {node_count}', '', '# HELP qfs_storage_objects_stored Total number of stored objects', '# TYPE qfs_storage_objects_stored gauge', f'qfs_storage_objects_stored {object_count}', '', '# HELP qfs_storage_shards_created Total number of created shards', '# TYPE qfs_storage_shards_created gauge', f'qfs_storage_shards_created {shard_count}', '', '# HELP qfs_storage_eligible_nodes Number of eligible storage nodes', '# TYPE qfs_storage_eligible_nodes gauge', f'qfs_storage_eligible_nodes {eligible_node_count}', '', '# HELP qfs_storage_current_epoch Current storage epoch', '# TYPE qfs_storage_current_epoch gauge', f'qfs_storage_current_epoch {storage_engine.current_epoch}']
        return '\n'.join(metrics_lines)
    except Exception as e:
        logger.error(f'Error generating Prometheus metrics: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to generate Prometheus metrics')