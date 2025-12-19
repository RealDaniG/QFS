'use client';

import { useWalletAuth } from '@/hooks/useWalletAuth';
import { Button } from '@/components/ui/button';
import { Loader2, Wallet, LogOut } from 'lucide-react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function WalletConnectButton() {
    const { isConnected, address, isLoading, error, connect, logout } = useWalletAuth();

    if (isLoading) {
        return (
            <Button disabled variant="outline">
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Connecting...
            </Button>
        );
    }

    if (isConnected && address) {
        return (
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button variant="outline" className="border-blue-500/20 bg-blue-500/10 text-blue-600 hover:bg-blue-500/20">
                        <Wallet className="mr-2 h-4 w-4" />
                        {address.slice(0, 6)}...{address.slice(-4)}
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Account</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-muted-foreground font-mono text-xs">
                        {address}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={logout} className="text-red-600 cursor-pointer">
                        <LogOut className="mr-2 h-4 w-4" />
                        Disconnect
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        );
    }

    return (
        <div className="flex flex-col items-end gap-2">
            <Button onClick={connect} variant="default" className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg shadow-blue-500/25">
                <Wallet className="mr-2 h-4 w-4" />
                Connect Wallet
            </Button>
            {error && (
                <span className="text-xs text-red-500 bg-red-50 px-2 py-1 rounded border border-red-100">
                    {error}
                </span>
            )}
        </div>
    );
}
