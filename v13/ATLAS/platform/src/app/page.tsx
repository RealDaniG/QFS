'use client'

import { useState } from 'react'
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
  TrendingUp,
  Activity,
  Eye,
  ChevronRight
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'
import { ExplainRewardFlow } from '@/components/ExplainRewardFlow'
import ContentComposer from '@/components/ContentComposer'
import MessagingInterface from '@/components/MessagingInterface'
import DiscoveryInterface from '@/components/DiscoveryInterface'
import WalletInterface from '@/components/WalletInterface'
import ProfileEditor from '@/components/ProfileEditor'
import GovernanceInterface from '@/components/GovernanceInterface'
import GuardsList from '@/components/GuardsList'
import { useInteraction } from '@/hooks/useInteraction'

// Atlas & QFS Imports
import { RealLedger } from '@/lib/ledger/real-ledger';
import { getTreasury } from '@/lib/economics/treasury-engine';
import { GovernanceService } from '@/lib/governance/service';
import { PendingEventStore } from '@/lib/ledger/pending-store';
import { LedgerSyncService } from '@/lib/ledger/sync-service';

// Services
const ledger = new RealLedger(); // New Zero-Sim Client
const treasury = getTreasury();
// Zero-Sim: GovernanceService fetches directly from QFS
const governance = new GovernanceService();
const pendingStore = new PendingEventStore();
// Fire and forget init
pendingStore.init();

// NOTE: LedgerSyncService might need updates to poll RealLedger instead of MockLedger
// For now, we keep it to handle local optimistic UI updates if compatible
const syncService = new LedgerSyncService(ledger);

export default function AtlasDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [activeTab, setActiveTab] = useState('home')
  const [showComposer, setShowComposer] = useState(false)
  const { interact } = useInteraction()

  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'create', label: 'Create', icon: PlusCircle },
    { id: 'messages', label: 'Messages', icon: MessageSquare },
    { id: 'communities', label: 'Communities', icon: Users },
    { id: 'governance', label: 'Governance', icon: Shield }, // Add item
    { id: 'ledger', label: 'Ledger & Explain', icon: BookOpen },
    { id: 'wallet', label: 'Wallet & Reputation', icon: Wallet },
    { id: 'settings', label: 'Settings & Safety', icon: Settings },
  ]

  const mockPosts = [
    {
      id: 1,
      author: 'Alice Chen',
      avatar: '/avatars/alice.jpg',
      content: 'Just published a comprehensive analysis of QFS coherence scoring algorithms. The transparency in how rewards are calculated is game-changing for decentralized social platforms!',
      coherenceScore: 0.92,
      rewardPotential: 45.50,
      likes: 234,
      comments: 45,
      reposts: 12,
      timestamp: '2 hours ago',
      tags: ['QFS', 'Coherence', 'Research']
    },
    {
      id: 2,
      author: 'Bob Martinez',
      avatar: '/avatars/bob.jpg',
      content: 'The new guard system implementation shows how deterministic economics can coexist with creative expression. Every action is traceable and explainable.',
      coherenceScore: 0.88,
      rewardPotential: 32.75,
      likes: 156,
      comments: 23,
      reposts: 8,
      timestamp: '4 hours ago',
      tags: ['Guards', 'Economics', 'Transparency']
    },
    {
      id: 3,
      author: 'Carol Davis',
      avatar: '/avatars/carol.jpg',
      content: 'Community governance through the event ledger creates unprecedented accountability. No more hidden moderation decisions!',
      coherenceScore: 0.95,
      rewardPotential: 67.25,
      likes: 412,
      comments: 89,
      reposts: 34,
      timestamp: '6 hours ago',
      tags: ['Governance', 'Community', 'Ledger']
    }
  ]

  const systemHealth = {
    qfsStatus: 'Operational',
    coherenceRanking: 'Active',
    guardSystem: 'All Green',
    ledgerSync: 'Real-time',
    nodeHealth: '98.2%'
  }

  return (
    <div className="flex h-screen bg-background">
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
            <div className="flex items-center gap-3">
              <Avatar className="h-8 w-8">
                <AvatarImage src="/avatars/user.jpg" />
                <AvatarFallback>JD</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">John Doe</p>
                <p className="text-xs text-muted-foreground">Reputation: 0.87</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
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
        <div className="flex-1 flex">
          {/* Main Feed */}
          <div className="flex-1 p-6">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-7">
                {navigationItems.map((item) => (
                  <TabsTrigger key={item.id} value={item.id} className="text-xs">
                    {item.label}
                  </TabsTrigger>
                ))}
              </TabsList>

              <TabsContent value="home" className="mt-6">
                <div className="max-w-2xl mx-auto space-y-6">
                  {/* Create Post Card */}
                  <Card>
                    <CardHeader>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarImage src="/avatars/user.jpg" />
                          <AvatarFallback>JD</AvatarFallback>
                        </Avatar>
                        <Input
                          placeholder="Share your thoughts with full transparency..."
                          className="flex-1"
                          onClick={() => setShowComposer(true)}
                          readOnly
                        />
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="sm" onClick={() => setShowComposer(true)}>
                            <Eye className="h-4 w-4 mr-1" />
                            Preview Economics
                          </Button>
                        </div>
                        <Button size="sm" onClick={() => setShowComposer(true)}>Create Post</Button>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Feed Posts */}
                  {mockPosts.map((post) => (
                    <Card key={post.id}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <Avatar className="h-10 w-10">
                              <AvatarImage src={post.avatar} />
                              <AvatarFallback>{post.author.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-medium">{post.author}</p>
                              <p className="text-sm text-muted-foreground">{post.timestamp}</p>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm">
                            <ChevronRight className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="mb-4">{post.content}</p>

                        {/* Tags */}
                        <div className="flex flex-wrap gap-2 mb-4">
                          {post.tags.map((tag) => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              #{tag}
                            </Badge>
                          ))}
                        </div>

                        {/* Coherence & Rewards */}
                        <div className="grid grid-cols-2 gap-4 p-3 bg-muted/50 rounded-lg mb-4">
                          <div className="flex items-center gap-2">
                            <TrendingUp className="h-4 w-4 text-green-600" />
                            <div>
                              <p className="text-xs text-muted-foreground">Coherence Score</p>
                              <p className="font-semibold text-green-600">{post.coherenceScore}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Wallet className="h-4 w-4 text-blue-600" />
                            <div>
                              <p className="text-xs text-muted-foreground">Reward Potential</p>
                              <p className="font-semibold text-blue-600">{post.rewardPotential} FLX</p>
                            </div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-4">
                          <Button variant="ghost" size="sm">
                            <MessageSquare className="h-4 w-4 mr-1" />
                            {post.comments}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => interact('like', `bafy_mock_${post.id}`)}
                          >
                            <Activity className="h-4 w-4 mr-1" />
                            {post.likes}
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Users className="h-4 w-4 mr-1" />
                            {post.reposts}
                          </Button>
                          <Button variant="ghost" size="sm" className="ml-auto">
                            <Eye className="h-4 w-4 mr-1" />
                            Explain
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="create">
                <div className="max-w-2xl mx-auto">
                  <Card>
                    <CardHeader>
                      <CardTitle>Create Content</CardTitle>
                      <CardDescription>
                        Every action is transparent and economically accountable
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center py-8">
                        <Button onClick={() => setShowComposer(true)} size="lg">
                          <PlusCircle className="h-5 w-5 mr-2" />
                          Open Content Composer
                        </Button>
                        <p className="text-muted-foreground mt-4">
                          Create posts, images, videos, polls with full economic transparency
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="messages">
                <div className="max-w-6xl mx-auto">
                  <Card className="h-[600px]">
                    <CardHeader className="pb-3">
                      <CardTitle>Messages</CardTitle>
                      <CardDescription>
                        Private and group messaging with full transparency and encryption
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-0">
                      <MessagingInterface />
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              <TabsContent value="communities" className="mt-0 h-full">
                <div className="max-w-6xl mx-auto">
                  <Card className="h-[600px]">
                    <CardHeader className="pb-3">
                      <CardTitle>Communities</CardTitle>
                      <CardDescription>
                        Explore and join communities with full transparency and encryption
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-0">
                      <DiscoveryInterface />
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="governance" className="mt-0 h-full p-6">
                <GovernanceInterface />
              </TabsContent>

              <TabsContent value="settings" className="mt-0 h-full p-6">
                <div className="max-w-2xl mx-auto space-y-8">
                  <div className="space-y-6">
                    <h2 className="text-2xl font-bold tracking-tight">Profile Settings</h2>
                    <ProfileEditor />
                  </div>

                  <div className="space-y-6">
                    <h2 className="text-2xl font-bold tracking-tight">Network Safety</h2>
                    <GuardsList />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="ledger" className="mt-0 h-full p-6">
                <div className="max-w-6xl mx-auto">
                  <div className="space-y-6">
                    <ExplainRewardFlow />
                    <Card>
                      <CardHeader>
                        <CardTitle>Event Ledger & Explainability</CardTitle>
                        <CardDescription>
                          Complete transparency of all system events and decisions
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="p-4 bg-muted/50 rounded-lg">
                            <div className="flex items-center gap-2 mb-2">
                              <Activity className="h-5 w-5 text-blue-600" />
                              <span className="font-medium">Global Stream</span>
                            </div>
                            <p className="text-sm text-muted-foreground">Chronological public events across the entire network</p>
                          </div>
                          <div className="p-4 bg-muted/50 rounded-lg">
                            <div className="flex items-center gap-2 mb-2">
                              <BookOpen className="h-5 w-5 text-green-600" />
                              <span className="font-medium">Per-Object Ledger</span>
                            </div>
                            <p className="text-sm text-muted-foreground">Mini-chains of events for specific content or actions</p>
                          </div>
                          <div className="p-4 bg-muted/50 rounded-lg">
                            <div className="flex items-center gap-2 mb-2">
                              <Shield className="h-5 w-5 text-purple-600" />
                              <span className="font-medium">Simulation Log</span>
                            </div>
                            <p className="text-sm text-muted-foreground">What-if scenarios and AGI proposals</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Recent Ledger Events</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {[
                            {
                              id: 'evt_001',
                              type: 'content_published',
                              timestamp: '2 minutes ago',
                              module: 'ContentModule',
                              user: 'Alice Chen',
                              description: 'Published analysis of QFS coherence scoring',
                              outcome: 'Success - 45.2 FLX rewards allocated',
                              guards: ['ContentQuality: PASS', 'EconomicGuard: PASS', 'AEGIS: PASS']
                            },
                            {
                              id: 'evt_002',
                              type: 'governance_vote',
                              timestamp: '15 minutes ago',
                              module: 'GovernanceModule',
                              user: 'Bob Martinez',
                              description: 'Voted on parameter update proposal #42',
                              outcome: 'Vote recorded - Reputation +0.02',
                              guards: ['VotingGuard: PASS', 'ReputationGuard: PASS']
                            },
                            {
                              id: 'evt_003',
                              type: 'moderation_action',
                              timestamp: '1 hour ago',
                              module: 'SafetyModule',
                              user: 'System',
                              description: 'Content flagged for review',
                              outcome: 'Content queued for human review',
                              guards: ['AEGIS: FLAG', 'SpamGuard: PASS']
                            }
                          ].map((event) => (
                            <div key={event.id} className="p-4 border rounded-lg">
                              <div className="flex items-start justify-between mb-3">
                                <div>
                                  <div className="flex items-center gap-2">
                                    <Badge variant="outline">{event.type}</Badge>
                                    <span className="text-sm text-muted-foreground">{event.timestamp}</span>
                                  </div>
                                  <h4 className="font-medium mt-1">{event.description}</h4>
                                  <p className="text-sm text-muted-foreground">by {event.user} via {event.module}</p>
                                </div>
                                <Button variant="ghost" size="sm">
                                  <Eye className="h-4 w-4" />
                                </Button>
                              </div>

                              <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-medium">Outcome:</span>
                                  <span className="text-sm text-green-600">{event.outcome}</span>
                                </div>

                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-medium">Guards:</span>
                                  <div className="flex gap-1">
                                    {event.guards.map((guard, idx) => (
                                      <Badge key={idx} variant="secondary" className="text-xs">
                                        {guard}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="wallet">
                <WalletInterface />
              </TabsContent>

              <TabsContent value="settings">
                <div className="max-w-4xl mx-auto">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="space-y-6">
                      <ProfileEditor />
                      <Card>
                        <CardHeader>
                          <CardTitle>Safety Controls</CardTitle>
                          <CardDescription>
                            Manage your safety and privacy preferences
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div className="flex items-center justify-between p-3 border rounded-lg">
                              <div>
                                <h4 className="font-medium">Content Filtering</h4>
                                <p className="text-sm text-muted-foreground">
                                  Automatically filter potentially sensitive content
                                </p>
                              </div>
                              <Button variant="outline" size="sm">Configure</Button>
                            </div>

                            <div className="flex items-center justify-between p-3 border rounded-lg">
                              <div>
                                <h4 className="font-medium">Blocked Users</h4>
                                <p className="text-sm text-muted-foreground">
                                  Manage users you've blocked
                                </p>
                              </div>
                              <Button variant="outline" size="sm">Manage</Button>
                            </div>

                            <div className="flex items-center justify-between p-3 border rounded-lg">
                              <div>
                                <h4 className="font-medium">Privacy Settings</h4>
                                <p className="text-sm text-muted-foreground">
                                  Control who can see your content and interact with you
                                </p>
                              </div>
                              <Button variant="outline" size="sm">Settings</Button>
                            </div>

                            <div className="flex items-center justify-between p-3 border rounded-lg">
                              <div>
                                <h4 className="font-medium">Two-Factor Authentication</h4>
                                <p className="text-sm text-muted-foreground">
                                  Add an extra layer of security to your account
                                </p>
                              </div>
                              <Button variant="outline" size="sm">Enable</Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle>Reporting & Appeals</CardTitle>
                          <CardDescription>
                            All moderation actions are transparent and appealable
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-3">
                            <div className="p-3 bg-muted/30 rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium">Recent Reports</span>
                                <Badge variant="secondary">3</Badge>
                              </div>
                              <div className="space-y-2">
                                <div className="text-xs">
                                  <div className="flex items-center justify-between">
                                    <span>Content reported by you</span>
                                    <span className="text-muted-foreground">2 days ago</span>
                                  </div>
                                  <div className="text-muted-foreground">Status: Under Review</div>
                                </div>
                                <div className="text-xs">
                                  <div className="flex items-center justify-between">
                                    <span>Appeal submitted</span>
                                    <span className="text-muted-foreground">1 week ago</span>
                                  </div>
                                  <div className="text-muted-foreground">Status: Approved</div>
                                </div>
                              </div>
                            </div>

                            <Button variant="outline" className="w-full">
                              View All Reports & Appeals
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    <div className="space-y-6">
                      <Card>
                        <CardHeader>
                          <CardTitle>Governance Participation</CardTitle>
                          <CardDescription>
                            Participate in transparent network governance
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div className="p-3 bg-muted/30 rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium">Active Proposals</span>
                                <Badge variant="secondary">2</Badge>
                              </div>
                              <div className="space-y-2">
                                <div className="text-xs">
                                  <div className="font-medium">Proposal #42: Update Coherence Algorithm</div>
                                  <div className="text-muted-foreground">Ends in 2 days • 78% voted</div>
                                </div>
                                <div className="text-xs">
                                  <div className="font-medium">Proposal #43: Reward Pool Adjustment</div>
                                  <div className="text-muted-foreground">Ends in 5 days • 45% voted</div>
                                </div>
                              </div>
                            </div>

                            <Button variant="outline" className="w-full">
                              View All Proposals
                            </Button>

                            <Button className="w-full">
                              Submit New Proposal
                            </Button>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle>System Preferences</CardTitle>
                          <CardDescription>
                            Customize your ATLAS experience
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <h4 className="font-medium">Email Notifications</h4>
                                <p className="text-sm text-muted-foreground">
                                  Receive updates about your account activity
                                </p>
                              </div>
                              <Button variant="outline" size="sm">Manage</Button>
                            </div>

                            <div className="flex items-center justify-between">
                              <div>
                                <h4 className="font-medium">Data Export</h4>
                                <p className="text-sm text-muted-foreground">
                                  Download all your data from the platform
                                </p>
                              </div>
                              <Button variant="outline" size="sm">Export</Button>
                            </div>

                            <div className="flex items-center justify-between">
                              <div>
                                <h4 className="font-medium">Account Deletion</h4>
                                <p className="text-sm text-muted-foreground">
                                  Permanently delete your account and data
                                </p>
                              </div>
                              <Button variant="destructive" size="sm">Delete</Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Right Panel - Context Info */}
          <div className="w-80 border-l p-4 space-y-4">
            {/* System Health */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">System Health</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.entries(systemHealth).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground capitalize">
                      {key.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                    <Badge
                      variant={value === 'Operational' || value === 'Active' || value === 'All Green' ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {value}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Notifications */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Recent Notifications</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                    <div>
                      <p className="text-xs font-medium">New reward earned</p>
                      <p className="text-xs text-muted-foreground">+12.5 FLX from post engagement</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                    <div>
                      <p className="text-xs font-medium">Reputation increased</p>
                      <p className="text-xs text-muted-foreground">Coherence score: 0.87 → 0.89</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-orange-500 rounded-full mt-1.5"></div>
                    <div>
                      <p className="text-xs font-medium">Guard alert</p>
                      <p className="text-xs text-muted-foreground">Content passed all checks</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Your Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-2xl font-bold">0.87</p>
                    <p className="text-xs text-muted-foreground">Reputation</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold">247</p>
                    <p className="text-xs text-muted-foreground">FLX Balance</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold">42</p>
                    <p className="text-xs text-muted-foreground">Posts</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold">1.2k</p>
                    <p className="text-xs text-muted-foreground">Interactions</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Content Composer Modal */}
      <ContentComposer
        isOpen={showComposer}
        onClose={() => setShowComposer(false)}
      />
    </div>
  )
}