'use client'

import { useState } from 'react'
import {
    TrendingUp,
    Activity,
    Eye,
    ChevronRight,
    MessageSquare,
    Users,
    Wallet
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Input } from '@/components/ui/input'
import { useInteraction } from '@/hooks/useInteraction'
import { useSystemStatus } from '@/hooks/useSystemStatus'
import { useQFSFeed } from '@/hooks/useQFSFeed'
import { useP2PConnection } from '@/hooks/useP2PConnection'
import { useP2PFeed } from '@/hooks/useP2PFeed'
import ContentComposer from '@/components/ContentComposer'
import { GovernanceAuditDashboard } from '@/components/GovernanceAuditDashboard'

export function HomeTab() {
    const { interact } = useInteraction()
    const { status } = useSystemStatus()
    const { feed, loading } = useQFSFeed()
    const { isConnected: p2pConnected, peerId } = useP2PConnection()
    useP2PFeed() // Activate subscriptions
    const [isComposerOpen, setIsComposerOpen] = useState(false)

    return (
        <div className="max-w-4xl mx-auto flex gap-6">
            {/* Main Feed */}
            <div className="flex-1 space-y-6">
                <Card>
                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <Avatar className="h-10 w-10">
                                <AvatarImage src="./avatars/user.jpg" />
                                <AvatarFallback>JD</AvatarFallback>
                            </Avatar>
                            <Input
                                placeholder="Share your thoughts with full transparency..."
                                className="flex-1"
                                readOnly
                            />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Button variant="ghost" size="sm">
                                    <Eye className="h-4 w-4 mr-1" />
                                    Preview Economics
                                </Button>
                            </div>
                            <Button size="sm" data-testid="composer-trigger" onClick={() => setIsComposerOpen(true)}>Create Post</Button>
                        </div>
                    </CardContent>
                </Card>

                {loading ? (
                    <div className="flex justify-center p-12" data-testid="feed-loading">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                ) : feed.length === 0 ? (
                    <Card>
                        <CardContent className="p-12 text-center text-muted-foreground" data-testid="feed-empty">
                            No posts yet. Be the first to share!
                        </CardContent>
                    </Card>
                ) : (
                    feed.map((post) => (
                        <Card key={post.id}>
                            <CardHeader>
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-3">
                                        <Avatar className="h-10 w-10">
                                            <AvatarImage src="./avatars/user.jpg" />
                                            <AvatarFallback>{post.authorDID.slice(0, 2)}</AvatarFallback>
                                        </Avatar>
                                        <div>
                                            <p className="font-medium">{post.authorDID.slice(0, 12)}...</p>
                                            <p className="text-sm text-muted-foreground">{new Date(post.timestamp).toLocaleString()}</p>
                                        </div>
                                    </div>
                                    <Button variant="ghost" size="sm">
                                        <ChevronRight className="h-4 w-4" />
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="mb-4">{post.content.text}</p>

                                <div className="grid grid-cols-2 gap-4 p-3 bg-muted/50 rounded-lg mb-4">
                                    <div className="flex items-center gap-2">
                                        <TrendingUp className="h-4 w-4 text-green-600" />
                                        <div>
                                            <p className="text-xs text-muted-foreground">Coherence Score</p>
                                            <p className="font-semibold text-green-600">{post.coherenceScore.toFixed(2)}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Wallet className="h-4 w-4 text-blue-600" />
                                        <div>
                                            <p className="text-xs text-muted-foreground">Proof</p>
                                            <p className="font-mono text-xs text-blue-600 truncate w-32">{post.proof}</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4">
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => interact('like', `cid://${post.cid}`)}
                                    >
                                        <Activity className="h-4 w-4 mr-1" />
                                        Like
                                    </Button>
                                    <Button variant="ghost" size="sm" className="ml-auto">
                                        <Eye className="h-4 w-4 mr-1" />
                                        Explain
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )))}
            </div>

            {/* Side Bar Info */}
            <div className="w-80 space-y-4 hidden lg:block">
                {/* P2P Status Indicator (New for v19) */}
                <Card>
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${p2pConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
                            P2P Mesh v19
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-muted-foreground">Status</span>
                            <Badge variant={p2pConnected ? "default" : "secondary"} className="text-xs">
                                {p2pConnected ? 'Connected' : 'Connecting...'}
                            </Badge>
                        </div>
                        {p2pConnected && (
                            <div className="flex flex-col gap-1">
                                <span className="text-xs text-muted-foreground">Peer ID</span>
                                <span className="text-xs font-mono break-all bg-muted p-1 rounded">{peerId}</span>
                            </div>
                        )}
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-muted-foreground">Protocol</span>
                            <Badge variant="outline" className="text-xs">WebSockets / GossipSub</Badge>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm">System Status</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-muted-foreground">Backend</span>
                            <Badge
                                variant={status.backend === 'online' ? "default" : "destructive"}
                                className="text-xs"
                            >
                                {status.backend === 'online' ? 'Operational' : 'Offline'}
                            </Badge>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-muted-foreground">Port</span>
                            <Badge variant="outline" className="text-xs">{status.port}</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-muted-foreground">Version</span>
                            <Badge variant="outline" className="text-xs">{status.version}</Badge>
                        </div>
                        <div className="pt-2 border-t">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Evidence Head</span>
                                <Activity className="h-3 w-3 text-primary animate-pulse" />
                            </div>
                            <p className="text-sm font-mono break-all text-muted-foreground bg-muted p-1 rounded">
                                {status.headHash.slice(0, 16)}...
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <ContentComposer isOpen={isComposerOpen} onClose={() => setIsComposerOpen(false)} data-testid="composer-dialog" />
        </div>
    )
}
