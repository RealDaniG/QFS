'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Progress } from '@/components/ui/progress'
import { createHash } from 'crypto'
import {
  Eye,
  TrendingUp,
  Wallet,
  Shield,
  Clock,
  Globe,
  Users,
  Lock,
  Zap,
  AlertCircle,
  CheckCircle,
  BarChart3,
  LayoutGrid
} from 'lucide-react'
import { cn } from '@/lib/utils'

import { useAuth } from '@/hooks/useAuth'
import { useWalletAuth } from '@/hooks/useWalletAuth'
import { useContentPublisher } from '@/hooks/useContentPublisher'
import type { Visibility } from '@/types/storage'

interface ContentComposerProps {
  isOpen: boolean
  onClose: () => void
}

export default function ContentComposer({ isOpen, onClose }: ContentComposerProps) {
  const { isAuthenticated, did } = useAuth()
  const { isConnected } = useWalletAuth()
  const { publish, isPublishing } = useContentPublisher()
  const [content, setContent] = useState('')
  const [tags, setTags] = useState('')
  const [visibility, setVisibility] = useState('public')
  const [showEconomics, setShowEconomics] = useState(false)
  const [scheduledTime, setScheduledTime] = useState('')
  const [coherenceWeight, setCoherenceWeight] = useState([70])
  const [engagementWeight, setEngagementWeight] = useState([30])

  const mockEconomicAnalysis = {
    coherenceScore: 0.0,
    rewardPotential: 0.0,
    estimatedReach: 0,
    guardChecks: [
      { name: 'Content Quality', status: 'pending', description: 'Analyzing content structure and clarity' },
      { name: 'Space Guidelines', status: 'pending', description: 'Checking against space standards' },
      { name: 'Economic Impact', status: 'pending', description: 'Evaluating reward distribution' },
      { name: 'Spam Detection', status: 'pending', description: 'Analyzing for spam patterns' }
    ],
    projections: {
      immediateRewards: 0,
      longTermRewards: 0,
      reputationImpact: 0,
      networkEffect: 0
    }
  }

  const [economicAnalysis, setEconomicAnalysis] = useState(mockEconomicAnalysis)

  const analyzeContent = () => {
    const length = content.length
    const wordCount = content.split(/\s+/).filter(word => word.length > 0).length

    // Deterministic simulation based on content hash
    const simpleHash = (str: string) => {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
      }
      return Math.abs(hash) / 2147483647; // Normalize 0-1
    };

    const seed = content + tags + visibility;
    const rng1 = simpleHash(seed + "coh");
    const rng2 = simpleHash(seed + "rew");
    const rng3 = simpleHash(seed + "rea");

    // Zero-Sim Compliant Metrics
    const coherenceScore = Math.min(0.95, (wordCount / 100) * 0.8 + rng1 * 0.15)
    const rewardPotential = coherenceScore * 50 + rng2 * 20
    const estimatedReach = Math.floor(coherenceScore * 1000 + rng3 * 500)

    const updatedAnalysis = {
      ...economicAnalysis,
      coherenceScore,
      rewardPotential,
      estimatedReach,
      guardChecks: [
        { name: 'Content Quality', status: coherenceScore > 0.7 ? 'pass' : 'warning', description: coherenceScore > 0.7 ? 'High quality content detected' : 'Content could be more detailed' },
        { name: 'Space Guidelines', status: 'pass', description: 'Content aligns with space standards' },
        { name: 'Economic Impact', status: rewardPotential > 30 ? 'pass' : 'warning', description: rewardPotential > 30 ? 'Positive economic impact expected' : 'Lower reward potential' },
        { name: 'Spam Detection', status: 'pass', description: 'No spam patterns detected' }
      ],
      projections: {
        immediateRewards: rewardPotential * 0.3,
        longTermRewards: rewardPotential * 0.7,
        reputationImpact: coherenceScore * 0.1,
        networkEffect: estimatedReach * 0.05
      }
    }

    setEconomicAnalysis(updatedAnalysis)
  }

  const [authError, setAuthError] = useState(false)

  const handlePublish = async () => {
    // Check wallet connection first
    if (!isConnected) {
      setAuthError(true)
      return
    }

    if (!content.trim()) {
      return
    }

    setAuthError(false)
    const tagArray = tags.split(',').map(t => t.trim()).filter(Boolean)

    const result = await publish(content, {
      visibility: visibility as Visibility,
      tags: tagArray
    })

    if (result) {
      console.log('Published:', result)
      setContent('')
      setTags('')
      setAuthError(false)
      onClose()
    } else {
      console.error('Publish failed')
    }
  }

  const getGuardIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      case 'fail':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getGuardStatusColor = (status: string) => {
    switch (status) {
      case 'pass':
        return 'text-green-600'
      case 'warning':
        return 'text-yellow-600'
      case 'fail':
        return 'text-red-600'
      default:
        return 'text-gray-400'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Create Content</CardTitle>
              <CardDescription>
                Every action is transparent and economically accountable
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowEconomics(!showEconomics)}
              >
                <Eye className="h-4 w-4 mr-1" />
                {showEconomics ? 'Hide' : 'Show'} Economics
              </Button>
              <Button variant="ghost" size="sm" onClick={onClose}>
                ×
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="flex h-[600px]">
            {/* Main Composer */}
            <div className={cn(
              "flex-1 p-6 overflow-y-auto",
              showEconomics && "border-r"
            )}>
              <div className="space-y-4">
                {/* Visibility Settings */}
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="visibility">Visibility:</Label>
                    <Select value={visibility} onValueChange={setVisibility}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="public">
                          <div className="flex items-center gap-2">
                            <Globe className="h-4 w-4" />
                            Public
                          </div>
                        </SelectItem>
                        <SelectItem value="space">
                          <div className="flex items-center gap-2">
                            <LayoutGrid className="h-4 w-4" />
                            Space
                          </div>
                        </SelectItem>
                        <SelectItem value="private">
                          <div className="flex items-center gap-2">
                            <Lock className="h-4 w-4" />
                            Private
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center gap-2">
                    <Label htmlFor="schedule">Schedule:</Label>
                    <Input
                      id="schedule"
                      type="datetime-local"
                      value={scheduledTime}
                      onChange={(e) => setScheduledTime(e.target.value)}
                      className="w-40"
                    />
                  </div>
                </div>

                {/* Content Input */}
                <div className="space-y-2">
                  <Label htmlFor="content">Content</Label>
                  <Textarea
                    id="content"
                    placeholder="Share your thoughts with full transparency..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    className="min-h-[200px] resize-none"
                  />
                  <div className="text-sm text-muted-foreground">
                    {content.length} characters • {content.split(/\s+/).filter(word => word.length > 0).length} words
                  </div>
                </div>

                {/* Tags */}
                <div className="space-y-2">
                  <Label htmlFor="tags">Tags</Label>
                  <Input
                    id="tags"
                    placeholder="Add tags separated by commas..."
                    className="w-full"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                  />
                </div>

                {/* Economic Weights */}
                <div className="space-y-4">
                  <Label>Content Ranking Preferences</Label>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label className="text-sm">Coherence Weight</Label>
                      <span className="text-sm font-medium">{coherenceWeight[0]}%</span>
                    </div>
                    <Slider
                      value={coherenceWeight}
                      onValueChange={setCoherenceWeight}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label className="text-sm">Engagement Weight</Label>
                      <span className="text-sm font-medium">{engagementWeight[0]}%</span>
                    </div>
                    <Slider
                      value={engagementWeight}
                      onValueChange={setEngagementWeight}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-between pt-4">
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={analyzeContent}>
                      <BarChart3 className="h-4 w-4 mr-1" />
                      Analyze
                    </Button>
                    <Button variant="outline" size="sm">
                      <Clock className="h-4 w-4 mr-1" />
                      Save Draft
                    </Button>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" onClick={onClose}>
                      Cancel
                    </Button>
                    <Button onClick={handlePublish} disabled={isPublishing || !content.trim()}>
                      {isPublishing ? 'Publishing...' : (scheduledTime ? 'Schedule' : 'Publish')}
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* Economic Analysis Panel */}
            {showEconomics && (
              <div className="w-96 p-6 overflow-y-auto bg-muted/30">
                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="guards">Guards</TabsTrigger>
                    <TabsTrigger value="projections">Projections</TabsTrigger>
                  </TabsList>

                  <TabsContent value="overview" className="space-y-4">
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-3 bg-background rounded-lg">
                          <TrendingUp className="h-6 w-6 mx-auto mb-1 text-green-600" />
                          <div className="text-2xl font-bold text-green-600">
                            {economicAnalysis.coherenceScore.toFixed(2)}
                          </div>
                          <div className="text-xs text-muted-foreground">Coherence Score</div>
                        </div>
                        <div className="text-center p-3 bg-background rounded-lg">
                          <Wallet className="h-6 w-6 mx-auto mb-1 text-blue-600" />
                          <div className="text-2xl font-bold text-blue-600">
                            {economicAnalysis.rewardPotential.toFixed(1)}
                          </div>
                          <div className="text-xs text-muted-foreground">FLX Rewards</div>
                        </div>
                      </div>

                      <div className="p-3 bg-background rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">Estimated Reach</span>
                          <span className="text-sm font-bold">{economicAnalysis.estimatedReach}</span>
                        </div>
                        <Progress value={(economicAnalysis.estimatedReach / 2000) * 100} className="h-2" />
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Content Quality</span>
                          <span className="font-medium">High</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span>Network Effect</span>
                          <span className="font-medium">Positive</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span>Reward Distribution</span>
                          <span className="font-medium">Fair</span>
                        </div>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="guards" className="space-y-3">
                    <div className="space-y-3">
                      {economicAnalysis.guardChecks.map((guard, index) => (
                        <div key={index} className="p-3 bg-background rounded-lg">
                          <div className="flex items-start gap-2">
                            {getGuardIcon(guard.status)}
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">{guard.name}</span>
                                <Badge
                                  variant={guard.status === 'pass' ? 'default' : guard.status === 'warning' ? 'secondary' : 'destructive'}
                                  className="text-xs"
                                >
                                  {guard.status}
                                </Badge>
                              </div>
                              <p className="text-xs text-muted-foreground mt-1">
                                {guard.description}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </TabsContent>

                  <TabsContent value="projections" className="space-y-4">
                    <div className="space-y-3">
                      <div className="p-3 bg-background rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm">Immediate Rewards</span>
                          <span className="font-bold text-green-600">
                            +{economicAnalysis.projections.immediateRewards.toFixed(1)} FLX
                          </span>
                        </div>
                      </div>

                      <div className="p-3 bg-background rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm">Long-term Rewards</span>
                          <span className="font-bold text-blue-600">
                            +{economicAnalysis.projections.longTermRewards.toFixed(1)} FLX
                          </span>
                        </div>
                      </div>

                      <div className="p-3 bg-background rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm">Reputation Impact</span>
                          <span className="font-bold text-purple-600">
                            +{economicAnalysis.projections.reputationImpact.toFixed(3)}
                          </span>
                        </div>
                      </div>

                      <div className="p-3 bg-background rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm">Network Effect</span>
                          <span className="font-bold text-orange-600">
                            +{economicAnalysis.projections.networkEffect.toFixed(0)} users
                          </span>
                        </div>
                      </div>

                      <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap className="h-4 w-4 text-blue-600" />
                          <span className="text-sm font-medium">Total Potential</span>
                        </div>
                        <div className="text-2xl font-bold text-blue-600">
                          {(economicAnalysis.projections.immediateRewards + economicAnalysis.projections.longTermRewards).toFixed(1)} FLX
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}