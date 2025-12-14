'use client';

import {
    Wallet,
    TrendingUp,
    MessageSquare,
    Users,
    Shield
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useTreasury } from '@/hooks/useTreasury';
import { useAuth } from '@/hooks/useAuth';

import { ExplainThisPanel } from '@/components/ExplainThisPanel';
import { useExplain } from '@/hooks/useExplain';
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";

export default function WalletInterface() {
    const { balance, history, isLoading } = useTreasury();
    const { did } = useAuth();
    const { explanation, fetchRewardExplanation, isLoading: isExplaining, clearExplanation } = useExplain();

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
                            <CardTitle>Token Balances</CardTitle>
                            <CardDescription>DID: {did ? `${did.slice(0, 20)}...` : 'Not connected'}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-4">
                                {/* FLX Balance */}
                                <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Wallet className="h-5 w-5 text-blue-600" />
                                        <span className="font-medium">FLX Token</span>
                                        {isLoading && <Badge variant="secondary" className="ml-auto text-xs">Syncing...</Badge>}
                                    </div>
                                    <div className="text-2xl font-bold text-blue-600">{displayBalance}</div>
                                    <div className="text-sm text-muted-foreground flex justify-between">
                                        <span>Available</span>
                                        <span className="text-blue-700 font-medium">Staked: {displayStaked}</span>
                                    </div>
                                </div>

                                {/* Reputation Score (Placeholder, will come from coherence) */}
                                <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                                    <div className="flex items-center gap-2 mb-2">
                                        <TrendingUp className="h-5 w-5 text-purple-600" />
                                        <span className="font-medium">Reputation</span>
                                    </div>
                                    <div className="text-2xl font-bold text-purple-600">0.000</div>
                                    <div className="text-sm text-muted-foreground">Network reputation</div>
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
                                                // Assuming wallet_id is effectively the DID here, and mocking epoch
                                                fetchRewardExplanation(did || "wallet_123", 10);
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
                                                    <div className="text-green-600 font-bold">+{tx.amount.toFixed(2)} FLX</div>
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
                                {/* Placeholder bars */}
                                {[
                                    { label: 'Content Quality', val: 0, color: 'bg-green-600' },
                                    { label: 'Engagement', val: 0, color: 'bg-blue-600' },
                                    { label: 'Governance', val: 0, color: 'bg-purple-600' }
                                ].map(item => (
                                    <div key={item.label}>
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm">{item.label}</span>
                                            <span className="text-sm font-medium">{item.val.toFixed(2)}</span>
                                        </div>
                                        <div className="w-full bg-muted rounded-full h-2">
                                            <div className={`${item.color} h-2 rounded-full`} style={{ width: `${item.val * 100}%` }}></div>
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
                                    Join Community
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
