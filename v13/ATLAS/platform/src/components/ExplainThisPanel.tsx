"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  ValueNodeRewardExplanation,
  ContentRankingExplanation,
  SimplifiedExplanation,
  formatExplanationSummary,
  getBadgeForReasonCode
} from "@/lib/qfs/explain-this";

// Define a unified props interface that accepts either raw explanation or simplified view
interface ExplainThisProps {
  type: "reward" | "ranking";
  explanation?: ValueNodeRewardExplanation | ContentRankingExplanation | SimplifiedExplanation;
  onClose?: () => void;
  isLoading?: boolean;
}

export function ExplainThisPanel({ type, explanation, onClose, isLoading }: ExplainThisProps) {
  if (isLoading) {
    return (
      <Card className="w-full max-w-2xl animate-pulse">
        <CardHeader><div className="h-6 bg-muted rounded w-1/3"></div></CardHeader>
        <CardContent><div className="h-24 bg-muted rounded"></div></CardContent>
      </Card>
    );
  }

  if (!explanation) {
    return null;
  }

  // Helper to safely access common fields whether it's simplified or raw
  // In a real app we might want strict type guards, but for now we trust the "type" prop
  const isReward = type === "reward";
  const isRanking = type === "ranking";

  // Cast to specific types for easier access
  const rewardData = isReward ? (explanation as any) : null;
  const rankingData = isRanking ? (explanation as any) : null;

  // Handle simplified structure vs raw structure
  const base = rewardData?.breakdown?.base_reward?.ATR || rewardData?.base_reward?.ATR;
  const bonuses = rewardData?.breakdown?.bonuses || rewardData?.bonuses;
  const caps = rewardData?.breakdown?.caps || rewardData?.caps;
  const guards = rewardData?.breakdown?.guards || rewardData?.guards;

  const signals = rankingData?.signals;
  const neighbors = rankingData?.neighbors;

  const hash = (explanation as any).verification?.hash || (explanation as any).explanation_hash || "unknown";

  return (
    <TooltipProvider>
      <Card className="w-full max-w-2xl shadow-lg border-2 border-primary/10">
        <CardHeader className="flex flex-row items-center justify-between bg-muted/20 pb-4">
          <div className="flex items-center gap-3">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              Explain This: {isReward ? "Reward" : "Ranking"}
            </CardTitle>
            <Badge variant="outline" className="font-mono text-xs">
              Hash: {hash.slice(0, 8)}...
            </Badge>
          </div>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose} className="hover:bg-destructive/10 hover:text-destructive">
              ✕
            </Button>
          )}
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          {isReward && (
            <>
              {/* Base Reward Section */}
              <div className="bg-muted/30 p-3 rounded-lg">
                <h4 className="font-medium text-sm text-muted-foreground mb-1">Base Reward</h4>
                <div className="text-2xl font-bold font-mono text-primary">{base}</div>
              </div>

              {/* Bonuses Section */}
              {bonuses && bonuses.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                    Bonuses <Badge variant="secondary" className="text-[10px]">{bonuses.length}</Badge>
                  </h4>
                  <ul className="space-y-2">
                    {bonuses.map((b: any, i: number) => (
                      <li key={i} className="flex justify-between items-center text-sm p-2 rounded hover:bg-muted/50 transition-colors">
                        <span className="font-medium">{b.label}</span>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-green-600 font-bold">{b.value}</span>
                          <Tooltip>
                            <TooltipTrigger>
                              <span className="text-muted-foreground cursor-help text-xs">Why?</span>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>{b.reason}</p>
                            </TooltipContent>
                          </Tooltip>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Caps Section */}
              {caps && caps.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2 flex items-center gap-2">Caps Applied</h4>
                  <ul className="space-y-2">
                    {caps.map((c: any, i: number) => (
                      <li key={i} className="flex justify-between items-center text-sm p-2 bg-red-50/50 dark:bg-red-900/10 rounded">
                        <span className="text-destructive/80">{c.label}</span>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-destructive font-bold">{c.value}</span>
                          <Tooltip>
                            <TooltipTrigger>
                              <span className="text-muted-foreground cursor-help text-xs">Why?</span>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>{c.reason}</p>
                            </TooltipContent>
                          </Tooltip>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Guards Section */}
              {guards && guards.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Guard Checks</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {guards.map((g: any, i: number) => (
                      <div key={i} className="flex items-center justify-between p-2 border rounded text-sm">
                        <span>{g.name}</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <Badge variant={g.result === "pass" ? "outline" : "destructive"} className={g.result === "pass" ? "border-green-500 text-green-600" : ""}>
                              {g.result.toUpperCase()}
                            </Badge>
                          </TooltipTrigger>
                          <TooltipContent><p>{g.reason}</p></TooltipContent>
                        </Tooltip>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {isRanking && (
            <>
              {/* Signals Section */}
              {signals && signals.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Ranking Signals</h4>
                  <div className="space-y-3">
                    {signals.map((s: any, i: number) => (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="font-medium">{s.name}</span>
                          <span className="font-mono text-xs text-muted-foreground">
                            W: {s.weight.toFixed(2)} × S: {s.score.toFixed(2)}
                          </span>
                        </div>
                        <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                          <div className="h-full bg-blue-500 transition-all" style={{ width: `${s.score * 100}%`, opacity: s.weight }}></div>
                        </div>
                        <p className="text-xs text-muted-foreground text-right">{s.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Neighbors Section */}
              {neighbors && neighbors.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium text-sm mb-2">Context (Neighbors)</h4>
                  <div className="rounded-md border divide-y">
                    {neighbors.map((n: any, i: number) => (
                      <div key={i} className="p-2 flex justify-between text-sm">
                        <span>{n.metric}</span>
                        <span className="font-mono">Rank #{n.rank} (Val: {n.value})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          <Separator />
          <div className="text-[10px] text-muted-foreground space-y-1 font-mono">
            <div className="flex justify-between">
              <span>Source:</span>
              <span>Deterministic Replay (Zero-Sim)</span>
            </div>
            <div className="flex justify-between">
              <span>Computed At:</span>
              <span>{(explanation as any).timestamp || (explanation as any).metadata?.computed_at || "Now"}</span>
            </div>
            <div className="flex justify-between">
              <span>Policy Version:</span>
              <span>{(explanation as any).policy_version || "unknown"}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  );
}
