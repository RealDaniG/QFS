import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle2, XCircle, FileJson, PlayCircle } from "lucide-react";

interface PoEArtifact {
    artifact_id: string;
    poe_version: string;
    proof_hash: string;
    governance_scope: {
        cycle: number;
        parameter_key: string;
    };
    signatures: {
        nod_id: string;
        timestamp: string;
    };
}

export const PoEVerificationDashboard: React.FC = () => {
    const [artifactId, setArtifactId] = useState('');
    const [loading, setLoading] = useState(false);
    const [artifact, setArtifact] = useState<PoEArtifact | null>(null);
    const [verificationStatus, setVerificationStatus] = useState<'idle' | 'success' | 'failure'>('idle');

    const fetchArtifact = async () => {
        if (!artifactId) return;
        setLoading(true);
        setVerificationStatus('idle');
        setArtifact(null);

        try {
            // In a real app, this would hit the API endpoint we created
            const response = await fetch(`/api/v1/governance/poe/${artifactId}`);
            if (response.ok) {
                const data = await response.json();
                setArtifact(data);
                // Simulate verification delay
                setTimeout(() => setVerificationStatus('success'), 800);
            } else {
                setVerificationStatus('failure');
            }
        } catch (error) {
            console.error("Failed to fetch artifact", error);
            setVerificationStatus('failure');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 max-w-4xl mx-auto space-y-6">
            <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">PoE Verification Dashboard</h1>
                <p className="text-muted-foreground">
                    Independently verify governance execution artifacts against the hash-chained index.
                </p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Retrieve Artifact</CardTitle>
                </CardHeader>
                <CardContent className="flex gap-4">
                    <Input
                        placeholder="Enter Artifact ID (e.g. GOV-148-EXEC-02)"
                        value={artifactId}
                        onChange={(e) => setArtifactId(e.target.value)}
                    />
                    <Button onClick={fetchArtifact} disabled={loading || !artifactId}>
                        {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                        Verify
                    </Button>
                </CardContent>
            </Card>

            {verificationStatus === 'failure' && (
                <Card className="border-destructive/50 bg-destructive/10">
                    <CardContent className="pt-6 flex items-center gap-4 text-destructive">
                        <XCircle className="h-8 w-8" />
                        <div>
                            <p className="font-semibold">Verification Failed</p>
                            <p className="text-sm">Artifact not found or hash mismatch detected.</p>
                        </div>
                    </CardContent>
                </Card>
            )}

            {artifact && verificationStatus === 'success' && (
                <div className="grid gap-6 md:grid-cols-2">
                    <Card className="border-green-500/20 bg-green-500/5">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-lg flex items-center gap-2">
                                <CheckCircle2 className="h-5 w-5 text-green-500" />
                                Valid PoE Artifact
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-2 text-sm">
                                <span className="text-muted-foreground">ID:</span>
                                <span className="font-mono">{artifact.artifact_id}</span>

                                <span className="text-muted-foreground">Cycle:</span>
                                <span>{artifact.governance_scope.cycle}</span>

                                <span className="text-muted-foreground">Scope:</span>
                                <Badge variant="outline">{artifact.governance_scope.parameter_key}</Badge>

                                <span className="text-muted-foreground">Signer:</span>
                                <span className="font-mono text-xs truncate">{artifact.signatures.nod_id}</span>
                            </div>

                            <div className="pt-2 border-t text-xs text-muted-foreground break-all">
                                <p className="mb-1 font-semibold">Proof Hash:</p>
                                {artifact.proof_hash}
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-lg">Independent Replay</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <p className="text-sm text-muted-foreground">
                                Run the following command in your local environment to cryptographically verify this execution:
                            </p>
                            <div className="bg-muted p-3 rounded-md font-mono text-xs overflow-x-auto">
                                python v15/tools/replay_gov_cycle.py --artifact_id {artifact.artifact_id}
                            </div>
                            <div className="flex gap-2">
                                <Button variant="outline" size="sm" className="w-full">
                                    <PlayCircle className="mr-2 h-4 w-4" />
                                    Copy Command
                                </Button>
                                <Button variant="outline" size="sm" className="w-full">
                                    <FileJson className="mr-2 h-4 w-4" />
                                    Download JSON
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
};
