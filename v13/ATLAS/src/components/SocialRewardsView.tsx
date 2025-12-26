"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Shield, CheckCircle, XCircle, Search } from "lucide-react";
import { useSocialEpochs, useSocialEpochRewards, SocialRewardReceipt } from "@/hooks/useSocialRewards";

export function SocialRewardsView() {
    const [selectedEpoch, setSelectedEpoch] = useState<number | null>(null);
    const { data: epochs, isLoading: epochsLoading } = useSocialEpochs();
    const { data: rewards, isLoading: rewardsLoading } = useSocialEpochRewards(selectedEpoch ?? undefined);

    return (
        <div className="space-y-6">
            {/* Epoch Selection */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5 text-indigo-500" />
                        Social Governance Epochs
                    </CardTitle>
                    <CardDescription>
                        Select a finalized epoch to view deterministic reward distribution proofs.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {epochsLoading ? (
                        <div className="flex justify-center p-4"><Loader2 className="animate-spin" /></div>
                    ) : (
                        <div className="space-y-2">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Epoch ID</TableHead>
                                        <TableHead>Status</TableHead>
                                        <TableHead>Avg Coherence</TableHead>
                                        <TableHead>Total FLX</TableHead>
                                        <TableHead>Merkle Root</TableHead>
                                        <TableHead>Action</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {epochs?.map((epoch) => (
                                        <TableRow key={epoch.id}>
                                            <TableCell className="font-medium">#{epoch.id}</TableCell>
                                            <TableCell>
                                                <Badge variant={epoch.status === 'finalized' ? 'default' : 'secondary'}>
                                                    {epoch.status}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>{epoch.coherence_avg}</TableCell>
                                            <TableCell>{epoch.total_flx}</TableCell>
                                            <TableCell className="font-mono text-xs text-muted-foreground">
                                                {epoch.merkle_root.substring(0, 10)}...
                                            </TableCell>
                                            <TableCell>
                                                <Button
                                                    variant={selectedEpoch === epoch.id ? "secondary" : "ghost"}
                                                    size="sm"
                                                    onClick={() => setSelectedEpoch(epoch.id)}
                                                >
                                                    View Rewards
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Reward Details */}
            {selectedEpoch && (
                <Card>
                    <CardHeader>
                        <CardTitle>Epoch #{selectedEpoch} Rewards</CardTitle>
                        <CardDescription>
                            Per-post breakdown of Coherence, Engagement, and Sybil factors.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {rewardsLoading ? (
                            <div className="flex justify-center p-8"><Loader2 className="animate-spin" /></div>
                        ) : (
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Post ID</TableHead>
                                        <TableHead>Coherence (HSMF)</TableHead>
                                        <TableHead>Engagement</TableHead>
                                        <TableHead>Sybil</TableHead>
                                        <TableHead className="text-right">FLX Reward</TableHead>
                                        <TableHead className="text-right">CHR Delta</TableHead>
                                        <TableHead>Proof</TableHead>
                                        <TableHead>Code Identity</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {rewards?.map((r) => (
                                        <TableRow key={r.post_id}>
                                            <TableCell className="font-mono text-xs">{r.post_id}</TableCell>
                                            <TableCell>
                                                <div className="flex flex-col">
                                                    <span className={Number(r.coherence_score) > 0.8 ? "text-green-600 font-bold" : ""}>
                                                        {Number(r.coherence_score).toFixed(4)}
                                                    </span>
                                                    <span className="text-[10px] text-muted-foreground">
                                                        (Elig: {Number(r.eligibility_factor).toFixed(2)})
                                                    </span>
                                                </div>
                                            </TableCell>
                                            <TableCell>{Number(r.engagement_weight).toFixed(2)}x</TableCell>
                                            <TableCell>
                                                {Number(r.sybil_multiplier) < 1.0 ? (
                                                    <span className="text-red-500 font-bold">{Number(r.sybil_multiplier).toFixed(2)}</span>
                                                ) : (
                                                    <span className="text-muted-foreground">1.0</span>
                                                )}
                                            </TableCell>
                                            <TableCell className="text-right font-mono text-indigo-600">
                                                {Number(r.flx_reward).toFixed(2)}
                                            </TableCell>
                                            <TableCell className="text-right font-mono">
                                                +{Number(r.chr_reward).toFixed(0)}
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant="outline" className="font-mono text-[10px]">
                                                    Verifiable
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex flex-col text-[10px] items-start">
                                                    <Badge variant="secondary" className="font-mono text-[9px] mb-1">
                                                        {r.v13_version}
                                                    </Badge>
                                                    <span className="text-muted-foreground font-mono" title="Build Manifest SHA">
                                                        {r.build_manifest_sha256?.substring(0, 8) || "unknown"}
                                                    </span>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {rewards?.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                                                No rewards found for this epoch.
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
