'use client';

import { useWalletAuth } from '@/hooks/useWalletAuth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Lock, Wallet } from 'lucide-react';

interface AuthGateProps {
    children: React.ReactNode;
    title?: string;
    description?: string;
}

export function AuthGate({ children, title = "Authentication Required", description = "Connect your wallet to access this section of the ATLAS v18 dashboard." }: AuthGateProps) {
    const { isConnected, sessionToken, connect, isLoading } = useWalletAuth();

    // v18 Rule: Must be both connected and have a valid (cryptographic) session token
    if (!isConnected || !sessionToken) {
        return (
            <div className="flex items-center justify-center p-8 min-h-[400px]">
                <Card className="w-full max-w-md border-dashed border-2 bg-muted/30">
                    <CardHeader className="text-center">
                        <div className="mx-auto w-12 h-12 bg-blue-500/10 rounded-full flex items-center justify-center mb-4">
                            <Lock className="h-6 w-6 text-blue-600" />
                        </div>
                        <CardTitle>{title}</CardTitle>
                        <CardDescription>{description}</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col items-center gap-4">
                        <p className="text-sm text-muted-foreground text-center">
                            Your identity must be verified via the QFS distributed ledger before interacting with this system.
                        </p>
                        {!isConnected ? (
                            <p className="text-sm font-medium text-amber-600">
                                ⚠️ Use the "Connect Wallet" button in the top right to start.
                            </p>
                        ) : (
                            <Button
                                onClick={connect}
                                disabled={isLoading}
                                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600"
                            >
                                {isLoading ? "Verifying..." : "Verify Session Identity"}
                            </Button>
                        )}
                    </CardContent>
                </Card>
            </div>
        );
    }

    return <>{children}</>;
}
