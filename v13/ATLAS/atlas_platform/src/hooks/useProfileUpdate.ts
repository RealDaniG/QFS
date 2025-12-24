'use client';

import { useState } from 'react';
import { useAuth } from './useAuth';
import { getPendingEventStore } from '@/lib/ledger/pending-store';
import { PendingLedgerEvent, hashMetadata } from '@/types/storage';
import { deterministicNow, deterministicUUID } from '@/lib/deterministic';

export function useProfileUpdate() {
    const { did } = useAuth();
    const [isUpdating, setIsUpdating] = useState(false);

    const updateProfile = async (
        profileData: {
            name?: string;
            bio?: string;
            avatar?: string; // CID or URL
        }
    ) => {
        if (!did) {
            console.error('No identity found');
            return;
        }

        setIsUpdating(true);
        try {
            // Hash the profile data as "inputs"
            const eventInputHash = await hashMetadata(profileData);
            const pendingId = deterministicUUID();

            const event: PendingLedgerEvent = {
                eventType: 'ProfileUpdated',
                pendingId,
                actorDID: did,
                inputs: profileData,
                eventInputHash,
                createdAtMs: deterministicNow(),
                status: 'pending'
            };

            const store = await getPendingEventStore();
            await store.save(event);
            console.log(`[Profile] Submitted update for ${did}`);
            return pendingId;

        } catch (error) {
            console.error('Failed to update profile:', error);
            throw error;
        } finally {
            setIsUpdating(false);
        }
    };

    return { updateProfile, isUpdating };
}
