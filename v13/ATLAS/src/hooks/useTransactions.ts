'use client';

import { useCallback, useEffect, useState } from 'react';

export interface TransactionResponse {
  tx_id: string;
  sender: string;
  receiver: string;
  amount: number;
  asset: string;
  timestamp: string;
  status: string;
  signature?: string | null;
  metadata?: Record<string, unknown>;
}

export function useTransactions() {
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/transactions/', {
        method: 'GET',
        headers: {
          Authorization: 'Bearer test-token',
        },
      });

      if (!res.ok) {
        throw new Error(`Failed to fetch transactions: ${res.status}`);
      }

      const data = (await res.json()) as TransactionResponse[];
      setTransactions(Array.isArray(data) ? data : []);
      setError(null);
    } catch (e) {
      setError(e as Error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    transactions,
    isLoading,
    error,
    refresh,
  };
}
