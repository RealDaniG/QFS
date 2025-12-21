'use client'

import dynamic from 'next/dynamic'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const MessagingInterface = dynamic(() => import('@/components/MessagingInterface'), {
    ssr: false,
    loading: () => <div className="h-[600px] flex items-center justify-center bg-muted/20 animate-pulse rounded-lg">Loading Secure Messaging...</div>
})

export function MessagesTab() {
    return (
        <div className="max-w-6xl mx-auto">
            <Card className="h-[600px] overflow-hidden">
                <CardHeader className="pb-3 px-6 pt-6">
                    <CardTitle>Messages</CardTitle>
                    <CardDescription>
                        Private and group messaging with full transparency and end-to-end encryption.
                    </CardDescription>
                </CardHeader>
                <CardContent className="p-0 h-full">
                    <MessagingInterface />
                </CardContent>
            </Card>
        </div>
    )
}
