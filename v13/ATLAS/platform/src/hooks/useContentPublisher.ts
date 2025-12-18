/**
 * useContentPublisher Hook
 * React wrapper for ContentPublisher service
 */

'use client';

import { useState, useMemo, useCallback } from 'react';
import { useAuth } from './useAuth';
import { ContentPublisher, PublishResult } from '@/lib/content/publisher';
import type { Visibility } from '@/types/storage';

export function useContentPublisher() {
    const { privateKey, did, isAuthenticated } = useAuth();
    const [isPublishing, setIsPublishing] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    // Memoize publisher instance
    const publisher = useMemo(() => {
        if (!isAuthenticated || !privateKey || !did) return null;
        return new ContentPublisher(privateKey, did);
    }, [isAuthenticated, privateKey, did]);

    const publish = useCallback(async (
        content: string,
        options: {
            tags?: string[];
            visibility?: Visibility;
            communityId?: string;
        }
    ): Promise<PublishResult | null> => {
        if (!publisher) {
            setError(new Error('User not authenticated'));
            return null;
        }

        setIsPublishing(true);
        setError(null);

        try {
            // Create metadata
            const metadata = {
                type: 'text/plain', // Default to text/plain for now
                communityId: options.communityId,
                tags: options.tags,
                visibility: options.visibility || 'public',
            };

            // Publish directly (create draft + publish)
            const result = await publisher.publishContent(content, metadata);

            return result;
        } catch (err) {
            console.error('Publishing failed:', err);
            setError(err as Error);
            return null;
        } finally {
            setIsPublishing(false);
        }
    }, [publisher]);

    const createDraft = useCallback((
        content: string,
        options: {
            tags?: string[];
            visibility?: Visibility;
        }
    ) => {
        if (!publisher) return null;

        return publisher.createDraft(content, {
            type: 'text/plain',
            tags: options.tags,
            visibility: options.visibility,
        });
    }, [publisher]);

    return {
        publish,
        createDraft,
        isPublishing,
        error,
        isReady: !!publisher,
    };
}
