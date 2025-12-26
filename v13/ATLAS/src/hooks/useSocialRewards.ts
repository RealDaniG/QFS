"use client";

import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useWalletAuth } from "./useWalletAuth";

export interface SocialEpochSummary {
    id: number;
    coherence_avg: string;
    total_flx: string;
    merkle_root: string;
    status: string;
}

export interface SocialRewardReceipt {
    type: "SOCIAL_REWARD_APPLIED";
    epoch_id: number;
    post_id: string;
    author_id: string;
    coherence_score: string;
    engagement_weight: string;
    sybil_multiplier: string;
    eligibility_factor: string;
    flx_reward: string;
    chr_reward: string;
    res_reward: string;
    v13_version: string;
    build_manifest_sha256: string;
}

export function useSocialEpochs() {
    const { isConnected } = useWalletAuth();

    return useQuery<SocialEpochSummary[]>({
        queryKey: ["socialEpochs"],
        queryFn: async () => {
            const { data } = await axios.get("/api/v13/social/epochs");
            return data;
        },
        enabled: isConnected,
    });
}

export function useSocialEpochRewards(epochId?: number) {
    const { isConnected } = useWalletAuth();

    return useQuery<SocialRewardReceipt[]>({
        queryKey: ["socialEpochRewards", epochId],
        queryFn: async () => {
            if (!epochId) return [];
            const { data } = await axios.get(`/api/v13/social/epochs/${epochId}/rewards`);
            return data;
        },
        enabled: isConnected && !!epochId,
    });
}
