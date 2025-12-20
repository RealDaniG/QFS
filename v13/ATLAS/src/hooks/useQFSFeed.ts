
import { useState, useEffect } from 'react';
import { atlasFetch } from '../lib/api';

export interface FeedItem {
    id: string;
    cid: string;
    authorDID: string;
    content: {
        text: string;
        image?: string;
    };
    coherenceScore: number;
    proof: string; // Merkle root or signature
    timestamp: number;
}

export interface NetworkNode {
    nodeDID: string;
}

const NETWORK_NODES: NetworkNode[] = [
    { nodeDID: 'did:key:qfs_primary_01' },
    { nodeDID: 'did:key:qfs_primary_02' },
    { nodeDID: 'did:key:qfs_replica_01' }
];

export function useQFSFeed() {
    const [feed, setFeed] = useState<FeedItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedNode, setSelectedNode] = useState<NetworkNode>(NETWORK_NODES[0]);

    useEffect(() => {
        fetchFeed();
    }, [selectedNode]); // Re-fetch if node changes (logical simulation)

    const fetchFeed = async () => {
        setLoading(true);
        try {
            // Use atlasFetch to get real data from backend
            const res = await atlasFetch('/api/v18/content/feed?limit=20');
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            const data = await res.json();

            // Map Backend MessageSummary to Frontend FeedItem
            // Backend keys: id, channel_id, sender, content, content_hash, timestamp
            const items: FeedItem[] = data.map((msg: any) => ({
                id: msg.id,
                cid: msg.content_hash,
                authorDID: msg.sender,
                content: { text: msg.content },
                coherenceScore: 1.0, // Default for now
                proof: `ledger_${msg.content_hash.slice(0, 8)}`, // Simulated proof reference
                // Convert seconds (Backend) to milliseconds (JS)
                timestamp: msg.timestamp * 1000
            }));

            setFeed(items);
        } catch (err) {
            console.error('Failed to fetch QFS feed:', err);
            // On error, we might want to clear feed or show error
        } finally {
            setLoading(false);
        }
    };

    return {
        feed,
        loading,
        refresh: fetchFeed,
        nodes: NETWORK_NODES,
        selectedNode,
        selectNode: setSelectedNode
    };
}
