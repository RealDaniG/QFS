'use client';

import { useAccount } from 'wagmi';
import { useWalletAuth } from '@/hooks/useWalletAuth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Lock, Wallet } from 'lucide-react';
import { useEffect } from 'react';
import { useConnectModal } from '@rainbow-me/rainbowkit';

interface AuthGateProps {
    children: React.ReactNode;
    title?: string;
    description?: string;
}

export function AuthGate({
    children,
    title = "Authentication Required",
    description = "Connect your wallet to access this section."
}: AuthGateProps) {
    const { isConnected: wagmiConnected } = useAccount();
    const { isConnected, sessionToken, isLoading, error, triggerAuth } = useWalletAuth();
    const { openConnectModal } = useConnectModal();

    useEffect(() => {
        console.log('[AuthGate] State:', {
            wagmiConnected,
            authStoreConnected: isConnected,
            hasToken: !!sessionToken,
            isLoading,
            error
        });
    }, [wagmiConnected, isConnected, sessionToken, isLoading, error]);

    // Stage 1: Loading auth
    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-8 min-h-[400px]">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Verifying identity...</p>
                </div>
            </div>
        );
    }

    // Stage 2: Wallet not connected at all
    if (!wagmiConnected) {
        return (
            <div className="flex items-center justify-center p-8 min-h-[400px]">
                <Card className="w-full max-w-md">
                    <CardHeader className="text-center">
                        <Wallet className="h-12 w-12 mx-auto mb-4 text-blue-600" />
                        <CardTitle>{title}</CardTitle>
                        <CardDescription>{description}</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col items-center gap-4">
                        <Button onClick={() => openConnectModal?.()} className="w-full">
                            Connect Wallet
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    // Stage 3: Wallet connected but no session yet
    if (wagmiConnected && !sessionToken) {

        return (
            <div className="flex items-center justify-center p-8 min-h-[400px]">
                <Card className="w-full max-w-md border-blue-500/30 bg-blue-500/5">
                    <CardHeader className="text-center">
                        <Lock className="h-12 w-12 mx-auto mb-4 text-blue-600 animate-pulse" />
                        <CardTitle>Security Check Required</CardTitle>
                        <CardDescription>
                            Please sign the challenge to verify your identity and unlock the dashboard.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {error && (
                            <p className="text-sm text-red-600 text-center bg-red-50 p-2 rounded">{error}</p>
                        )}
                        <Button
                            onClick={() => triggerAuth()}
                            className="w-full font-bold shadow-lg"
                            size="lg"
                        >
                            Sign to Continue
                        </Button>
                        <p className="text-xs text-center text-muted-foreground">
                            This signature is free and does not cost gas.
                        </p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    // Stage 4: Fully authenticated
    console.log('[AuthGate] ✅ Unlocked');
    return <>{children}</>;
}
