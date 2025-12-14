
import { useState, useEffect } from 'react';
import { QFSExecutor } from '@/lib/qfs/executor';

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

// Mock distributed nodes
const NETWORK_NODES = [
    new QFSExecutor('did:key:node_1'),
    new QFSExecutor('did:key:node_2'),
    new QFSExecutor('did:key:node_3')
];

export function useQFSFeed() {
    const [feed, setFeed] = useState<FeedItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedNode, setSelectedNode] = useState(NETWORK_NODES[0]);

    useEffect(() => {
        fetchFeed();
    }, [selectedNode]);

    const fetchFeed = async () => {
        setLoading(true);
        try {
            // In a real implementation, we would query the node's API
            // Here we simulate the node "computing" the feed

            // Mock data - in real version this comes from IPFS + Ledger + QFS sort
            const mockRawData = [
                { id: '1', author: 'did:key:alice', text: 'Decentralized AI is the future.' },
                { id: '2', author: 'did:key:bob', text: 'Just setup my QFS node! #Atlas' },
                { id: '3', author: 'did:key:charlie', text: 'Governance proposal #12 is live, go vote!' }
            ];

            const computedFeed = await Promise.all(mockRawData.map(async (item) => {
                const task = {
                    taskId: `score_${item.id}`,
                    type: 'coherence_scoring',
                    dataCID: `cid_${item.id}`,
                    policyVersion: 'v0.0.1'
                };

                // Executor computes score and proof
                const result = await selectedNode.executeTask(task as any, item);

                return {
                    id: item.id,
                    cid: `cid_${item.id}`,
                    authorDID: item.author,
                    content: { text: item.text },
                    coherenceScore: 0.85 + (Math.random() * 0.1), // Mock score from "executor"
                    proof: result.proof.root,
                    timestamp: result.timestamp
                };
            }));

            setFeed(computedFeed);
        } catch (err) {
            console.error('Failed to fetch QFS feed:', err);
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
