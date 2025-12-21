"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { P2PNode, P2PConfig } from '@/lib/p2p/node'; // Ensure path is correct
import { useWalletAuth } from '@/hooks/useWalletAuth';

interface P2PContextType {
    node: P2PNode | null;
    isReady: boolean;
}

const P2PContext = createContext<P2PContextType>({
    node: null,
    isReady: false
});

export function P2PProvider({ children }: { children: ReactNode }) {
    const { isAuthenticated, address } = useWalletAuth();
    const [node, setNode] = useState<P2PNode | null>(null);
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        let activeNode: P2PNode | null = null;

        const initP2P = async () => {
            if (isAuthenticated && address) {
                console.log("Initializing P2P Node...");
                activeNode = new P2PNode();

                // TODO: Fetch real bootstrap peers from backend or config
                const config: P2PConfig = {
                    walletAddress: address,
                    bootstrapPeers: []
                };

                await activeNode.start(config);
                setNode(activeNode);
                setIsReady(true);
            }
        };

        if (isAuthenticated && !node) {
            initP2P();
        }

        return () => {
            if (activeNode) {
                console.log("Stopping P2P Node...");
                activeNode.stop();
            }
        };
    }, [isAuthenticated, address, node]);

    return (
        <P2PContext.Provider value={{ node, isReady }}>
            {children}
        </P2PContext.Provider>
    );
}

export function useP2P() {
    return useContext(P2PContext);
}
