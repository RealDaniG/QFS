/**
 * useFeed Hook
 * Fetches pending events from local store to simulate a "Feed"
 * In Phase 2, this will also fetch confirmed events from the Ledger
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { getPendingEventStore } from '@/lib/ledger/pending-store';
import type { PendingLedgerEvent } from '@/types/storage';

export function useFeed() {
    const [events, setEvents] = useState<PendingLedgerEvent[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchFeed = useCallback(async () => {
        setIsLoading(true);
        try {
            const store = await getPendingEventStore();
            // Fetch all pending events for now
            // In reality we would filter or paginate
            const allEvents = await store.getAll();

            // Sort by timestamp desc
            const sorted = allEvents.sort((a, b) => b.timestamp - a.timestamp);

            setEvents(sorted);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch feed:', err);
            setError(err as Error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchFeed();

        // Optional: Poll for updates every few seconds to see new posts appear
        const interval = setInterval(fetchFeed, 3000);
        return () => clearInterval(interval);
    }, [fetchFeed]);

    return {
        events,
        isLoading,
        error,
        refresh: fetchFeed
    };
}
