'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import DiscoveryInterface from '@/components/DiscoveryInterface'

export function CommunitiesTab() {
    return (
        <div className="max-w-6xl mx-auto">
            <Card>
                <CardHeader className="pb-3 px-6 pt-6">
                    <CardTitle>Communities</CardTitle>
                    <CardDescription>
                        Explore and join communities with full transparency and encryption.
                    </CardDescription>
                </CardHeader>
                <CardContent className="p-0 h-full">
                    <DiscoveryInterface />
                </CardContent>
            </Card>
        </div>
    )
}
