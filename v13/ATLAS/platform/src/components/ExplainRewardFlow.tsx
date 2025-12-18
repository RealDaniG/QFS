"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ExplainThisPanel } from "./ExplainThisPanel";
import { useExplainReward } from "@/hooks/useExplainReward";
import { Loader2, AlertCircle } from "lucide-react";

export function ExplainRewardFlow() {
  const [walletId, setWalletId] = useState("");
  const [epoch, setEpoch] = useState<number | undefined>(undefined);
  const [showExplanation, setShowExplanation] = useState(false);

  const {
    data: explanation,
    isLoading,
    error,
    refetch,
  } = useExplainReward(walletId, epoch);

  const handleExplain = () => {
    if (walletId.trim()) {
      setShowExplanation(true);
      refetch();
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Explain Reward (End-to-End Demo)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="walletId">Wallet ID</Label>
              <Input
                id="walletId"
                value={walletId}
                onChange={(e) => setWalletId(e.target.value)}
                placeholder="e.g., wallet_123"
              />
            </div>
            <div>
              <Label htmlFor="epoch">Epoch (optional)</Label>
              <Input
                id="epoch"
                type="number"
                value={epoch ?? ""}
                onChange={(e) => setEpoch(e.target.value ? Number(e.target.value) : undefined)}
                placeholder="e.g., 1"
              />
            </div>
          </div>
          <Button onClick={handleExplain} disabled={!walletId.trim() || isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Explain Reward
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">Failed to load explanation. Please try again.</span>
            </div>
          </CardContent>
        </Card>
      )}

      {showExplanation && explanation && (
        <ExplainThisPanel
          type="reward"
          data={{
            base: explanation.base,
            bonuses: explanation.bonuses,
            caps: explanation.caps,
            guards: explanation.guards,
          }}
          onClose={() => setShowExplanation(false)}
        />
      )}
    </div>
  );
}
