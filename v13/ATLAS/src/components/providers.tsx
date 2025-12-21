"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState, useEffect } from "react";
import { WagmiProvider } from 'wagmi';
import { RainbowKitProvider } from '@rainbow-me/rainbowkit';
import { config } from '@/lib/web3/config';
import '@rainbow-me/rainbowkit/styles.css';
import { WalletProvider } from '@/lib/wallet/WalletProvider';
import { P2PProvider } from '@/contexts/P2PContext';

export function Providers({ children }: { children: ReactNode }) {
    const [mounted, setMounted] = useState(false);
    const [queryClient] = useState(() => new QueryClient({
        defaultOptions: {
            queries: {
                staleTime: 60 * 1000, // 1 minute
                gcTime: 5 * 60 * 1000, // 5 minutes
                refetchOnWindowFocus: false,
                retry: 1,
            },
        },
    }));

    useEffect(() => {
        setMounted(true);
    }, []);

    // Prevent hydration mismatch
    // if (!mounted) {
    //     return <>{children}</>;
    // }

    return (
        <WagmiProvider config={config}>
            <QueryClientProvider client={queryClient}>
                <RainbowKitProvider>
                    <WalletProvider>
                        <P2PProvider>
                            {children}
                        </P2PProvider>
                    </WalletProvider>
                </RainbowKitProvider>
            </QueryClientProvider>
        </WagmiProvider>
    );
}

