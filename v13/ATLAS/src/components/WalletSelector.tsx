'use client';

import { useWalletAdapter } from "@/lib/wallet/WalletProvider";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import Image from "next/image";

export function WalletSelector() {
    const { adapters, connect, isConnecting, error } = useWalletAdapter();

    return (
        <div className="w-full space-y-4">
            <div className="grid grid-cols-2 gap-3">
                {adapters.map((adapter) => (
                    <Button
                        key={adapter.id}
                        variant="outline"
                        className="h-24 flex flex-col items-center justify-center space-y-2 hover:bg-slate-50 border-slate-200"
                        onClick={() => connect(adapter.id)}
                        disabled={isConnecting}
                    >
                        {/* 
                           Note: Icons are assumed to be in public/icons or we can use text fallback.
                           For now, we use a simple placeholder or text if image fails 
                        */}
                        <div className="w-8 h-8 relative">
                            {/* Placeholder for real icons */}
                            <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center text-xs">
                                {adapter.name[0]}
                            </div>
                        </div>
                        <span className="font-medium text-slate-700">{adapter.name}</span>
                    </Button>
                ))}
            </div>

            {isConnecting && (
                <div className="flex items-center justify-center text-sm text-blue-600 animate-pulse">
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Connecting to wallet...
                </div>
            )}

            {error && (
                <div className="p-3 bg-red-50 text-red-600 text-xs rounded-md border border-red-100">
                    {error}
                </div>
            )}
        </div>
    );
}
