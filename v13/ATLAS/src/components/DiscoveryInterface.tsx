import { ExplainThisPanel } from '@/components/ExplainThisPanel';
import { useExplain } from '@/hooks/useExplain';
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";

// ... inside component ...

export default function DiscoveryInterface() {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('communities')
  const { explanation, fetchRankingExplanation, isLoading: isExplaining, clearExplanation } = useExplain();

  // ... (data definitions) ...

  return (
    // ...
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
        </CardContent>
      </Card>
    </TabsContent>
    // ...
  )
}

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

      </Tabs >
    </div >
  )
}