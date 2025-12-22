'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Activity, Database, Clock, Fingerprint } from 'lucide-react'

interface EvidenceEntry {
    id: number
    evidence_hash: string
    event_type: string
    actor_wallet: string
    payload: string
    timestamp: number
    parent_hash?: string
}

export function EvidenceLog() {
    const [entries, setEntries] = useState<EvidenceEntry[]>([])
    const [loading, setLoading] = useState(true)

    const fetchEvidence = async () => {
        try {
            // Use 127.0.0.1:8001 only (standard port)
            const ports = ['8001']
            let data = null
            for (const p of ports) {
                try {
                    const res = await fetch(`http://127.0.0.1:${p}/api/evidence/recent?limit=20`)
                    if (res.ok) {
                        data = await res.json()
                        break
                    }
                } catch (e) { continue }
            }

            if (data) {
                setEntries(data)
            }
        } catch (error) {
            console.error('Failed to fetch evidence:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchEvidence()
        const interval = setInterval(fetchEvidence, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <Card className="h-full border-primary/20 bg-primary/5">
            <CardHeader className="pb-2 border-b border-primary/10">
                <CardTitle className="text-sm font-bold flex items-center gap-2">
                    <Database className="h-4 w-4 text-primary" />
                    EvidenceBus: Append-Only Log
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <ScrollArea className="h-[400px]">
                    <div className="p-4 space-y-4">
                        {loading && entries.length === 0 && (
                            <div className="text-center py-10 text-muted-foreground text-sm">
                                <Activity className="h-8 w-8 animate-pulse mx-auto mb-2 opacity-20" />
                                Synchronizing Ledger...
                            </div>
                        )}
                        {!loading && entries.length === 0 && (
                            <div className="text-center py-10 text-muted-foreground text-sm">
                                No evidence entries recorded yet.
                            </div>
                        )}
                        {entries.map((entry) => (
                            <div
                                key={entry.evidence_hash}
                                className="p-3 bg-background border rounded-lg shadow-sm hover:border-primary/40 transition-colors"
                            >
                                <div className="flex items-start justify-between gap-2 mb-2">
                                    <div className="flex items-center gap-2">
                                        <Badge variant="secondary" className="text-[10px] py-0 px-1.5 uppercase font-bold tracking-wider">
                                            {entry.event_type}
                                        </Badge>
                                        <div className="flex items-center text-[10px] text-muted-foreground">
                                            <Clock className="h-3 w-3 mr-1" />
                                            {new Date(entry.timestamp * 1000).toLocaleTimeString()}
                                        </div>
                                    </div>
                                    <Badge variant="outline" className="text-[9px] font-mono">
                                        #{entry.id}
                                    </Badge>
                                </div>
                                <div className="space-y-1">
                                    <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
                                        <Fingerprint className="h-3 w-3" />
                                        <span className="font-mono truncate max-w-[200px]">{entry.evidence_hash}</span>
                                    </div>
                                    <div className="text-[11px] text-foreground/80 break-all bg-muted/30 p-1.5 rounded mt-1">
                                        <span className="font-bold text-primary/70">ACTOR:</span> {entry.actor_wallet.substring(0, 10)}...
                                        <div className="mt-1 flex flex-wrap gap-1">
                                            <span className="font-bold text-primary/70">PAYLOAD:</span>
                                            <span className="font-mono text-[9px] truncate">
                                                {entry.payload}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </ScrollArea>
                <div className="p-3 border-t border-primary/10 bg-muted/20 text-[10px] text-muted-foreground flex items-center justify-between">
                    <span>V18 Peer Validation: ACTIVE</span>
                    <span className="flex items-center gap-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                        Synchronized
                    </span>
                </div>
            </CardContent>
        </Card>
    )
}
