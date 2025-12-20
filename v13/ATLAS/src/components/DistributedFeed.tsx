'use client';

import { useQFSFeed } from '@/hooks/useQFSFeed';
import { useWalletAuth } from '@/hooks/useWalletAuth';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Shield, CheckCircle2, Server, Lock } from 'lucide-react';

export default function DistributedFeed() {
    const { isConnected } = useWalletAuth();
    const { feed, loading, nodes, selectedNode, selectNode } = useQFSFeed();

    // Show public feed mode when unauthenticated
    if (!isConnected) {
        return (
            <div className="space-y-6">
                <Card className="border-blue-500/30 bg-blue-500/5">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Lock className="h-5 w-5 text-blue-600" />
                            Public Feed Mode
                        </CardTitle>
                        <CardDescription>
                            Connect your wallet to see your personalized distributed feed from trusted QFS nodes.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="p-4 bg-background/50 rounded-xl border border-blue-500/20">
                                <p className="text-sm text-muted-foreground">
                                    The distributed feed shows content verified across multiple QFS nodes.
                                    Authentication is required to participate and view node-specific content.
                                </p>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                <Shield className="h-4 w-4 text-green-500" />
                                <span>All content is cryptographically verified</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }


    return (
        <div className="space-y-6">
            {/* Node Selector */}
            <Card className="bg-muted/30">
                <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Server className="h-5 w-5 text-primary" />
                            <CardTitle className="text-lg">QFS Node Network</CardTitle>
                        </div>
                        <Select
                            value={selectedNode.nodeDID}
                            onValueChange={(did) => {
                                const node = nodes.find(n => n.nodeDID === did);
                                if (node) selectNode(node);
                            }}
                        >
                            <SelectTrigger className="w-[280px]">
                                <SelectValue placeholder="Select a trusted node" />
                            </SelectTrigger>
                            <SelectContent>
                                {nodes.map(node => (
                                    <SelectItem key={node.nodeDID} value={node.nodeDID}>
                                        <div className="flex items-center gap-2">
                                            <Shield className="h-3 w-3 text-green-500" />
                                            <span className="font-mono">{node.nodeDID.slice(0, 16)}...</span>
                                        </div>
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <CardDescription>
                        You are viewing the content reality computed by <strong>{selectedNode.nodeDID.slice(0, 12)}...</strong>.
                        Verifiable by Merkle Proofs.
                    </CardDescription>
                </CardHeader>
            </Card>

            {/* Feed Content */}
            <div className="space-y-4">
                {loading ? (
                    <div className="text-center py-10">Connecting to distributed node...</div>
                ) : feed.map(item => (
                    <Card key={item.id}>
                        <CardContent className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <Avatar>
                                        <AvatarFallback>{item.authorDID.slice(8, 10).toUpperCase()}</AvatarFallback>
                                    </Avatar>
                                    <div>
                                        <div className="font-medium">{item.authorDID}</div>
                                        <div className="text-xs text-muted-foreground">
                                            {new Date(item.timestamp).toLocaleTimeString()}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex flex-col items-end gap-1">
                                    <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                                        Coherence: {item.coherenceScore.toFixed(3)}
                                    </Badge>
                                    <div className="text-[10px] text-muted-foreground flex items-center gap-1">
                                        <CheckCircle2 className="h-3 w-3" />
                                        Verified Proof
                                    </div>
                                </div>
                            </div>

                            <p className="text-base mb-4">{item.content.text}</p>

                            <div className="p-2 bg-muted/50 rounded text-xs font-mono text-muted-foreground break-all">
                                Proof Root: {item.proof}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
