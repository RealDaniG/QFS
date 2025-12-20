'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { 
  Send, 
  Search, 
  Plus, 
  Users, 
  MessageSquare, 
  Clock,
  Check,
  CheckCheck,
  Shield,
  Eye
} from 'lucide-react'

interface Message {
  id: string
  sender: string
  content: string
  timestamp: string
  isOwn: boolean
  status?: 'sent' | 'delivered' | 'read'
  ledgerId?: string
}

interface Conversation {
  id: string
  name: string
  avatar?: string
  lastMessage: string
  timestamp: string
  unread: number
  isGroup: boolean
  members?: number
  isEncrypted: boolean
}

export default function MessagingInterface() {
  const [activeConversation, setActiveConversation] = useState<string | null>(null)
  const [messageInput, setMessageInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  const conversations: Conversation[] = [
    {
      id: 'conv_1',
      name: 'Alice Chen',
      avatar: '/avatars/alice.jpg',
      lastMessage: 'The QFS transparency features are amazing!',
      timestamp: '2 min ago',
      unread: 2,
      isGroup: false,
      isEncrypted: true
    },
    {
      id: 'conv_2',
      name: 'QFS Developers',
      avatar: '/avatars/group.jpg',
      lastMessage: 'Bob: New guard system proposal is ready for review',
      timestamp: '15 min ago',
      unread: 0,
      isGroup: true,
      members: 12,
      isEncrypted: true
    },
    {
      id: 'conv_3',
      name: 'Carol Davis',
      avatar: '/avatars/carol.jpg',
      lastMessage: 'Can you explain the coherence scoring algorithm?',
      timestamp: '1 hour ago',
      unread: 1,
      isGroup: false,
      isEncrypted: true
    },
    {
      id: 'conv_4',
      name: 'Governance Committee',
      avatar: '/avatars/gov.jpg',
      lastMessage: 'Meeting scheduled for tomorrow at 3 PM UTC',
      timestamp: '2 hours ago',
      unread: 5,
      isGroup: true,
      members: 8,
      isEncrypted: true
    }
  ]

  const messages: Message[] = [
    {
      id: 'msg_1',
      sender: 'Alice Chen',
      content: 'Hey! Have you seen the new transparency features in the ATLAS dashboard?',
      timestamp: '10:30 AM',
      isOwn: false,
      ledgerId: 'ledger_001'
    },
    {
      id: 'msg_2',
      sender: 'You',
      content: 'Yes! The ability to see exactly how rewards are calculated is game-changing. Every action is traceable on the ledger.',
      timestamp: '10:32 AM',
      isOwn: true,
      status: 'read',
      ledgerId: 'ledger_002'
    },
    {
      id: 'msg_3',
      sender: 'Alice Chen',
      content: 'The QFS transparency features are amazing! I can see exactly how my content coherence score affects my rewards.',
      timestamp: '10:35 AM',
      isOwn: false,
      ledgerId: 'ledger_003'
    }
  ]

  const activeConv = conversations.find(c => c.id === activeConversation)

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'sent':
        return <Check className="h-3 w-3 text-muted-foreground" />
      case 'delivered':
        return <CheckCheck className="h-3 w-3 text-muted-foreground" />
      case 'read':
        return <CheckCheck className="h-3 w-3 text-blue-500" />
      default:
        return null
    }
  }

  const filteredConversations = conversations.filter(conv =>
    conv.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="h-[600px] flex">
      {/* Conversations List */}
      <div className="w-80 border-r flex flex-col">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Messages</h3>
            <Button size="sm">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search conversations..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2">
            {filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`p-3 rounded-lg cursor-pointer transition-colors hover:bg-muted/50 ${
                  activeConversation === conversation.id ? 'bg-muted' : ''
                }`}
                onClick={() => setActiveConversation(conversation.id)}
              >
                <div className="flex items-start gap-3">
                  <div className="relative">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={conversation.avatar} />
                      <AvatarFallback>
                        {conversation.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    {conversation.isGroup && (
                      <div className="absolute -bottom-1 -right-1 bg-blue-500 rounded-full p-1">
                        <Users className="h-3 w-3 text-white" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium truncate">{conversation.name}</h4>
                      <span className="text-xs text-muted-foreground">
                        {conversation.timestamp}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {conversation.isEncrypted && (
                        <Shield className="h-3 w-3 text-green-500" />
                      )}
                      <p className="text-sm text-muted-foreground truncate">
                        {conversation.lastMessage}
                      </p>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      {conversation.isGroup && (
                        <span className="text-xs text-muted-foreground">
                          {conversation.members} members
                        </span>
                      )}
                      {conversation.unread > 0 && (
                        <Badge variant="default" className="text-xs">
                          {conversation.unread}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Chat Area */}
      {activeConv ? (
        <div className="flex-1 flex flex-col">
          {/* Chat Header */}
          <div className="p-4 border-b bg-card">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={activeConv.avatar} />
                  <AvatarFallback>
                    {activeConv.name.split(' ').map(n => n[0]).join('')}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h4 className="font-medium">{activeConv.name}</h4>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    {activeConv.isEncrypted && (
                      <>
                        <Shield className="h-3 w-3 text-green-500" />
                        <span>End-to-end encrypted</span>
                      </>
                    )}
                    {activeConv.isGroup && (
                      <span>• {activeConv.members} members</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm">
                  <Eye className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm">
                  <Users className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Messages */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isOwn ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[70%] ${message.isOwn ? 'order-2' : 'order-1'}`}>
                    {!message.isOwn && (
                      <div className="flex items-center gap-2 mb-1">
                        <Avatar className="h-6 w-6">
                          <AvatarFallback className="text-xs">
                            {message.sender.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-xs font-medium">{message.sender}</span>
                      </div>
                    )}
                    <div
                      className={`p-3 rounded-lg ${
                        message.isOwn
                          ? 'bg-primary text-primary-foreground ml-auto'
                          : 'bg-muted'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <div className={`flex items-center gap-2 mt-1 text-xs ${
                        message.isOwn ? 'text-primary-foreground/70' : 'text-muted-foreground'
                      }`}>
                        <span>{message.timestamp}</span>
                        {message.ledgerId && (
                          <Badge variant="secondary" className="text-xs">
                            Ledger: {message.ledgerId}
                          </Badge>
                        )}
                        {message.isOwn && getStatusIcon(message.status)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          {/* Message Input */}
          <div className="p-4 border-t bg-card">
            <div className="flex items-end gap-2">
              <Textarea
                placeholder="Type a message... (All messages are logged to the ledger)"
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                className="min-h-[40px] max-h-32 resize-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    // Handle send message
                    setMessageInput('')
                  }
                }}
              />
              <Button size="icon">
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
              <Shield className="h-3 w-3 text-green-500" />
              <span>All messages are end-to-end encrypted and logged to the QFS ledger for transparency</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">Select a conversation</h3>
            <p className="text-muted-foreground">
              Choose a conversation from the list to start messaging with full transparency
            </p>
          </div>
        </div>
      )}
    </div>
  )
}