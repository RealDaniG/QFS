'use client'

import { useState, Suspense } from 'react'
import dynamic from 'next/dynamic'
import { Shell } from '@/components/layout/Shell'
import { Tabs, TabsContent } from '@/components/ui/tabs'
import { Loader2 } from 'lucide-react'

// Loading state component for Playwright detection
function TabLoadingState({ label }: { label: string }) {
  return (
    <div
      data-testid={`${label.toLowerCase()}-loading`}
      className="flex flex-col items-center justify-center p-12 min-h-[300px]"
    >
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-3" />
      <span className="text-muted-foreground text-sm">Loading {label}...</span>
    </div>
  )
}

// Dynamic imports with loading states for Playwright compatibility
const HomeTab = dynamic(
  () => import('./tabs/HomeTab').then(m => m.HomeTab),
  { loading: () => <TabLoadingState label="Home" /> }
)

const CreateTab = dynamic(
  () => import('./tabs/CreateTab').then(m => m.CreateTab),
  { loading: () => <TabLoadingState label="Create" /> }
)

const MessagesTab = dynamic(
  () => import('./tabs/MessagesTab').then(m => m.MessagesTab),
  { loading: () => <TabLoadingState label="Messages" /> }
)

const CommunitiesTab = dynamic(
  () => import('./tabs/CommunitiesTab').then(m => m.CommunitiesTab),
  { loading: () => <TabLoadingState label="Communities" /> }
)

const GovernanceTab = dynamic(
  () => import('./tabs/GovernanceTab').then(m => m.GovernanceTab),
  { loading: () => <TabLoadingState label="Governance" /> }
)

const LedgerTab = dynamic(
  () => import('./tabs/LedgerTab').then(m => m.LedgerTab),
  { loading: () => <TabLoadingState label="Ledger" /> }
)

const WalletTab = dynamic(
  () => import('./tabs/WalletTab').then(m => m.WalletTab),
  { loading: () => <TabLoadingState label="Wallet" /> }
)

const SettingsTab = dynamic(
  () => import('./tabs/SettingsTab').then(m => m.SettingsTab),
  { loading: () => <TabLoadingState label="Settings" /> }
)

export default function AtlasDashboard() {
  const [activeTab, setActiveTab] = useState('home')

  return (
    <Shell activeTab={activeTab} setActiveTab={setActiveTab}>
      <main className="p-6 h-full">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          <TabsContent value="home" className="mt-0 h-full">
            <Suspense fallback={<TabLoadingState label="Home" />}>
              <HomeTab />
            </Suspense>
          </TabsContent>
          <TabsContent value="create" className="mt-0 h-full">
            <Suspense fallback={<TabLoadingState label="Create" />}>
              <CreateTab />
            </Suspense>
          </TabsContent>
          <TabsContent value="messages" className="mt-0 h-full">
            <Suspense fallback={<TabLoadingState label="Messages" />}>
              <MessagesTab />
            </Suspense>
          </TabsContent>
          <TabsContent value="communities" className="mt-0 h-full">
            <Suspense fallback={<TabLoadingState label="Communities" />}>
              <CommunitiesTab />
            </Suspense>
          </TabsContent>
          <TabsContent value="governance" className="mt-0 h-full">
            <Suspense fallback={<TabLoadingState label="Governance" />}>
              <GovernanceTab />
            </Suspense>
          </TabsContent>
          <TabsContent value="ledger" className="mt-0 h-full">
            <Suspense fallback={<TabLoadingState label="Ledger" />}>
              <LedgerTab />
            </Suspense>
          </TabsContent>
          <TabsContent value="wallet" className="mt-0 h-full">
            <Suspense fallback={<TabLoadingState label="Wallet" />}>
              <WalletTab />
            </Suspense>
          </TabsContent>
          <TabsContent value="settings" className="mt-0 h-full">
            <Suspense fallback={<TabLoadingState label="Settings" />}>
              <SettingsTab />
            </Suspense>
          </TabsContent>
        </Tabs>
      </main>
    </Shell>
  )
}