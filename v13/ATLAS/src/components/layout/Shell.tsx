'use client'

import React, { useState } from 'react'
import {
    House,
    CirclePlus,
    MessageSquare,
    Users,
    BookOpen,
    Wallet,
    Settings,
    Shield,
    Bell,
    Search,
    Menu,
    X,
    Info
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
    { id: 'home', label: 'Home', icon: House },
    { id: 'create', label: 'Create', icon: CirclePlus },
    { id: 'messages', label: 'Messages', icon: MessageSquare },
    { id: 'communities', label: 'Communities', icon: Users },
    { id: 'governance', label: 'Governance', icon: Shield },
    { id: 'ledger', label: 'Ledger & Explain', icon: BookOpen },
    { id: 'wallet', label: 'Wallet & Reputation', icon: Wallet },
    { id: 'settings', label: 'Settings & Safety', icon: Settings },
]

export function Shell({ children, activeTab, setActiveTab }: ShellProps) {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true)
    const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)
    const { isConnected, isAuthenticated, address, session, authenticate, logout } = useWalletAuth()

    return (
        <div className="flex h-screen bg-background text-foreground">
            {/* Sidebar */}
            <aside className={cn(
                "flex flex-col border-r bg-card transition-all duration-300",
                isSidebarOpen ? "w-64" : "w-16"
            )}>
                {/* Logo */}
                <div className="flex items-center justify-between p-4 border-b">
                    {isSidebarOpen && (
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-pink-500 rounded-lg flex items-center justify-center">
                                <span className="text-white font-bold text-sm">AT</span>
                            </div>
                            <span className="font-bold text-lg">ATLAS</span>
                        </div>
                    )}
                    <Button
                        variant="ghost"
                        size="sm"
                        className={cn("h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5", !isSidebarOpen && "mx-auto")}
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                    >
                        {isSidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
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
                                    variant="ghost"
                                    className={cn(
                                        "w-full justify-start mb-1 text-sm font-medium",
                                        activeTab === item.id ? "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80" : "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50",
                                        !isSidebarOpen && "justify-center px-0"
                                    )}
                                    onClick={() => setActiveTab(item.id)}
                                    data-testid={`nav-${item.id}`}
                                >
                                    <Icon className="h-4 w-4" />
                                    {isSidebarOpen && <span className="ml-2">{item.label}</span>}
                                </Button>
                            )
                        })}
                    </div>
                </ScrollArea>

                {/* User Profile */}
                <div className="p-4 border-t">
                    <div className="flex flex-col gap-3">
                        {isSidebarOpen && (
                            isConnected ? (
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
                                    <ConnectButton label="Connect Wallet" accountStatus="avatar" chainStatus="icon" showBalance={false} />
                                </div>
                            )
                        )}
                        {!isSidebarOpen && !isConnected && (
                            <div className="flex justify-center">
                                <Wallet className="h-4 w-4 text-muted-foreground" />
                            </div>
                        )}
                    </div>
                    {isSidebarOpen && (
                        <div className="mt-4 px-2 py-1 bg-muted/30 rounded border border-border/50">
                            <div className="flex items-center justify-between text-[10px] text-muted-foreground uppercase tracking-tighter">
                                <span>Network Layer</span>
                                <Badge variant="outline" className="h-4 px-1 text-[9px] font-mono" data-testid="v18-badge">v14-v2-baseline</Badge>
                            </div>
                        </div>
                    )}
                </div>
            </aside>

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

                    <div className="flex items-center gap-2 relative">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="relative"
                            id="notification-bell"
                            data-testid="notification-bell"
                            onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                        >
                            <Bell className="h-4 w-4" />
                            <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
                                3
                            </Badge>
                        </Button>

                        {isNotificationsOpen && (
                            <div className="absolute top-10 right-0 w-80 bg-card border rounded-lg shadow-lg z-50 p-4 animate-in fade-in slide-in-from-top-2 duration-200">
                                <div className="flex items-center justify-between mb-4 pb-2 border-b">
                                    <h3 className="font-semibold text-sm">Notifications</h3>
                                    <Badge variant="outline">3 New</Badge>
                                </div>
                                <div className="space-y-3">
                                    <div className="p-2 hover:bg-muted/50 rounded-md transition-colors cursor-pointer border-l-2 border-primary">
                                        <div className="text-xs font-medium">Protocol Update</div>
                                        <div className="text-[10px] text-muted-foreground">v14-v2-baseline initialized successfully.</div>
                                    </div>
                                    <div className="p-2 hover:bg-muted/50 rounded-md transition-colors cursor-pointer">
                                        <div className="text-xs font-medium">New Grant Proposal</div>
                                        <div className="text-[10px] text-muted-foreground">ATLAS-01 is open for voting.</div>
                                    </div>
                                    <div className="p-2 hover:bg-muted/50 rounded-md transition-colors cursor-pointer">
                                        <div className="text-xs font-medium">Network Health</div>
                                        <div className="text-[10px] text-muted-foreground">All nodes reporting 100% coherence.</div>
                                    </div>
                                </div>
                                <Button variant="ghost" className="w-full mt-4 text-xs h-8" onClick={() => setIsNotificationsOpen(false)}>
                                    Clear all
                                </Button>
                            </div>
                        )}
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
