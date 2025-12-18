/**
 * useP0Services.ts - React hooks for P0 features
 * 
 * Provides React Query integration for:
 * - Direct Messaging
 * - Explain-This
 * - Guilds/Communities
 * - Appeals
 * - Onboarding Tours
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from './useAuth';
import type {
    Thread,
    Message,
    Explanation,
    Guild,
    GuildManifest,
    Appeal,
    TourProgress
} from '../lib/p0-api-client';

// ============= Direct Messaging =============

export function useDM() {
    const { user, p0Api, capabilities } = useAuth();
    const queryClient = useQueryClient();

    const canSend = capabilities.includes('DM_SEND');
    const canRead = capabilities.includes('DM_READ_OWN');
    const canCreateThread = capabilities.includes('DM_CREATE_THREAD');

    // List all threads
    const threads = useQuery({
        queryKey: ['dm-threads', user?.id],
        queryFn: () => p0Api.dm_listThreads(),
        enabled: canRead && !!user
    });

    // Get thread history
    const useThreadHistory = (threadId: string) => {
        return useQuery({
            queryKey: ['dm-thread-history', threadId],
            queryFn: () => p0Api.dm_getHistory(threadId),
            enabled: canRead && !!threadId
        });
    };

    // Create thread
    const createThread = useMutation({
        mutationFn: (recipientId: string) => p0Api.dm_createThread(recipientId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['dm-threads'] });
        }
    });

    // Send message
    const sendMessage = useMutation({
        mutationFn: ({ threadId, content }: { threadId: string; content: string }) =>
            p0Api.dm_sendMessage(threadId, content),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['dm-thread-history', variables.threadId] });
        }
    });

    return {
        threads,
        useThreadHistory,
        createThread: createThread.mutate,
        sendMessage: sendMessage.mutate,
        canSend,
        canRead,
        canCreateThread,
        isCreatingThread: createThread.isPending,
        isSendingMessage: sendMessage.isPending
    };
}

// ============= Explain-This =============

export function useExplainThis() {
    const { p0Api } = useAuth();

    // Single explanation
    const useExplanation = (entityType: string, entityId: string, enabled = true) => {
        return useQuery({
            queryKey: ['explain', entityType, entityId],
            queryFn: () => p0Api.explain(entityType, entityId),
            enabled: enabled && !!entityType && !!entityId
        });
    };

    // Explanation tree (drill-down)
    const useExplanationTree = (entityId: string, depth = 2) => {
        return useQuery({
            queryKey: ['explain-tree', entityId, depth],
            queryFn: () => p0Api.explainTree(entityId, depth),
            enabled: !!entityId
        });
    };

    // Batch explanations
    const explainBatch = useMutation({
        mutationFn: (targets: Array<{ type: string; id: string }>) =>
            p0Api.explainBatch(targets)
    });

    return {
        useExplanation,
        useExplanationTree,
        explainBatch: explainBatch.mutate,
        isBatchLoading: explainBatch.isPending
    };
}

// ============= Guilds/Communities =============

export function useGuilds() {
    const { user, p0Api } = useAuth();
    const queryClient = useQueryClient();

    // List all guilds
    const guilds = useQuery({
        queryKey: ['guilds'],
        queryFn: () => p0Api.guild_list()
    });

    // Get specific guild
    const useGuild = (guildId: string) => {
        return useQuery({
            queryKey: ['guild', guildId],
            queryFn: () => p0Api.guild_get(guildId),
            enabled: !!guildId
        });
    };

    // Create guild
    const createGuild = useMutation({
        mutationFn: (manifest: GuildManifest) => p0Api.guild_create(manifest),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['guilds'] });
        }
    });

    // Join guild
    const joinGuild = useMutation({
        mutationFn: (guildId: string) => p0Api.guild_join(guildId),
        onSuccess: (_, guildId) => {
            queryClient.invalidateQueries({ queryKey: ['guild', guildId] });
            queryClient.invalidateQueries({ queryKey: ['guilds'] });
        }
    });

    return {
        guilds,
        useGuild,
        createGuild: createGuild.mutate,
        joinGuild: joinGuild.mutate,
        isCreating: createGuild.isPending,
        isJoining: joinGuild.isPending
    };
}

// ============= Appeals =============

export function useAppeals() {
    const { p0Api } = useAuth();
    const queryClient = useQueryClient();

    // Get appeal status
    const useAppealStatus = (appealId: string) => {
        return useQuery({
            queryKey: ['appeal', appealId],
            queryFn: () => p0Api.appeal_status(appealId),
            enabled: !!appealId,
            refetchInterval: (data) => {
                // Poll every 30s if still pending
                return data?.status === 'PENDING' ? 30000 : false;
            }
        });
    };

    // Submit appeal
    const submitAppeal = useMutation({
        mutationFn: ({
            targetEventId,
            evidenceCid,
            reason
        }: {
            targetEventId: string;
            evidenceCid: string;
            reason: string;
        }) => p0Api.appeal_submit(targetEventId, evidenceCid, reason)
    });

    return {
        useAppealStatus,
        submitAppeal: submitAppeal.mutate,
        isSubmitting: submitAppeal.isPending
    };
}

// ============= Onboarding Tours =============

export function useOnboarding() {
    const { user, p0Api } = useAuth();
    const queryClient = useQueryClient();

    // List available tours
    const tours = useQuery({
        queryKey: ['tours'],
        queryFn: () => p0Api.tour_list()
    });

    // Get tour progress
    const useTourProgress = (tourId: string) => {
        return useQuery({
            queryKey: ['tour-progress', tourId, user?.id],
            queryFn: () => p0Api.tour_getProgress(tourId),
            enabled: !!tourId && !!user
        });
    };

    // Start tour
    const startTour = useMutation({
        mutationFn: (tourId: string) => p0Api.tour_start(tourId),
        onSuccess: (_, tourId) => {
            queryClient.invalidateQueries({ queryKey: ['tour-progress', tourId] });
        }
    });

    // Complete step
    const completeStep = useMutation({
        mutationFn: ({ tourId, stepId }: { tourId: string; stepId: string }) =>
            p0Api.tour_completeStep(tourId, stepId),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['tour-progress', variables.tourId] });
        }
    });

    return {
        tours,
        useTourProgress,
        startTour: startTour.mutate,
        completeStep: completeStep.mutate,
        isStarting: startTour.isPending,
        isCompletingStep: completeStep.isPending
    };
}

// ============= Utility Hooks =============

/**
 * Check if user has specific capability
 */
export function useHasCapability(capability: string): boolean {
    const { capabilities } = useAuth();
    return capabilities.includes(capability);
}

/**
 * Get missing capabilities for a feature
 */
export function useMissingCapabilities(required: string[]): string[] {
    const { capabilities } = useAuth();
    return required.filter(cap => !capabilities.includes(cap));
}

/**
 * Combined hook for all P0 services
 */
export function useP0() {
    const dm = useDM();
    const explainThis = useExplainThis();
    const guilds = useGuilds();
    const appeals = useAppeals();
    const onboarding = useOnboarding();

    return {
        dm,
        explainThis,
        guilds,
        appeals,
        onboarding
    };
}
