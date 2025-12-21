'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Bell, Shield, Wallet, Zap, Clock, CheckCircle2, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Notification {
    id: string;
    type: 'reward' | 'security' | 'system' | 'mention';
    title: string;
    message: string;
    timestamp: number;
    read: boolean;
    data?: any;
}

export function NotificationPanel() {
    const queryClient = useQueryClient();

    // Fetch notifications from API
    const { data: notifications = [], isLoading } = useQuery<Notification[]>({
        queryKey: ['notifications'],
        queryFn: async () => {
            const res = await fetch('/api/v18/notifications');
            if (!res.ok) throw new Error('Failed to fetch notifications');
            return res.json();
        },
        refetchInterval: 30000, // Refresh every 30 seconds
    });

    // Mark all as read mutation
    const markReadMutation = useMutation({
        mutationFn: async () => {
            const unreadIds = notifications.filter(n => !n.read).map(n => n.id);
            const res = await fetch('/api/v18/notifications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    notificationIds: unreadIds,
                    action: 'markRead'
                })
            });
            if (!res.ok) throw new Error('Failed to mark as read');
            return res.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
        }
    });

    const markAllRead = () => {
        markReadMutation.mutate();
    };

    const getIcon = (type: string) => {
        switch (type) {
            case 'reward': return <Wallet className="h-4 w-4 text-green-500" />;
            case 'security': return <Shield className="h-4 w-4 text-blue-500" />;
            case 'system': return <Zap className="h-4 w-4 text-purple-500" />;
            default: return <Bell className="h-4 w-4 text-muted-foreground" />;
        }
    };

    return (
        <Card className="w-80 shadow-2xl border-primary/10 bg-card/95 backdrop-blur-md">
            <CardHeader className="p-4 pb-2 border-b">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-bold flex items-center gap-2">
                        <Bell className="h-4 w-4" />
                        Notifications
                    </CardTitle>
                    <button
                        onClick={markAllRead}
                        className="text-[10px] text-primary hover:underline font-semibold"
                    >
                        Mark all read
                    </button>
                </div>
            </CardHeader>
            <CardContent className="p-0">
                <ScrollArea className="h-80">
                    <div className="divide-y divide-border">
                        {notifications.length === 0 ? (
                            <div className="p-8 text-center text-muted-foreground">
                                <p className="text-xs italic">No new signals</p>
                            </div>
                        ) : notifications.map(n => (
                            <div
                                key={n.id}
                                className={cn(
                                    "p-4 hover:bg-muted/50 transition-colors cursor-pointer relative",
                                    !n.read && "bg-primary/[0.03]"
                                )}
                            >
                                {!n.read && <div className="absolute top-4 right-4 w-2 h-2 bg-blue-600 rounded-full" />}
                                <div className="flex gap-3">
                                    <div className="mt-1">{getIcon(n.type)}</div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-xs font-bold leading-tight mb-1">{n.title}</p>
                                        <p className="text-[11px] text-muted-foreground leading-snug line-clamp-2">
                                            {n.message}
                                        </p>
                                        <div className="flex items-center gap-1.5 mt-2">
                                            <Clock className="h-3 w-3 text-muted-foreground" />
                                            <span className="text-[9px] text-muted-foreground uppercase font-medium">
                                                {new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </ScrollArea>
            </CardContent>
            <div className="p-2 border-t bg-muted/30 text-center">
                <button className="text-[10px] font-bold text-muted-foreground hover:text-foreground">
                    View Audit Ledger
                </button>
            </div>
        </Card>
    );
}
