"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface WalletSummary {
  totalValue: string;
  atrBalance: string;
  flxBalance: string;
  reputationScore?: number;
  coherenceScore?: number;
}

interface TransactionList {
  transactions: Array<{
    id: string;
    type: string;
    amount: string;
    timestamp: string;
  }>;
}

interface ValueNodeViewProps {
  walletSummary: WalletSummary;
  transactionList: TransactionList;
}

export function ValueNodeView({ walletSummary, transactionList }: ValueNodeViewProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">User-as-Value-Node Overview</CardTitle>
          <Badge variant="outline">Read-only projection</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium">Total Value</h4>
              <p className="text-2xl font-mono">{walletSummary.totalValue}</p>
            </div>
            <div>
              <h4 className="font-medium">ATR Balance</h4>
              <p className="text-2xl font-mono">{walletSummary.atrBalance}</p>
            </div>
            <div>
              <h4 className="font-medium">FLX Balance</h4>
              <p className="text-2xl font-mono">{walletSummary.flxBalance}</p>
            </div>
            {walletSummary.reputationScore !== undefined && (
              <div>
                <h4 className="font-medium">Reputation</h4>
                <p className="text-2xl font-mono">{walletSummary.reputationScore}</p>
              </div>
            )}
            {walletSummary.coherenceScore !== undefined && (
              <div>
                <h4 className="font-medium">Coherence</h4>
                <p className="text-2xl font-mono">{walletSummary.coherenceScore}</p>
              </div>
            )}
          </div>
          <Separator />
          <div>
            <h4 className="font-medium mb-2">Recent Transactions</h4>
            <ul className="space-y-1 text-sm">
              {transactionList.transactions.slice(0, 5).map((tx) => (
                <li key={tx.id} className="flex justify-between">
                  <span>{tx.type}</span>
                  <span className="font-mono">{tx.amount}</span>
                </li>
              ))}
            </ul>
          </div>
          <Separator />
          <div className="text-xs text-muted-foreground">
            <p>All values are derived from deterministic replay of QFS events.</p>
            <p>No economic state is mutated by this view.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
