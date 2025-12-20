'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
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
  X,
  Activity
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { useWalletAuth } from '@/hooks/useWalletAuth';

// Components
import { ExplainRewardFlow } from '@/components/ExplainRewardFlow';
import ContentComposer from '@/components/ContentComposer';
import MessagingInterface from '@/components/MessagingInterface';
import DiscoveryInterface from '@/components/DiscoveryInterface';
import WalletInterface from '@/components/WalletInterface';
import ProfileEditor from '@/components/ProfileEditor';
import GovernanceInterface from '@/components/GovernanceInterface';
import GuardsList from '@/components/GuardsList';
import DistributedFeed from '@/components/DistributedFeed';

import { ErrorBoundary } from '@/components/ui/error-boundary';
import { WalletConnectButton } from '@/components/WalletConnectButton';
import { NotificationPanel } from '@/components/NotificationPanel';

export default function AtlasDashboard() {
  const { isConnected, address, isLoading: authLoading } = useWalletAuth();
  const router = useRouter();

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeView, setActiveView] = useState('home');
  const [showComposer, setShowComposer] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);

  // v18 Login Gate
  useEffect(() => {
    if (!authLoading && !isConnected) {
      // For now, if not connected, we show a simplified welcome or prompt
    }
  }, [isConnected, authLoading]);

  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'discover', label: 'Discover', icon: Users },
    { id: 'messages', label: 'Messages', icon: MessageSquare },
    { id: 'wallet', label: 'Wallet', icon: Wallet },
    { id: 'bounties', label: 'Bounties', icon: Activity },
    { id: 'ledger', label: 'Ledger & Explain', icon: BookOpen },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const systemHealth = {
    qfsStatus: 'Operational',
    coherenceRanking: 'Active',
    guardSystem: 'All Green',
    ledgerSync: 'Real-time',
    nodeHealth: '98.2%'
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Synchronizing v18 clusters...</p>
        </div>
      </div>
    );
  }

  // Dashboard identity display update for v18
  const displayAddress = address ? `${address.slice(0, 6)}...${address.slice(-4)}` : "Not Connected";

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <div className={cn(
        "flex flex-col border-r bg-card transition-all duration-300 shadow-xl z-20",
        sidebarOpen ? "w-64" : "w-20"
      )}>
        <div className="flex items-center justify-between p-4 border-b">
          <div className={cn("flex items-center gap-2", !sidebarOpen && "hidden")}>
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-sm">AT</span>
            </div>
            <span className="font-bold text-lg tracking-tight">ATLAS v18</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>

        <ScrollArea className="flex-1 px-3 py-4">
          <nav className="space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  data-testid={`nav-${item.id}`}
                  onClick={() => setActiveView(item.id)}
                  className={cn(
                    "flex items-center w-full transition-all duration-200 group relative",
                    "hover:bg-accent hover:text-accent-foreground rounded-lg px-3 py-2.5",
                    activeView === item.id ? "bg-primary/10 text-primary font-semibold" : "text-muted-foreground",
                    !sidebarOpen && "justify-center"
                  )}
                >
                  <Icon className={cn("h-5 w-5", activeView === item.id ? "text-primary" : "group-hover:scale-110 transition-transform")} />
                  {sidebarOpen && <span className="ml-3 text-sm">{item.label}</span>}
                  {activeView === item.id && (
                    <div className="absolute left-0 w-1 h-6 bg-primary rounded-r-full" />
                  )}
                </button>
              );
            })}
          </nav>
        </ScrollArea>

        <div className="p-4 border-t bg-muted/30">
          <div className={cn("flex items-center gap-3", !sidebarOpen && "justify-center")}>
            <Avatar className="h-9 w-9 border-2 border-background shadow-sm">
              <AvatarImage src="/avatars/user.jpg" />
              <AvatarFallback className="bg-primary/10 text-primary">JD</AvatarFallback>
            </Avatar>
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold truncate">{displayAddress}</p>
                {isConnected && (
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">Reputation: 142</p>
                  </div>
                )}
                {!isConnected && (
                  <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">Unauthenticated</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-between p-4 border-b bg-card/80 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-4 flex-1">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold capitalize">{activeView.replace('-', ' ')}</h2>
              <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20 text-[10px] font-mono">
                v18-ALPHA
              </Badge>
            </div>
            <div className="relative max-w-sm flex-1 hidden md:block">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search v18 clusters..."
                className="pl-10 bg-muted/50 border-none h-9 focus-visible:ring-1"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center gap-3 relative">
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                "relative cursor-pointer hover:bg-muted transition-colors",
                showNotifications && "bg-muted"
              )}
              onClick={() => setShowNotifications(!showNotifications)}
              id="notification-bell"
            >
              <Bell className="h-5 w-5" />
              {!showNotifications && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-600 rounded-full border-2 border-card animate-pulse" />
              )}
            </Button>

            {showNotifications && (
              <div className="absolute top-full right-0 mt-2 z-50 animate-in fade-in zoom-in-95 duration-200 origin-top-right">
                <NotificationPanel />
              </div>
            )}

            <div className="h-8 w-px bg-border mx-1" />
            <WalletConnectButton />
          </div>
        </header>

        <main className="flex-1 overflow-auto bg-gradient-to-b from-background to-muted/20">
          <div className="max-w-6xl mx-auto p-6">
            {!isConnected && activeView !== 'settings' && (
              <Card className="mb-6 border-blue-500/30 bg-blue-500/5 backdrop-blur-sm border-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-blue-600" />
                    Authentication Required
                  </CardTitle>
                  <CardDescription>
                    Connect your wallet to participate in the v18 Quantum Financial System.
                    Wallets are used as cryptographic identity only. No transfers are supported.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4 p-4 bg-background/50 rounded-xl border border-blue-500/20">
                    <p className="text-sm text-balance">
                      Your v18 session will be sealed with <strong>ASCON-128</strong> authenticated encryption.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <ErrorBoundary name={activeView}>
                {activeView === 'home' && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-8">
                      <Card className="overflow-hidden border-none shadow-sm group">
                        <div className="h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500" />
                        <CardHeader className="pb-3 flex flex-row items-center gap-4">
                          <Avatar className="h-10 w-10">
                            <AvatarImage src="/avatars/user.jpg" />
                            <AvatarFallback>JD</AvatarFallback>
                          </Avatar>
                          <Input
                            data-testid="composer-trigger"
                            placeholder="Share deterministic content..."
                            className="bg-muted/50 border-none h-11"
                            onClick={() => setShowComposer(true)}
                            readOnly
                          />
                        </CardHeader>
                        <CardContent className="flex justify-end gap-2 pt-0">
                          <Button variant="outline" size="sm" onClick={() => setShowComposer(true)}>Preview Economics</Button>
                          <Button size="sm" onClick={() => setShowComposer(true)}>Publish Event</Button>
                        </CardContent>
                      </Card>

                      <DistributedFeed />
                    </div>

                    <div className="space-y-6">
                      <Card className="border-none shadow-sm">
                        <CardHeader>
                          <CardTitle className="text-sm font-bold flex items-center gap-2">
                            <Activity className="h-4 w-4 text-primary" />
                            System Health
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          {Object.entries(systemHealth).map(([key, value]) => (
                            <div key={key} className="flex items-center justify-between">
                              <span className="text-xs text-muted-foreground capitalize">
                                {key.replace(/([A-Z])/g, ' $1').trim()}
                              </span>
                              <Badge
                                variant={value === 'Operational' || value === 'Active' || value === 'All Green' ? 'default' : 'secondary'}
                                className="text-[10px] h-5"
                              >
                                {value}
                              </Badge>
                            </div>
                          ))}
                        </CardContent>
                      </Card>

                      <Card className="border-none shadow-sm bg-gradient-to-br from-indigo-600 to-blue-700 text-white">
                        <CardHeader>
                          <CardTitle className="text-sm">Total Internal Credits</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold tracking-tight">1,000.00 FLX</div>
                          <p className="text-[10px] mt-2 opacity-80 uppercase font-bold tracking-wider">Non-Transferable (v18 Plan)</p>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                )}

                {activeView === 'discover' && <DiscoveryInterface />}
                {activeView === 'messages' && <MessagingInterface />}
                {activeView === 'bounties' && (
                  <div className="space-y-6">
                    <Card className="border-none shadow-sm">
                      <CardHeader>
                        <CardTitle>Available Bounties</CardTitle>
                        <CardDescription>Contribute to QFS development and earn rewards</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-muted-foreground">Bounty system integration in progress for v18.</p>
                      </CardContent>
                    </Card>
                  </div>
                )}
                {activeView === 'ledger' && (
                  <div className="space-y-6">
                    <ExplainRewardFlow />
                    <Card className="border-none shadow-sm">
                      <CardHeader>
                        <CardTitle>v18 Event Ledger</CardTitle>
                        <CardDescription>ASCON-sealed deterministic audit trail</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-muted-foreground">Detailed event streams for v18 are being synchronized from primary clusters.</p>
                      </CardContent>
                    </Card>
                  </div>
                )}
                {activeView === 'wallet' && <WalletInterface />}
                {activeView === 'settings' && (
                  <div className="space-y-12">
                    <ProfileEditor />
                    <GuardsList />
                  </div>
                )}
              </ErrorBoundary>
            </div>
          </div>
        </main>
      </div>

      {/* Content Composer Modal */}
      {showComposer && (
        <ContentComposer
          isOpen={showComposer}
          onClose={() => setShowComposer(false)}
        />
      )}
    </div>
  );
}