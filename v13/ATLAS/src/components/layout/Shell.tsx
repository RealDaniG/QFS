'use client'

import React, { useState } from 'react'
import {
    Home,
    PlusCircle,
    MessageSquare,
    Users,
    BookOpen,
    Wallet,
    Settings,
    Shield,
    Bell,
    Search,
    Menu,
    X
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'
import { useWalletAuth } from '@/hooks/useWalletAuth'
import { ConnectButton } from '@rainbow-me/rainbowkit'

interface NavigationItem {
    id: string
    label: string
    icon: any
}

interface ShellProps {
    children: React.ReactNode
    activeTab: string
    setActiveTab: (tab: string) => void
}

export const navigationItems: NavigationItem[] = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'create', label: 'Create', icon: PlusCircle },
    { id: 'messages', label: 'Messages', icon: MessageSquare },
    { id: 'communities', label: 'Communities', icon: Users },
    { id: 'governance', label: 'Governance', icon: Shield },
    { id: 'ledger', label: 'Ledger & Explain', icon: BookOpen },
    { id: 'wallet', label: 'Wallet & Reputation', icon: Wallet },
    { id: 'settings', label: 'Settings & Safety', icon: Settings },
]

export function Shell({ children, activeTab, setActiveTab }: ShellProps) {
    const [sidebarOpen, setSidebarOpen] = useState(true)
    const { isConnected, isAuthenticated, address, session, authenticate, logout } = useWalletAuth()

    return (
        <div className="flex h-screen bg-background text-foreground">
            {/* Sidebar */}
            <div className={cn(
                "flex flex-col border-r bg-card transition-all duration-300",
                sidebarOpen ? "w-64" : "w-16"
            )}>
                {/* Logo */}
                <div className="flex items-center justify-between p-4 border-b">
                    <div className={cn("flex items-center gap-2", !sidebarOpen && "hidden")}>
                        <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-pink-500 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-sm">AT</span>
                        </div>
                        <span className="font-bold text-lg">ATLAS</span>
                    </div>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                    >
                        {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
                    </Button>
                </div>

                {/* Navigation */}
                <ScrollArea className="flex-1">
                    <div className="p-2">
                        {navigationItems.map((item) => {
                            const Icon = item.icon
                            return (
                                <Button
                                    key={item.id}
                                    variant={activeTab === item.id ? "secondary" : "ghost"}
                                    className={cn(
                                        "w-full justify-start mb-1",
                                        !sidebarOpen && "justify-center px-2"
                                    )}
                                    onClick={() => setActiveTab(item.id)}
                                >
                                    <Icon className="h-4 w-4" />
                                    {sidebarOpen && <span className="ml-2">{item.label}</span>}
                                </Button>
                            )
                        })}
                    </div>
                </ScrollArea>

                {/* User Profile */}
                {sidebarOpen && (
                    <div className="p-4 border-t">
                        <div className="flex flex-col gap-3">
                            {isConnected ? (
                                <>
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                                            {address?.substring(2, 4).toUpperCase()}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium truncate">{address}</p>
                                            <p className={cn(
                                                "text-[10px] font-bold uppercase tracking-wider",
                                                isAuthenticated ? "text-green-500" : "text-yellow-500"
                                            )}>
                                                {isAuthenticated ? "Authenticated" : "Unverified Session"}
                                            </p>
                                        </div>
                                    </div>
                                    {!isAuthenticated && (
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="w-full text-xs h-8 border-yellow-500/50 hover:bg-yellow-500/10"
                                            onClick={() => authenticate()}
                                        >
                                            Verify Identity
                                        </Button>
                                    )}
                                    {isAuthenticated && (
                                        <Button
                                            size="sm"
                                            variant="ghost"
                                            className="w-full text-xs h-8 text-muted-foreground hover:text-destructive"
                                            onClick={() => logout()}
                                        >
                                            Logout
                                        </Button>
                                    )}
                                </>
                            ) : (
                                <div className="text-center py-2">
                                    <p className="text-xs text-muted-foreground mb-2">Connect wallet to start</p>
                                    <ConnectButton label="Connect" accountStatus="avatar" chainStatus="icon" showBalance={false} />
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
                {/* Top Bar */}
                <div className="flex items-center justify-between p-4 border-b bg-card">
                    <div className="flex items-center gap-4 flex-1">
                        <div className="relative max-w-md flex-1">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Search posts, users, topics..."
                                className="pl-10"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" className="relative">
                            <Bell className="h-4 w-4" />
                            <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
                                3
                            </Badge>
                        </Button>
                    </div>
                </div>

                {/* Content Area */}
                <div className="flex-1 relative overflow-auto">
                    {children}
                </div>
            </div>
        </div>
    )
}
