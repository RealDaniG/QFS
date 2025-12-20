"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ExplainThisPanel } from "./ExplainThisPanel";
import { useExplainReward } from "@/hooks/useExplainReward";
import { useWalletAuth } from "@/hooks/useWalletAuth";
import { Loader2, AlertCircle, Shield } from "lucide-react";
import { WalletConnectButton } from "./WalletConnectButton";

export function ExplainRewardFlow() {
  const { isConnected } = useWalletAuth();
  const [walletId, setWalletId] = useState("");
  const [epoch, setEpoch] = useState<number | undefined>(undefined);
  const [showExplanation, setShowExplanation] = useState(false);

  const {
    data: explanation,
    isLoading,
    error,
    refetch,
  } = useExplainReward(walletId, epoch);

  // Auth Gate: Show connect wallet message if not authenticated
  if (!isConnected) {
    return (
      <div className="space-y-6">
        <Card className="border-blue-500/30 bg-blue-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-600" />
              Reward Explanation Requires Authentication
            </CardTitle>
            <CardDescription>
              Connect your wallet to inspect reward explanations and verify economic calculations.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-background/50 rounded-xl border border-blue-500/20">
              <p className="text-sm text-muted-foreground">
                The Explain Reward feature provides deterministic, auditable explanations for all
                reward calculations in the QFS system. Authentication is required to access this feature.
              </p>
            </div>
            <div className="flex justify-center pt-4">
              <WalletConnectButton />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

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
          explanation={{
            wallet_id: explanation.wallet_id,
            user_id: explanation.wallet_id, // Mapping for compatibility
            reward_event_id: "demo",
            epoch: explanation.epoch,
            timestamp: Date.now(),
            base_reward: { ATR: explanation.base },
            bonuses: explanation.bonuses,
            caps: explanation.caps,
            guards: explanation.guards,
            policy_version: "v18",
            policy_hash: "demo",
            total_reward: { ATR: explanation.total },
            explanation_hash: explanation.metadata.replay_hash,
            reason_codes: [],
          }}
          onClose={() => setShowExplanation(false)}
        />
      )}
    </div>
  );
}
