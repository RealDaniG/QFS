'use client'

import { useFeed } from '@/hooks/useFeed'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function Feed() {
    const { events, isLoading, error } = useFeed()

    if (isLoading && events.length === 0) {
        return <div className="p-4 text-center text-muted-foreground">Loading feed...</div>
    }

    if (error) {
        return <div className="p-4 text-center text-red-500">Error loading feed: {error.message}</div>
    }

    return (
        <Card className="w-full h-full border-none shadow-none">
            <CardHeader>
                <CardTitle>Activity Feed</CardTitle>
                <CardDescription>
                    Real-time events pending ledger confirmation
                </CardDescription>
            </CardHeader>
            <CardContent>
                <ScrollArea className="h-[600px] pr-4">
                    <div className="space-y-4">
                        {events.length === 0 ? (
                            <div className="text-center py-8 text-muted-foreground">
                                No activity yet. Create some content!
                            </div>
                        ) : (
                            events.map((event) => (
                                <Card key={event.id} className="overflow-hidden">
                                    <div className="p-4 space-y-3">
                                        <div className="flex items-center justify-between">
                                            <Badge variant="outline" className="font-mono text-xs">
                                                {event.eventType}
                                            </Badge>
                                            <div className="flex items-center text-xs text-muted-foreground">
                                                <Clock className="w-3 h-3 mr-1" />
                                                {formatDistanceToNow(event.timestamp, { addSuffix: true })}
                                            </div>
                                        </div>

                                        <div className="space-y-1">
                                            <p className="text-sm font-medium">
                                                Event ID: <span className="font-mono text-xs text-muted-foreground">{event.id.slice(0, 8)}...</span>
                                            </p>
                                            <div className="text-sm text-muted-foreground break-all">
                                                {/* Display specific event data based on type */}
                                                {event.eventType === 'ContentCreated' && (
                                                    <span>
                                                        Created content CID: <span className="font-mono text-xs bg-muted px-1 rounded">
                                                            {(event.eventData as any).contentCID?.slice(0, 16)}...
                                                        </span>
                                                    </span>
                                                )}
                                                {event.eventType === 'ProfileUpdated' && (
                                                    <span>
                                                        Updated profile
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex items-center justify-between pt-2 border-t">
                                            <div className="flex items-center text-xs">
                                                Status:
                                                <Badge
                                                    variant={event.status === 'confirmed' ? 'default' : 'secondary'}
                                                    className="ml-2 capitalize"
                                                >
                                                    {event.status}
                                                </Badge>
                                            </div>
                                            <div className="text-xs text-muted-foreground font-mono">
                                                {event.did.slice(0, 12)}...
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                            ))
                        )}
                    </div>
                </ScrollArea>
            </CardContent>
        </Card>
    )
}
