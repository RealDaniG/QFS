'use client';

import {
    Wallet,
    TrendingUp,
    MessageSquare,
    Users,
    Shield,
    Zap
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useTreasury } from '@/hooks/useTreasury';
import { useAuth } from '@/hooks/useAuth';
import { useWalletAuth } from '@/hooks/useWalletAuth';
import { WalletConnectButton } from '@/components/WalletConnectButton';

import { ExplainThisPanel } from '@/components/ExplainThisPanel';
import { useExplain } from '@/hooks/useExplain';
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";

export default function WalletInterface() {
    const { balance, history, isLoading } = useTreasury();
    const { did } = useAuth();
    const { isConnected, address: walletAddress } = useWalletAuth();
    const { explanation, fetchRewardExplanation, isLoading: isExplaining, clearExplanation } = useExplain();

    // Auth Gate: Show connect wallet message if not authenticated
    if (!isConnected) {
        return (
            <div className="max-w-4xl mx-auto">
                <Card className="border-blue-500/30 bg-blue-500/5">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Shield className="h-5 w-5 text-blue-600" />
                            Wallet Connection Required
                        </CardTitle>
                        <CardDescription>
                            Connect your wallet to view your balance, transaction history, and internal credits.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center gap-4 p-4 bg-background/50 rounded-xl border border-blue-500/20">
                            <Wallet className="h-8 w-8 text-blue-600" />
                            <div className="flex-1">
                                <p className="text-sm font-semibold">Secure Wallet Authentication</p>
                                <p className="text-xs text-muted-foreground">
                                    Your wallet is used for cryptographic identity only. No transfers are supported.
                                </p>
                            </div>
                        </div>
                        <div className="flex justify-center pt-4">
                            <WalletConnectButton />
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    // Fallback if loading or no auth (although auth is likely present)
    const displayBalance = balance?.balance.toFixed(2) || '0.00';
    const displayRewards = balance?.rewards.toFixed(2) || '0.00';
    const displayStaked = balance?.staked.toFixed(2) || '0.00';

    return (
        <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Main Stats Column */}
                <div className="lg:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Wallet Balance</CardTitle>
                            <div className="flex justify-between items-center">
                                <CardDescription>
                                    {isConnected ? (
                                        <span className="text-blue-600 font-mono">
                                            Connected: {walletAddress?.slice(0, 6)}...{walletAddress?.slice(-4)}
                                        </span>
                                    ) : (
                                        <span>DID: {did ? `${did.slice(0, 20)}...` : 'Not connected'}</span>
                                    )}
                                </CardDescription>
                                <WalletConnectButton />
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {/* Wallet Balance */}
                                <div className="p-4 bg-blue-50 rounded-lg">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Wallet className="h-5 w-5 text-blue-600" />
                                        <span className="font-medium text-blue-900">Wallet Balance</span>
                                    </div>
                                    <div className="text-2xl font-bold text-blue-600">
                                        {displayBalance} FLX
                                    </div>
                                    <div className="text-sm text-blue-700 font-medium">
                                        Staked: {displayStaked}
                                    </div>
                                </div>

                                {/* Accrued Rewards */}
                                <div className="p-4 bg-green-50 rounded-lg border border-green-100">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Zap className="h-5 w-5 text-green-600" />
                                        <span className="font-medium text-green-900">Accrued Rewards</span>
                                    </div>
                                    <div className="text-2xl font-bold text-green-600">
                                        {displayRewards} FLX
                                    </div>
                                    <div className="text-sm text-green-700 font-medium">
                                        V18 Yield Pool
                                    </div>
                                </div>

                                {/* Reputation Score */}
                                <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                                    <div className="flex items-center gap-2 mb-2">
                                        <TrendingUp className="h-5 w-5 text-purple-600" />
                                        <span className="font-medium text-purple-900">Reputation</span>
                                    </div>
                                    <div className="text-2xl font-bold text-purple-600">
                                        {balance?.reputation?.toFixed(0) || '0'}
                                    </div>
                                    <div className="text-sm text-purple-700 font-medium">Network weight</div>
                                </div>
                            </div>

                        </CardContent>
                    </Card>

                    {/* Transaction/Reward History */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Reward History</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {history.length === 0 ? (
                                    <div className="text-center text-muted-foreground py-4">No recent transactions</div>
                                ) : (
                                    history.map((tx) => (
                                        <Dialog key={tx.id} onOpenChange={(open) => {
                                            if (open) {
                                                // Using walletAddress or fallback DID
                                                fetchRewardExplanation(walletAddress || did || "wallet_123", 10);
                                            } else {
                                                clearExplanation();
                                            }
                                        }}>
                                            <DialogTrigger asChild>
                                                <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                                                    <div>
                                                        <div className="font-medium">{tx.reason}</div>
                                                        <div className="text-sm text-muted-foreground">
                                                            {new Date(tx.timestamp).toLocaleTimeString()} • {tx.id.split('_')[2]}
                                                            <Badge variant="outline" className="ml-2 text-[10px] h-5">Explain</Badge>
                                                        </div>
                                                    </div>
                                                    <div className={tx.amount >= 0 ? "text-green-600 font-bold" : "text-red-600 font-bold"}>
                                                        {tx.amount >= 0 ? '+' : ''}{tx.amount.toFixed(2)} FLX
                                                    </div>

                                                </div>
                                            </DialogTrigger>
                                            <DialogContent className="max-w-2xl">
                                                <ExplainThisPanel
                                                    type="reward"
                                                    explanation={explanation || undefined}
                                                    isLoading={isExplaining}
                                                />
                                            </DialogContent>
                                        </Dialog>
                                    ))
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Right Column: Actions */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Reputation Breakdown</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                { /* Real reputation bars from API */}
                                {[
                                    { label: 'Content Quality', val: balance?.reputation_breakdown?.content_quality || 0, color: 'bg-green-600' },
                                    { label: 'Engagement', val: balance?.reputation_breakdown?.engagement || 0, color: 'bg-blue-600' },
                                    { label: 'Governance', val: balance?.reputation_breakdown?.governance || 0, color: 'bg-purple-600' }
                                ].map(item => (
                                    <div key={item.label}>
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm">{item.label}</span>
                                            <span className="text-sm font-medium">{(item.val * 100).toFixed(0)}%</span>
                                        </div>
                                        <div className="w-full bg-muted rounded-full h-2">
                                            <div className={`${item.color} h-2 rounded-full transition-all duration-500`} style={{ width: `${item.val * 100}%` }}></div>
                                        </div>
                                    </div>
                                ))}

                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Action Simulator</CardTitle>
                            <CardDescription>Simulate potential rewards</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                <Button variant="outline" className="w-full justify-start" disabled>
                                    <MessageSquare className="h-4 w-4 mr-2" />
                                    Post Content (Use 'Create' Tab)
                                </Button>
                                <Button variant="outline" className="w-full justify-start">
                                    <Users className="h-4 w-4 mr-2" />
                                    Join Space
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
