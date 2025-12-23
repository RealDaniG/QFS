/**
 * Hook for real-time feed updates via P2P
 */

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { getP2PClient } from '@/lib/p2p/client';
import type { TrustedEnvelope } from '@/lib/trust/envelope';

export function useP2PFeed() {
    const queryClient = useQueryClient();

    useEffect(() => {
        if (typeof window === 'undefined') return;

        const client = getP2PClient();

        const handler = (envelope: TrustedEnvelope) => {
            console.log('[Feed] 📬 New post via P2P:', envelope.payload_cid.slice(0, 16));

            // Invalidate feed query to trigger refetch
            queryClient.invalidateQueries({ queryKey: ['feed'] });

            // Future: Optimistically update cache here
        };

        // Subscribe to feed topic
        client.subscribe('/atlas/feed', handler);

        // Cleanup
        return () => {
            client.unsubscribe('/atlas/feed', handler);
        };
    }, [queryClient]);
}
