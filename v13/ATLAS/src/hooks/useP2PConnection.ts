/**
 * React Hook for P2P Connection Management
 */

import { useEffect, useState } from 'react';
import { getP2PClient } from '@/lib/p2p/client';

export function useP2PConnection() {
    const [isConnected, setIsConnected] = useState(false);
    const [peerId, setPeerId] = useState('');
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Ensure this runs only on client side
        if (typeof window === 'undefined') return;

        const client = getP2PClient();

        // Connect on mount (if not already connected)
        const status = client.getConnectionStatus();
        if (!status.connected) {
            client.connect()
                .then(() => {
                    const newStatus = client.getConnectionStatus();
                    setIsConnected(newStatus.connected);
                    setPeerId(newStatus.peerId);
                })
                .catch((err) => {
                    setError(err.message || 'Connection failed');
                });
        } else {
            setIsConnected(status.connected);
            setPeerId(status.peerId);
        }

        // Check status periodically to update UI
        const interval = setInterval(() => {
            const status = client.getConnectionStatus();
            setIsConnected(status.connected);
        }, 2000);

        // Cleanup on unmount
        return () => {
            clearInterval(interval);
            // Don't disconnect - keep connection alive across navigations
        };
    }, []);

    return { isConnected, peerId, error };
}
