'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import { Shell } from '@/components/layout/Shell'
import { Tabs, TabsContent } from '@/components/ui/tabs'

// Dynamically import heavy content components with ssr: false
const HomeTab = dynamic(() => import('./tabs/HomeTab').then(m => m.HomeTab), { ssr: false })
const CreateTab = dynamic(() => import('./tabs/CreateTab').then(m => m.CreateTab), { ssr: false })
const MessagesTab = dynamic(() => import('./tabs/MessagesTab').then(m => m.MessagesTab), { ssr: false })
const CommunitiesTab = dynamic(() => import('./tabs/CommunitiesTab').then(m => m.CommunitiesTab), { ssr: false })
const GovernanceTab = dynamic(() => import('./tabs/GovernanceTab').then(m => m.GovernanceTab), { ssr: false })
const LedgerTab = dynamic(() => import('./tabs/LedgerTab').then(m => m.LedgerTab), { ssr: false })
const WalletTab = dynamic(() => import('./tabs/WalletTab').then(m => m.WalletTab), { ssr: false })
const SettingsTab = dynamic(() => import('./tabs/SettingsTab').then(m => m.SettingsTab), { ssr: false })

export default function AtlasDashboard() {
  const [activeTab, setActiveTab] = useState('home')

  return (
    <Shell activeTab={activeTab} setActiveTab={setActiveTab}>
      <main className="p-6 h-full">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          <TabsContent value="home" className="mt-0 h-full"><HomeTab /></TabsContent>
          <TabsContent value="create" className="mt-0 h-full"><CreateTab /></TabsContent>
          <TabsContent value="messages" className="mt-0 h-full"><MessagesTab /></TabsContent>
          <TabsContent value="communities" className="mt-0 h-full"><CommunitiesTab /></TabsContent>
          <TabsContent value="governance" className="mt-0 h-full"><GovernanceTab /></TabsContent>
          <TabsContent value="ledger" className="mt-0 h-full"><LedgerTab /></TabsContent>
          <TabsContent value="wallet" className="mt-0 h-full"><WalletTab /></TabsContent>
          <TabsContent value="settings" className="mt-0 h-full"><SettingsTab /></TabsContent>
        </Tabs>
      </main>
    </Shell>
  )
}