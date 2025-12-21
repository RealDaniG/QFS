'use client';

import { useState } from 'react';
import { useAuth } from './useAuth';
import { getPendingEventStore } from '@/lib/ledger/pending-store';
import { PendingInteractionEvent, hashMetadata } from '@/types/storage';

export function useInteraction() {
    const { did } = useAuth();
    const [isSubmitting, setIsSubmitting] = useState(false);

    const interact = async (
        type: 'like' | 'comment' | 'repost' | 'quote',
        targetCID: string,
        contentCID?: string, // If commenting/quoting
        extraData?: Record<string, any> // e.g. comment text
    ) => {
        if (!did) {
            console.error('No identity found');
            return;
        }

        setIsSubmitting(true);
        try {
            const inputs = {
                interactionType: type,
                targetCID,
                contentCID,
                ...extraData
            };

            const eventInputHash = await hashMetadata(inputs);
            const pendingId = crypto.randomUUID();

            const event: PendingInteractionEvent = {
                eventType: 'InteractionCreated',
                pendingId,
                actorDID: did,
                inputs,
                eventInputHash,
                createdAtMs: Date.now(),
                status: 'pending' // Will be picked up by SyncService
            };

            const store = await getPendingEventStore();
            await store.save(event);
            console.log(`[Interaction] Saved locally: ${type} on ${targetCID}`);

            // v18 Re-integration: Commit to EvidenceBus
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
            const sessionToken = localStorage.getItem('atlas_session')
                ? JSON.parse(localStorage.getItem('atlas_session')!).sessionToken
                : null;

            if (sessionToken) {
                try {
                    const commitRes = await fetch(`${baseUrl}/api/evidence/commit`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${sessionToken}`
                        },
                        body: JSON.stringify({
                            type: event.eventType,
                            payload: event.inputs,
                            signature: null, // signatures deferred until P2P layer is full
                            parent_hash: null
                        })
                    });

                    if (commitRes.ok) {
                        const commitData = await commitRes.ok ? await commitRes.json() : null;
                        console.log(`[Interaction] Committed to EvidenceBus: ${commitData?.id}`);
                    }
                } catch (e) {
                    console.warn('[Interaction] EvidenceBus commit failed (offline?), but action saved locally.', e);
                }
            }

            return pendingId;

        } catch (error) {
            console.error('Failed to submit interaction:', error);
            throw error;
        } finally {
            setIsSubmitting(false);
        }
    };

    return { interact, isSubmitting };
}
