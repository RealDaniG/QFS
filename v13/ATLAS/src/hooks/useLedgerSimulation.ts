'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { MockLedger } from '@/lib/ledger/mock-ledger';
import { LedgerSyncService } from '@/lib/ledger/sync-service';

// Global singleton instances to persist across re-renders
let mockLedgerInstance: MockLedger | null = null;
let syncServiceInstance: LedgerSyncService | null = null;

export function useLedgerSimulation() {
    const [isRunning, setIsRunning] = useState(false);
    const [blockTimeMs, setBlockTimeMs] = useState(5000);

    const toggleSimulation = useCallback(() => {
        if (isRunning) {
            // Stop
            if (mockLedgerInstance) mockLedgerInstance.stopMining();
            if (syncServiceInstance) syncServiceInstance.stop();
            setIsRunning(false);
        } else {
            // Start
            if (!mockLedgerInstance) {
                mockLedgerInstance = new MockLedger(true, blockTimeMs);
            } else {
                mockLedgerInstance.startMining();
            }

            if (!syncServiceInstance) {
                syncServiceInstance = new LedgerSyncService(mockLedgerInstance);
            }
            syncServiceInstance.start();
            setIsRunning(true);
        }
    }, [isRunning, blockTimeMs]);

    // Cleanup on unmount (optional - maybe we want it running in background?)
    // For now, let's keep it running even if hook unmounts, to simulate a background node.

    return {
        isRunning,
        toggleSimulation,
        setBlockTimeMs
    };
}
