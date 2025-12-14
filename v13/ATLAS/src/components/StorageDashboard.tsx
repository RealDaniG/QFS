"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";

interface StorageDashboardProps {
  metrics: {
    epoch: number;
    bytesStoredPerNode: Record<string, string>;
    proofsGeneratedPerNode: Record<string, number>;
    proofFailures: number;
  };
}

export function StorageDashboard({ metrics }: StorageDashboardProps) {
  const totalBytes = Object.values(metrics.bytesStoredPerNode).reduce(
    (sum, v) => sum + Number(v),
    0
  );
  const totalProofs = Object.values(metrics.proofsGeneratedPerNode).reduce(
    (sum, v) => sum + v,
    0
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Storage Observability (Epoch {metrics.epoch})</CardTitle>
          <Badge variant="outline">Read-only</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium">Total bytes stored</h4>
              <p className="text-2xl font-mono">{totalBytes.toLocaleString()}</p>
            </div>
            <div>
              <h4 className="font-medium">Proofs generated</h4>
              <p className="text-2xl font-mono">{totalProofs.toLocaleString()}</p>
            </div>
          </div>
          <Separator />
          <div>
            <h4 className="font-medium mb-2">Proof failures</h4>
            <p className="text-sm text-muted-foreground">{metrics.proofFailures} failures this epoch</p>
          </div>
          <Separator />
          <div>
            <h4 className="font-medium mb-2">Per-node health</h4>
            <div className="space-y-2">
              {Object.entries(metrics.bytesStoredPerNode).map(([nodeId, bytes]) => {
                const proofs = metrics.proofsGeneratedPerNode[nodeId] || 0;
                const bytesNum = Number(bytes);
                const maxBytes = Math.max(
                  ...Object.values(metrics.bytesStoredPerNode).map(Number)
                );
                const percent = maxBytes > 0 ? (bytesNum / maxBytes) * 100 : 0;
                return (
                  <div key={nodeId} className="flex items-center justify-between">
                    <span className="text-sm font-mono">{nodeId}</span>
                    <div className="flex items-center space-x-2">
                      <Progress value={percent} className="w-20" />
                      <span className="text-xs text-muted-foreground">
                        {bytesNum.toLocaleString()} / {proofs} proofs
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <Separator />
          <div className="text-xs text-muted-foreground">
            <p>All metrics are replay-derived from StorageEvents; no economic state is shown.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
