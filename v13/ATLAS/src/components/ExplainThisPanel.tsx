"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface ExplainThisProps {
  type: "reward" | "ranking";
  data: {
    base?: string;
    bonuses?: Array<{ label: string; value: string; reason: string }>;
    caps?: Array<{ label: string; value: string; reason: string }>;
    guards?: Array<{ name: string; result: "pass" | "fail"; reason: string }>;
    signals?: Array<{ name: string; weight: number; score: number }>;
    neighbors?: Array<{ metric: string; value: number; rank: number }>;
  };
  onClose?: () => void;
}

export function ExplainThisPanel({ type, data, onClose }: ExplainThisProps) {
  return (
    <TooltipProvider>
      <Card className="w-full max-w-2xl">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg font-semibold">
            Explain This: {type === "reward" ? "Reward" : "Ranking"}
          </CardTitle>
          <Badge variant="outline">Read-only</Badge>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              ✕
            </Button>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {type === "reward" && (
            <>
              <div>
                <h4 className="font-medium">Base reward</h4>
                <p className="text-sm text-muted-foreground">{data.base}</p>
              </div>
              {data.bonuses && data.bonuses.length > 0 && (
                <div>
                  <h4 className="font-medium">Bonuses</h4>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {data.bonuses.map((b, i) => (
                      <li key={i} className="flex justify-between">
                        <span>{b.label}</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <span className="font-mono">{b.value}</span>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{b.reason}</p>
                          </TooltipContent>
                        </Tooltip>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {data.caps && data.caps.length > 0 && (
                <div>
                  <h4 className="font-medium">Caps applied</h4>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {data.caps.map((c, i) => (
                      <li key={i} className="flex justify-between">
                        <span>{c.label}</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <span className="font-mono">{c.value}</span>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{c.reason}</p>
                          </TooltipContent>
                        </Tooltip>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {data.guards && data.guards.length > 0 && (
                <div>
                  <h4 className="font-medium">Guard results</h4>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {data.guards.map((g, i) => (
                      <li key={i} className="flex justify-between">
                        <span>{g.name}</span>
                        <Badge variant={g.result === "pass" ? "default" : "destructive"}>
                          {g.result}
                        </Badge>
                        <Tooltip>
                          <TooltipTrigger>
                            <span>ℹ️</span>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{g.reason}</p>
                          </TooltipContent>
                        </Tooltip>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}

          {type === "ranking" && (
            <>
              {data.signals && data.signals.length > 0 && (
                <div>
                  <h4 className="font-medium">Signal breakdown</h4>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {data.signals.map((s, i) => (
                      <li key={i} className="flex justify-between">
                        <span>{s.name}</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <span className="font-mono">
                              {s.weight.toFixed(2)} × {s.score.toFixed(2)}
                            </span>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Weight × Score</p>
                          </TooltipContent>
                        </Tooltip>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {data.neighbors && data.neighbors.length > 0 && (
                <div>
                  <h4 className="font-medium">Neighbor comparison</h4>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {data.neighbors.map((n, i) => (
                      <li key={i} className="flex justify-between">
                        <span>{n.metric}</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <span className="font-mono">
                              {n.value} (rank {n.rank})
                            </span>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Value vs peer rank</p>
                          </TooltipContent>
                        </Tooltip>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}

          <Separator />
          <div className="text-xs text-muted-foreground">
            <p>All values are derived from deterministic replay of QFS events.</p>
            <p>No economic state is mutated by this panel.</p>
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  );
}
