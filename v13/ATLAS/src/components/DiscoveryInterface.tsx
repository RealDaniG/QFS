'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Progress } from '@/components/ui/progress'
import Feed from '@/components/Feed'
import DistributedFeed from '@/components/DistributedFeed' // Add import
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { useLedgerSimulation } from '@/hooks/useLedgerSimulation'
import {
  TrendingUp,
  Users,
  Hash,
  MessageSquare,
  Eye,
  Star,
  Shield,
  Globe,
  Clock,
  Activity,
  Zap
} from 'lucide-react'

interface Community {
  id: string
  name: string
  description: string
  avatar?: string
  members: number
  isPublic: boolean
  isVerified: boolean
  tags: string[]
  coherenceScore: number
  rewardPool: number
  growthRate: number
}

interface TrendingTopic {
  id: string
  name: string
  posts: number
  engagement: number
  growth: number
  coherenceScore: number
}

export default function DiscoveryInterface() {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('communities')

  const communities: Community[] = [
    {
      id: 'comm_1',
      name: 'QFS Developers',
      description: 'Discussion and development of Quantum Financial System features and protocols',
      avatar: '/avatars/qfs-dev.jpg',
      members: 2847,
      isPublic: true,
      isVerified: true,
      tags: ['Development', 'QFS', 'Technical'],
      coherenceScore: 0.94,
      rewardPool: 15420.50,
      growthRate: 12.5
    },
    {
      id: 'comm_2',
      name: 'DeFi Governance',
      description: 'Exploring decentralized governance models and transparent decision-making',
      avatar: '/avatars/defi-gov.jpg',
      members: 1523,
      isPublic: true,
      isVerified: true,
      tags: ['Governance', 'DeFi', 'DAO'],
      coherenceScore: 0.89,
      rewardPool: 8750.25,
      growthRate: 8.3
    },
    {
      id: 'comm_3',
      name: 'Content Creators',
      description: 'Community for content creators exploring transparent reward systems',
      avatar: '/avatars/creators.jpg',
      members: 3421,
      isPublic: true,
      isVerified: false,
      tags: ['Content', 'Creative', 'Rewards'],
      coherenceScore: 0.87,
      rewardPool: 12340.75,
      growthRate: 15.7
    },
    {
      id: 'comm_4',
      name: 'Transparency Advocates',
      description: 'Promoting transparency and accountability in digital platforms',
      avatar: '/avatars/transparency.jpg',
      members: 892,
      isPublic: true,
      isVerified: true,
      tags: ['Transparency', 'Advocacy', 'Ethics'],
      coherenceScore: 0.92,
      rewardPool: 5670.00,
      growthRate: 6.2
    }
  ]

  const trendingTopics: TrendingTopic[] = [
    {
      id: 'topic_1',
      name: 'QFS Transparency',
      posts: 1247,
      engagement: 8934,
      growth: 45.2,
      coherenceScore: 0.91
    },
    {
      id: 'topic_2',
      name: 'Coherence Scoring',
      posts: 892,
      engagement: 6721,
      growth: 32.8,
      coherenceScore: 0.88
    },
    {
      id: 'topic_3',
      name: 'Guard Systems',
      posts: 645,
      engagement: 5234,
      growth: 28.5,
      coherenceScore: 0.93
    },
    {
      id: 'topic_4',
      name: 'Ledger Technology',
      posts: 523,
      engagement: 4156,
      growth: 22.1,
      coherenceScore: 0.86
    },
    {
      id: 'topic_5',
      name: 'Deterministic Economics',
      posts: 412,
      engagement: 3245,
      growth: 18.9,
      coherenceScore: 0.90
    }
  ]

  const filteredCommunities = communities.filter(community =>
    community.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    community.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    community.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="communities">Communities</TabsTrigger>
          <TabsTrigger value="trending">Trending Topics</TabsTrigger>
          <TabsTrigger value="network">Network & Trust</TabsTrigger>
          <TabsTrigger value="discover">Discover</TabsTrigger>
          <TabsTrigger value="activity">Raw Ledger</TabsTrigger>
        </TabsList>

        <TabsContent value="communities" className="space-y-6">
          {/* Search and Filters */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Communities</CardTitle>
                  <CardDescription>
                    Join communities that align with your interests and values
                  </CardDescription>
                </div>
                <Button>
                  <Users className="h-4 w-4 mr-2" />
                  Create Community
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <Hash className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search communities by name, description, or tags..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Communities Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredCommunities.map((community) => (
              <Card key={community.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={community.avatar} />
                        <AvatarFallback>
                          {community.name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold">{community.name}</h3>
                          {community.isVerified && (
                            <Shield className="h-4 w-4 text-blue-500" />
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Users className="h-3 w-3" />
                          <span>{community.members.toLocaleString()} members</span>
                          {community.isPublic ? (
                            <Globe className="h-3 w-3" />
                          ) : (
                            <Shield className="h-3 w-3" />
                          )}
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-green-600">
                      +{community.growthRate}%
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    {community.description}
                  </p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {community.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        #{tag}
                      </Badge>
                    ))}
                  </div>

                  {/* Community Stats */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center p-3 bg-muted/50 rounded-lg">
                      <div className="flex items-center justify-center gap-1 mb-1">
                        <TrendingUp className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium">Coherence</span>
                      </div>
                      <div className="text-lg font-bold text-green-600">
                        {community.coherenceScore.toFixed(2)}
                      </div>
                    </div>
                    <div className="text-center p-3 bg-muted/50 rounded-lg">
                      <div className="flex items-center justify-center gap-1 mb-1">
                        <Zap className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium">Reward Pool</span>
                      </div>
                      <div className="text-lg font-bold text-blue-600">
                        {community.rewardPool.toFixed(0)} FLX
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <Button className="flex-1">Join Community</Button>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="trending" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Trending Topics</CardTitle>
              <CardDescription>
                Discover what's trending across the ATLAS network with full transparency
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {trendingTopics.map((topic, index) => (
                  <div key={topic.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="text-2xl font-bold text-muted-foreground w-8">
                        #{index + 1}
                      </div>
                      <div>
                        <h3 className="font-semibold mb-1">{topic.name}</h3>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <MessageSquare className="h-3 w-3" />
                            <span>{topic.posts.toLocaleString()} posts</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Activity className="h-3 w-3" />
                            <span>{topic.engagement.toLocaleString()} engagements</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <TrendingUp className="h-3 w-3 text-green-600" />
                            <span className="text-green-600">+{topic.growth}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="text-sm font-medium">Coherence</div>
                        <div className="text-lg font-bold text-green-600">
                          {topic.coherenceScore.toFixed(2)}
                        </div>
                      </div>
                      <Button variant="outline">Explore</Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="network" className="space-y-6">
          <DistributedFeed />
        </TabsContent>

        <TabsContent value="discover" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Recommended for You</CardTitle>
                <CardDescription>
                  Communities and topics based on your activity and interests
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    {
                      type: 'community',
                      name: 'QFS Research',
                      reason: 'Based on your engagement with technical content',
                      match: 94
                    },
                    {
                      type: 'topic',
                      name: 'Transparent Governance',
                      reason: 'Trending in your network',
                      match: 87
                    },
                    {
                      type: 'community',
                      name: 'Economic Modeling',
                      reason: 'Similar members have joined',
                      match: 82
                    }
                  ].map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium">{item.name}</h4>
                          <Badge variant="outline" className="text-xs">
                            {item.type}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{item.reason}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-green-600">{item.match}%</div>
                        <div className="text-xs text-muted-foreground">match</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Network Activity</CardTitle>
                <CardDescription>
                  Real-time activity across the ATLAS network
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    {
                      action: 'New post in QFS Developers',
                      user: 'Alice Chen',
                      time: '2 minutes ago',
                      type: 'content'
                    },
                    {
                      action: 'Community "Transparency Advocates" reached 1K members',
                      user: 'System',
                      time: '15 minutes ago',
                      type: 'milestone'
                    },
                    {
                      action: 'Trending topic: "Guard Systems"',
                      user: 'Network',
                      time: '1 hour ago',
                      type: 'trending'
                    },
                    {
                      action: 'New governance proposal submitted',
                      user: 'Bob Martinez',
                      time: '2 hours ago',
                      type: 'governance'
                    }
                  ].map((activity, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="text-sm">{activity.action}</p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <span>{activity.user}</span>
                          <span>•</span>
                          <span>{activity.time}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="activity" className="space-y-6">
          <Feed />
        </TabsContent>

      </Tabs>
    </div>
  )
}