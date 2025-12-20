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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

function getAuthToken() {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('token') || '';
    }
    return '';
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
            const url = `${API_BASE_URL}/explain/reward/${walletId}${epoch ? `?epoch=${epoch}` : ''}`;

            const res = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!res.ok) {
                if (res.status === 401) throw new Error('Authentication required');
                if (res.status === 403) throw new Error('Permission denied');
                throw new Error('Failed to fetch explanation');
            }
            const data = await res.json();
            setExplanation(data);
        } catch (err) {
            console.error(err);
            setError(err instanceof Error ? err.message : 'Could not load explanation.');
            setExplanation(null);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchRankingExplanation = async (contentId: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const url = `${API_BASE_URL}/explain/ranking/${contentId}`;
            const res = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
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
