"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Trophy, Calendar, CheckCircle2 } from "lucide-react";
import { useWalletAuth } from "@/hooks/useWalletAuth";
import { useAuthStore } from "@/lib/store/useAuthStore";
import { useWalletAdapter } from "@/lib/wallet/WalletProvider";
import { useConnectModal } from '@rainbow-me/rainbowkit';

interface StreakData {
    active: boolean;
    day_index: number;
    current_reward: number;
    next_window: number;
}

export function DailyRewardCard() {
    const { triggerAuth: connect, isConnected, isAuthenticating: isLoading } = useWalletAuth();
    const { address } = useAuthStore();
    const [streak, setStreak] = useState<StreakData | null>(null);
    const [loadingStreak, setLoadingStreak] = useState(false);

    const { session, connect: walletConnect } = useWalletAdapter();
    const isWalletConnected = !!session?.address;

    const { openConnectModal } = useConnectModal();

    const fetchStreak = async () => {
        if (!address) return;
        setLoadingStreak(true);
        try {
            const res = await fetch(`/api/v18/rewards/streak?wallet=${address}`);
            if (res.ok) {
                const data = await res.json();
                setStreak(data);
            }
        } catch (e) {
            console.error("Failed to fetch streak", e);
        } finally {
            setLoadingStreak(false);
        }
    };

    useEffect(() => {
        if (isConnected && address) {
            fetchStreak();
        }
    }, [isConnected, address]);

    // Handle claim
    const handleClaim = async () => {
        await connect();
        await fetchStreak();
    };

    const day = streak?.day_index || 0;
    const progress = (day / 15) * 100;

    const handleConnect = () => {
        if (openConnectModal) {
            openConnectModal();
        } else {
            // Fallback unique to this component
            console.warn("RainbowKit modal not available");
            walletConnect('metamask');
        }
    };

    return (
        <Card className="border-amber-200 bg-amber-50/50 dark:bg-amber-950/20">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2 text-amber-800 dark:text-amber-400">
                        <Trophy className="h-5 w-5" />
                        Daily Presence
                    </CardTitle>
                    <span className="text-sm font-bold text-amber-600">Day {day}/15</span>
                </div>
                <CardDescription>Sign daily to boost coherence & reputation.</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <Progress value={progress} className="h-2 bg-amber-200" />

                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Current Reward: {streak?.current_reward || 0} FLX</span>
                        <span>Target: 15 Days</span>
                    </div>

                    <Button
                        onClick={isWalletConnected ? (isConnected ? handleClaim : connect) : handleConnect}
                        disabled={isLoading}
                        className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
                    >
                        {isLoading ? (
                            "Processing..."
                        ) : isConnected ? (
                            <span className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4" />
                                Sign Today's Presence
                            </span>
                        ) : isWalletConnected ? (
                            <span className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4" />
                                Verify Presence (Sign)
                            </span>
                        ) : (
                            <span className="flex items-center gap-2">
                                <Calendar className="h-4 w-4" />
                                Connect to Start Streak
                            </span>
                        )}
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
