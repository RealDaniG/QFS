import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ShieldCheck, HardDrive, Server, FileDigit, Activity } from "lucide-react";

interface StorageExplanation {
    content_id: string;
    replica_count: number;
    assigned_nodes: string[];
    shards: string[];
    proof_outcomes: Record<string, string>;
    metadata: {
        epoch: number;
        integrity_hash: string;
        explanation_hash: string;
        source: string;
    };
}

interface StorageExplainPanelProps {
    contentId: string;
}

export const StorageExplainPanel: React.FC<StorageExplainPanelProps> = ({ contentId }) => {
    const [explanation, setExplanation] = useState<StorageExplanation | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!contentId) return;

        const fetchExplanation = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`/api/explain/storage/${contentId}`);
                if (!response.ok) throw new Error("Failed to load storage proof");
                const data = await response.json();
                setExplanation(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Unlock failed");
            } finally {
                setLoading(false);
            }
        };

        fetchExplanation();
    }, [contentId]);

    if (loading) return <div className="p-4 text-center animate-pulse">Verifying Storage Proofs...</div>;
    if (error) return <Alert variant="destructive"><AlertTitle>Verification Failed</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>;
    if (!explanation) return null;

    return (
        <Card className="w-full max-w-2xl bg-zinc-950 border-zinc-800 text-zinc-100 font-mono">
            <CardHeader className="border-b border-zinc-800 pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium flex items-center gap-2 text-emerald-400">
                        <ShieldCheck className="w-4 h-4" />
                        STORAGE PROOF VERIFIED
                    </CardTitle>
                    <Badge variant="outline" className="text-xs bg-zinc-900 text-zinc-400 border-zinc-700">
                        {explanation.metadata.source.toUpperCase()}
                    </Badge>
                </div>
            </CardHeader>

            <CardContent className="pt-4 space-y-6">
                {/* Content Identity */}
                <div className="space-y-1">
                    <label className="text-xs text-zinc-500 uppercase tracking-wider">Content CID</label>
                    <div className="flex items-center gap-2 p-2 bg-zinc-900/50 rounded border border-zinc-800 break-all">
                        <FileDigit className="w-4 h-4 text-blue-400 shrink-0" />
                        <span className="text-xs text-zinc-300">{explanation.content_id}</span>
                    </div>
                </div>

                {/* Replica Status */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                        <label className="text-xs text-zinc-500 uppercase tracking-wider">Replication</label>
                        <div className="flex items-center gap-2 text-sm">
                            <HardDrive className="w-4 h-4 text-purple-400" />
                            <span className="font-bold">{explanation.replica_count} Node(s)</span>
                        </div>
                    </div>
                    <div className="space-y-1">
                        <label className="text-xs text-zinc-500 uppercase tracking-wider">Epoch Assigned</label>
                        <div className="flex items-center gap-2 text-sm">
                            <Activity className="w-4 h-4 text-yellow-400" />
                            <span className="font-bold">Epoch {explanation.metadata.epoch}</span>
                        </div>
                    </div>
                </div>

                {/* Node Distribution Map */}
                <div className="space-y-2">
                    <label className="text-xs text-zinc-500 uppercase tracking-wider mb-2 block">Node Distribution & Status</label>
                    <div className="space-y-2">
                        {explanation.assigned_nodes.map((nodeId) => (
                            <div key={nodeId} className="flex items-center justify-between p-2 rounded bg-zinc-900 border border-zinc-800">
                                <div className="flex items-center gap-2">
                                    <Server className="w-3 h-3 text-zinc-400" />
                                    <span className="text-xs text-zinc-300 font-mono">{nodeId.slice(0, 16)}...</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    {explanation.proof_outcomes[nodeId] === "success" ? (
                                        <Badge className="bg-emerald-950 text-emerald-400 border-emerald-800 text-[10px] uppercase">Verified</Badge>
                                    ) : (
                                        <Badge className="bg-red-950 text-red-400 border-red-800 text-[10px] uppercase">Proof Missing</Badge>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Verification Footer */}
                <div className="pt-4 border-t border-zinc-900">
                    <div className="flex flex-col gap-1">
                        <div className="flex justify-between text-[10px] text-zinc-600">
                            <span>Integrity Hash:</span>
                            <span className="font-mono text-zinc-500">{explanation.metadata.integrity_hash.slice(0, 24)}...</span>
                        </div>
                        <div className="flex justify-between text-[10px] text-zinc-600">
                            <span>Verification Hash:</span>
                            <span className="font-mono text-zinc-500">{explanation.metadata.explanation_hash.slice(0, 24)}...</span>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};
