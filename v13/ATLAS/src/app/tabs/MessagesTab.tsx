'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import MessagingInterface from '@/components/MessagingInterface'

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
