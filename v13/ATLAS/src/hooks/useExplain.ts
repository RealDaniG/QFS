import { useState } from 'react';
import { ValueNodeRewardExplanation, ContentRankingExplanation, SimplifiedExplanation } from '@/lib/qfs/explain-this';

type ExplanationType = ValueNodeRewardExplanation | ContentRankingExplanation | SimplifiedExplanation;

interface UseExplainResult {
    isLoading: boolean;
    error: string | null;
    explanation: ExplanationType | null;
    fetchRewardExplanation: (walletId: string, epoch?: number) => Promise<void>;
    fetchRankingExplanation: (contentId: string) => Promise<void>;
    clearExplanation: () => void;
}

export function useExplain(): UseExplainResult {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [explanation, setExplanation] = useState<ExplanationType | null>(null);

    const clearExplanation = () => {
        setExplanation(null);
        setError(null);
    };

    const fetchRewardExplanation = async (walletId: string, epoch?: number) => {
        setIsLoading(true);
        setError(null);
        try {
            const url = `/api/explain/reward/${walletId}${epoch ? `?epoch=${epoch}` : ''}`;
            // Note: In Next.js App Router, this would likely be a server action or standard fetch to API route
            // We assume /api/explain proxies to our FastApi endpoint or IS the FastApi endpoint
            // For this "stubbed" environment, we'll fetch from the python server if running, or mock if not

            const res = await fetch(`http://localhost:8000/explain/reward/${walletId}${epoch ? `?epoch=${epoch}` : ''}`);
            if (!res.ok) throw new Error('Failed to fetch explanation');
            const data = await res.json();
            setExplanation(data);
        } catch (err) {
            console.error(err);
            setError('Could not load explanation. Ensure QFS Backend is running.');

            // Fallback for demo if backend is offline
            setExplanation({
                summary: "Demo Mode",
                reason: "Backend unreachable",
                reason_codes: ["OFFLINE_MODE"],
                breakdown: {
                    base_reward: { ATR: "0.00 ATR" },
                    bonuses: [],
                    caps: [],
                    guards: [],
                    total_reward: { ATR: "0.00 ATR" }
                },
                policy_info: { version: "v13.stub", hash: "stub", has_guard_failures: false },
                verification: { hash: "stub-offline", consistent: true }
            } as any);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchRankingExplanation = async (contentId: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const res = await fetch(`http://localhost:8000/explain/ranking/${contentId}`);
            if (!res.ok) throw new Error('Failed to fetch explanation');
            const data = await res.json();
            setExplanation(data);
        } catch (err) {
            console.error(err);
            setError('Could not load explanation.');
        } finally {
            setIsLoading(false);
        }
    };

    return {
        isLoading,
        error,
        explanation,
        fetchRewardExplanation,
        fetchRankingExplanation,
        clearExplanation
    };
}
