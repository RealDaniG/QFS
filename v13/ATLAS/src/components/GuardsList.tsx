
'use client';

import { useEffect, useState } from 'react';
import { getGuardRegistry, Guard } from '@/lib/guards/registry';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ShieldAlert, ShieldCheck } from 'lucide-react';

export default function GuardsList() {
    const [guards, setGuards] = useState<Guard[]>([]);

    useEffect(() => {
        // In a real app we might fetch this from an API
        setGuards(getGuardRegistry().getAllGuards());
    }, []);

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <ShieldCheck className="h-5 w-5 text-green-600" />
                    Active Security Guards
                </CardTitle>
                <CardDescription>
                    These autonomous agents protect the network from spam, sybil attacks, and low-coherence content.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {guards.length === 0 ? (
                        <div className="text-muted-foreground text-sm">No active guards loaded.</div>
                    ) : (
                        guards.map(guard => (
                            <div key={guard.id} className="flex items-start justify-between p-3 border rounded-lg bg-muted/20">
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <h4 className="font-semibold text-sm">{guard.name}</h4>
                                        <Badge variant="outline" className="text-xs">{guard.version}</Badge>
                                    </div>
                                    <p className="text-sm text-muted-foreground">{guard.description}</p>
                                </div>
                                <div className="text-xs font-mono text-muted-foreground bg-muted px-2 py-1 rounded">
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
