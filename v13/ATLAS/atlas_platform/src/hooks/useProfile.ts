/**
 * useProfile Hook
 * React wrapper for ProfileService
 */

'use client';

import { useState, useMemo, useCallback, useEffect } from 'react';
import { useAuth } from './useAuth';
import { ProfileService } from '@/lib/profile/service';
import type { Profile } from '@/types/storage';
import { Buffer } from 'buffer';
import { deterministicNow } from '../lib/deterministic';

export function useProfile() {
    const { privateKey, did, isAuthenticated } = useAuth();
    const [profile, setProfile] = useState<Profile | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    // Memoize service instance
    const service = useMemo(() => {
        if (!isAuthenticated || !privateKey || !did) return null;
        return new ProfileService(privateKey, did);
    }, [isAuthenticated, privateKey, did]);

    // Load profile on auth (placeholder - actual loading needs a CID)
    // In Phase 1, we might store the profile CID locally or fetch from a 'test' resolver
    useEffect(() => {
        if (did) {
            // TODO: Logic to look up current profile CID for the DID 
            // (For now, we start empty or could load from localStorage cache)
        }
    }, [did]);

    const updateProfile = useCallback(async (
        updates: Partial<Profile>
    ) => {
        if (!service || !did) {
            setError(new Error('User not authenticated'));
            return null;
        }

        setIsSaving(true);
        setError(null);

        try {
            // 1. Construct new profile object
            const newProfile: Profile = {
                did,
                displayName: updates.displayName || 'Anonymous',
                createdAtMs: profile?.createdAtMs || deterministicNow(),
                updatedAtMs: deterministicNow(),
                version: (profile?.version || 0) + 1,
                ...updates,
            };

            // 2. Publish
            const result = await service.publishProfile(newProfile);

            // 3. Update local state
            setProfile(newProfile);

            return result;
        } catch (err) {
            console.error('Profile update failed:', err);
            setError(err as Error);
            return null;
        } finally {
            setIsSaving(false);
        }
    }, [service, did, profile]);

    const uploadAvatar = useCallback(async (file: File) => {
        if (!service) return null;
        try {
            const buffer = Buffer.from(await file.arrayBuffer());
            return await service.uploadAvatar(buffer, file.type);
        } catch (err) {
            console.error('Avatar upload failed:', err);
            throw err;
        }
    }, [service]);

    return {
        profile,
        updateProfile,
        uploadAvatar,
        isLoading,
        isSaving,
        error,
        isReady: !!service,
    };
}
