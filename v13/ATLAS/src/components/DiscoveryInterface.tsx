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
import DistributedFeed from '@/components/DistributedFeed'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { useQuery } from '@tanstack/react-query'
import { atlasFetch } from '@/lib/api'
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
  Zap,
  LayoutGrid
} from 'lucide-react'
import { ExplainThisPanel } from '@/components/ExplainThisPanel';
import { useExplain } from '@/hooks/useExplain';
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";

interface Space {
  id: string
  name: string
  description: string
  avatar?: string
  members: number
  isPublic: boolean
  isVerified: boolean
  tags: string[]
  coherenceScore: number
  coherence_rank?: number
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

interface Recommendation {
  type: string
  name: string
  reason: string
  match: number
}

interface ActivityItem {
  action: string
  user: string
  time: string
  type: string
}


export default function DiscoveryInterface() {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('spaces')
  const { explanation, fetchRankingExplanation, isLoading: isExplaining, clearExplanation } = useExplain();

  // Fetch real spaces from API
  const { data: apiSpaces, isLoading: isLoadingSpaces } = useQuery<Space[]>({
    queryKey: ['spaces'],
    queryFn: async () => {
      const res = await atlasFetch('/api/v18/spaces');
      if (!res.ok) throw new Error('Failed to fetch spaces');
      return res.json();
    }
  });

  // Fetch real trending topics from API
  const { data: apiTrending, isLoading: isLoadingTrending } = useQuery<TrendingTopic[]>({
    queryKey: ['trending'],
    queryFn: async () => {
      const res = await atlasFetch('/api/v18/trending');
      if (!res.ok) throw new Error('Failed to fetch trending topics');
      return res.json();
    }
  });

  // Fetch recommendations
  const { data: apiRecommendations, isLoading: isLoadingRecommendations } = useQuery<Recommendation[]>({
    queryKey: ['recommendations'],
    queryFn: async () => {
      const res = await atlasFetch('/api/v18/recommendations');
      if (!res.ok) throw new Error('Failed to fetch recommendations');
      return res.json();
    }
  });

  // Fetch activity
  const { data: apiActivity, isLoading: isLoadingActivity } = useQuery<ActivityItem[]>({
    queryKey: ['activity'],
    queryFn: async () => {
      const res = await atlasFetch('/api/v18/activity');
      if (!res.ok) throw new Error('Failed to fetch activity');
      return res.json();
    }
  });

  const spaces: Space[] = apiSpaces || [];
  const trendingTopics: TrendingTopic[] = apiTrending || [];
  const recommendations: Recommendation[] = apiRecommendations || [];
  const activity: ActivityItem[] = apiActivity || [];


  const filteredSpaces = spaces.filter(space =>
    space.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    space.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    space.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const handleJoinSpace = async (spaceId: string) => {
    try {
      const res = await atlasFetch(`/api/v18/spaces/${spaceId}/join`, {
        method: 'POST',
      });
      if (!res.ok) {
        throw new Error('Failed to join space');
      }
      // Optionally, refetch spaces or update UI to reflect joined status
      alert(`Successfully joined space ${spaceId}! (Stub: Action recorded in EvidenceBus)`);
    } catch (error) {
      console.error('Error joining space:', error);
      alert('Failed to join space.');
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="spaces">Spaces</TabsTrigger>
          <TabsTrigger value="trending">Trending Topics</TabsTrigger>
          <TabsTrigger value="network">Network & Trust</TabsTrigger>
          <TabsTrigger value="discover">Discover</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="spaces" className="space-y-6">
          {/* Search and Filters */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Spaces</CardTitle>
                  <CardDescription>
                    Join spaces that align with your interests and values
                  </CardDescription>
                </div>
                <Button>
                  <LayoutGrid className="h-4 w-4 mr-2" />
                  Create Space
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <Hash className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search spaces by name, description, or tags..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Spaces Grid */}
          {isLoadingSpaces ? (
            <div className="flex justify-center p-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredSpaces.map((space) => (
                <Card key={space.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={space.avatar} />
                          <AvatarFallback>
                            {space.name.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold">{space.name}</h3>
                            {space.isVerified && (
                              <Shield className="h-4 w-4 text-blue-500" />
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Users className="h-3 w-3" />
                            <span>{(space.members || 0).toLocaleString()} members</span>
                            {space.isPublic ? (
                              <Globe className="h-3 w-3" />
                            ) : (
                              <Shield className="h-3 w-3" />
                            )}
                          </div>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-green-600">
                        +{space.growthRate || 0}%
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      {space.description}
                    </p>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mb-4">
                      {(space.tags || []).map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          #{tag}
                        </Badge>
                      ))}
                    </div>

                    {/* Space Stats */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="text-center p-3 bg-muted/50 rounded-lg">
                        <div className="flex items-center justify-center gap-1 mb-1">
                          <TrendingUp className="h-4 w-4 text-green-600" />
                          <span className="text-sm font-medium">Coherence</span>
                        </div>
                        <div className="text-lg font-bold text-green-600">
                          {(space.coherence_rank || space.coherenceScore || 0).toFixed(2)}
                        </div>
                      </div>
                      <div className="text-center p-3 bg-muted/50 rounded-lg">
                        <div className="flex items-center justify-center gap-1 mb-1">
                          <Zap className="h-4 w-4 text-blue-600" />
                          <span className="text-sm font-medium">Reward Pool</span>
                        </div>
                        <div className="text-lg font-bold text-blue-600">
                          {(space.rewardPool || 0).toFixed(0)} FLX
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <Button className="flex-1" onClick={() => handleJoinSpace(space.id)}>Join Space</Button>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
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
              {isLoadingTrending ? (
                <div className="flex justify-center p-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                <div className="space-y-4">
                  {trendingTopics.map((topic, index) => (
                    <Dialog key={topic.id} onOpenChange={(open) => {
                      if (open) {
                        fetchRankingExplanation(topic.id);
                      } else {
                        clearExplanation();
                      }
                    }}>
                      <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
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
                          <DialogTrigger asChild>
                            <Button variant="outline" size="sm" className="gap-2">
                              <Hash className="h-3 w-3" />
                              Why?
                            </Button>
                          </DialogTrigger>
                          <Button variant="outline">Explore</Button>
                        </div>
                      </div>
                      <DialogContent className="max-w-2xl">
                        <ExplainThisPanel
                          type="ranking"
                          explanation={explanation || undefined}
                          isLoading={isExplaining}
                        />
                      </DialogContent>
                    </Dialog>
                  ))}
                </div>
              )}
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
                  Spaces and topics based on your activity and interests
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recommendations.map((item, idx) => (
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
                  <div className="space-y-4">
                    {activity.map((item, idx) => (
                      <div key={idx} className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <div className="flex-1">
                          <p className="text-sm">{item.action}</p>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span>{item.user}</span>
                            <span>•</span>
                            <span>{item.time}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="activity" className="space-y-6">
          <Feed />
        </TabsContent>

      </Tabs >
    </div >
  )
}