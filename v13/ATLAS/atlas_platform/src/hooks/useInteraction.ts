'use client';

import { useState } from 'react';
import { useAuth } from './useAuth';
import { getPendingEventStore } from '@/lib/ledger/pending-store';
import { PendingInteractionEvent, hashMetadata } from '@/types/storage';
import { deterministicNow, deterministicUUID } from '../lib/deterministic';

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
            const pendingId = deterministicUUID();

            const event: PendingInteractionEvent = {
                eventType: 'InteractionCreated',
                pendingId,
                actorDID: did,
                inputs,
                eventInputHash,
                createdAtMs: deterministicNow(),
                status: 'pending' // Will be picked up by SyncService
            };

            const store = await getPendingEventStore();
            await store.save(event);
            console.log(`[Interaction] Submitted ${type} on ${targetCID}`);
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
