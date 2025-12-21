'use client';

import { useEffect, useState } from 'react';
import { getGuardRegistry, Guard } from '@/lib/guards/registry';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ShieldCheck } from 'lucide-react';

export default function GuardsList() {
    const [guards, setGuards] = useState<Guard[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        let mounted = true;
        const loadGuards = async () => {
            try {
                const registry = getGuardRegistry();
                const all = await registry.getAllGuards();
                if (mounted) {
                    setGuards(all);
                    setIsLoading(false);
                }
            } catch (e) {
                console.error("Failed to load guards:", e);
                if (mounted) setIsLoading(false);
            }
        };

        loadGuards();
        return () => { mounted = false; };
    }, []);

    return (
        <Card className="border-none shadow-sm">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <ShieldCheck className="h-5 w-5 text-blue-600" />
                    v18 Security Guards
                </CardTitle>
                <CardDescription>
                    Autonomous v18 agents ensuring deterministic compliance and economic safety.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {isLoading ? (
                        <div className="flex items-center gap-2 text-muted-foreground animate-pulse">
                            <div className="w-4 h-4 rounded-full bg-muted"></div>
                            <span className="text-sm">Initializing guards...</span>
                        </div>
                    ) : guards.length === 0 ? (
                        <div className="text-muted-foreground text-sm italic">No active guards found in current cluster.</div>
                    ) : (
                        guards.map(guard => (
                            <div key={guard.id} className="flex items-start justify-between p-4 border rounded-xl bg-muted/5 hover:bg-muted/10 transition-colors">
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <h4 className="font-bold text-sm">{guard.name}</h4>
                                        <Badge variant="outline" className="text-[10px] uppercase font-bold tracking-tighter h-5">{guard.version}</Badge>
                                    </div>
                                    <p className="text-xs text-muted-foreground leading-relaxed">{guard.description}</p>
                                </div>
                                <div className="text-[10px] font-mono text-muted-foreground bg-muted px-2 py-1 rounded-md opacity-60">
                                    {guard.id}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
