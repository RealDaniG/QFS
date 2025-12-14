import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertTriangle, CheckCircle, FileText, Activity, Lock, Database } from "lucide-react";

interface AuditLogEntry {
    id: string;
    timestamp: string;
    type: "REWARD" | "STORAGE" | "CONTRACT" | "SIGNAL";
    severity: "INFO" | "WARNING" | "CRITICAL";
    actor_did: string;
    action: string;
    integrity_hash: string;
    verified: boolean;
}

const DEMO_LOGS: AuditLogEntry[] = [
    { id: "evt_1", timestamp: "2025-12-14T18:00:00Z", type: "CONTRACT", severity: "INFO", actor_did: "did:key:zAdmin", action: "Upgraded Contract to V1.3", integrity_hash: "sha256-abc...", verified: true },
    { id: "evt_2", timestamp: "2025-12-14T18:05:00Z", type: "SIGNAL", severity: "INFO", actor_did: "did:key:zAES", action: "Registered ArtisticSignalAddon", integrity_hash: "sha256-def...", verified: true },
    { id: "evt_3", timestamp: "2025-12-14T18:10:00Z", type: "REWARD", severity: "WARNING", actor_did: "did:key:zSystem", action: "Cap Applied to Wallet 0x123", integrity_hash: "sha256-ghi...", verified: true },
    { id: "evt_4", timestamp: "2025-12-14T18:15:00Z", type: "STORAGE", severity: "INFO", actor_did: "did:key:zNode1", action: "Storage Proof Verified", integrity_hash: "sha256-jkl...", verified: true },
];

export const GovernanceAuditDashboard: React.FC = () => {
    const [logs, setLogs] = useState<AuditLogEntry[]>(DEMO_LOGS);

    // In a real implementation, this would fetch from /api/governance/audit-log

    return (
        <div className="w-full h-full p-6 space-y-6 bg-zinc-950 text-zinc-100 font-sans">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-white">Governance Audit</h1>
                    <p className="text-zinc-400">Zero-Simulation Compliance & Operational Logs</p>
                </div>
                <div className="flex gap-2">
                    <Badge variant="outline" className="border-emerald-800 text-emerald-400 bg-emerald-950/30">
                        <CheckCircle className="w-3 h-3 mr-1" /> System Healthy
                    </Badge>
                    <Badge variant="outline" className="border-blue-800 text-blue-400 bg-blue-950/30">
                        <Lock className="w-3 h-3 mr-1" /> Contract V1.3 Active
                    </Badge>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <Card className="bg-zinc-900 border-zinc-800">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-zinc-400">Zero-Sim Violations</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">0</div>
                        <p className="text-xs text-zinc-500">Last scan: 5 mins ago</p>
                    </CardContent>
                </Card>
                <Card className="bg-zinc-900 border-zinc-800">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-zinc-400">Active Signals</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">2</div>
                        <p className="text-xs text-zinc-500">Humor V1, Artistic V13.8</p>
                    </CardContent>
                </Card>
                <Card className="bg-zinc-900 border-zinc-800">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-zinc-400">Immutable Ledger Height</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">1,402,854</div>
                        <p className="text-xs text-zinc-500">Epoch 42</p>
                    </CardContent>
                </Card>
            </div>

            <Card className="bg-zinc-900 border-zinc-800 text-zinc-100">
                <CardHeader>
                    <CardTitle>Operational Audit Log</CardTitle>
                    <CardDescription>Immutable record of system actions, verified by AEGIS.</CardDescription>
                </CardHeader>
                <CardContent>
                    <Tabs defaultValue="all" className="w-full">
                        <TabsList className="bg-zinc-950 border border-zinc-800 mb-4">
                            <TabsTrigger value="all">All Events</TabsTrigger>
                            <TabsTrigger value="critical">Critical</TabsTrigger>
                            <TabsTrigger value="warnings">Warnings</TabsTrigger>
                        </TabsList>

                        <TabsContent value="all" className="mt-0">
                            <ScrollArea className="h-[400px] w-full rounded-md border border-zinc-800 p-4">
                                <div className="space-y-4">
                                    {logs.map((log) => (
                                        <div key={log.id} className="flex items-start justify-between p-3 rounded bg-zinc-950/50 border border-zinc-800/50 hover:bg-zinc-900 transition-colors">
                                            <div className="flex gap-4">
                                                <div className="mt-1">
                                                    {log.type === "REWARD" && <Activity className="w-4 h-4 text-purple-400" />}
                                                    {log.type === "STORAGE" && <Database className="w-4 h-4 text-blue-400" />}
                                                    {log.type === "CONTRACT" && <FileText className="w-4 h-4 text-yellow-400" />}
                                                    {log.type === "SIGNAL" && <Activity className="w-4 h-4 text-pink-400" />}
                                                </div>
                                                <div>
                                                    <p className="text-sm font-medium text-white">{log.action}</p>
                                                    <div className="flex items-center gap-2 mt-1">
                                                        <Badge variant="secondary" className="text-[10px] h-4 px-1">{log.type}</Badge>
                                                        <span className="text-xs text-zinc-500 font-mono">{log.timestamp}</span>
                                                        <span className="text-xs text-zinc-600 font-mono">Actor: {log.actor_did}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex flex-col items-end gap-1">
                                                {log.verified && (
                                                    <Badge variant="outline" className="text-[10px] text-emerald-500 border-emerald-900 bg-emerald-950/20">
                                                        VERIFIED
                                                    </Badge>
                                                )}
                                                <span className="text-[10px] font-mono text-zinc-700">{log.integrity_hash.slice(0, 8)}...</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </ScrollArea>
                        </TabsContent>
                    </Tabs>
                </CardContent>
            </Card>
        </div>
    );
};
