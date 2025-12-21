"use client";

import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useWalletAuth } from "./useWalletAuth";

interface ExplainRewardResponse {
  wallet_id: string;
  epoch: number;
  base: string;
  bonuses: Array<{ label: string; value: string; reason: string }>;
  caps: Array<{ label: string; value: string; reason: string }>;
  guards: Array<{ name: string; result: "pass" | "fail"; reason: string }>;
  total: string;
  metadata: {
    replay_hash: string;
    computed_at: string;
    source: string;
  };
}

export function useExplainReward(walletId: string, epoch?: number) {
  const { isConnected, address } = useWalletAuth();

  return useQuery<ExplainRewardResponse>({
    queryKey: ["explainReward", walletId, epoch],
    queryFn: async () => {
      const params = epoch ? `?epoch=${epoch}` : "";
      const { data } = await axios.get(
        `/api/explain/reward/${walletId}${params}`,
        {
          headers: {
            'x-atlas-address': address
          }
        }
      );
      return data;
    },
    enabled: !!walletId && isConnected && !!address,
    staleTime: 60_000, // 1 minute
  });
}
