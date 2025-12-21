'use client'

import dynamic from 'next/dynamic'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, BookOpen, Shield, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { EvidenceLog } from '@/components/EvidenceLog'

const ExplainRewardFlow = dynamic(() => import('@/components/ExplainRewardFlow').then(m => m.ExplainRewardFlow), { ssr: false })

export function LedgerTab() {
    return (
        <div className="max-w-6xl mx-auto space-y-6 p-6">
            <ExplainRewardFlow />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                    <EvidenceLog />
                </div>

                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Event Ledger & Explainability</CardTitle>
                        <CardDescription>
                            Complete transparency of all system events and decisions.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-4 bg-muted/50 rounded-lg">
                                <div className="flex items-center gap-2 mb-2">
                                    <BookOpen className="h-5 w-5 text-green-600" />
                                    <span className="font-medium">Per-Object Ledger</span>
                                </div>
                                <p className="text-sm text-muted-foreground">Mini-chains of events for specific content or actions.</p>
                            </div>
                            <div className="p-4 bg-muted/50 rounded-lg">
                                <div className="flex items-center gap-2 mb-2">
                                    <Shield className="h-5 w-5 text-purple-600" />
                                    <span className="font-medium">Simulation Log</span>
                                </div>
                                <p className="text-sm text-muted-foreground">What-if scenarios and AGI proposals.</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
