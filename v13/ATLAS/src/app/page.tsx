'use client'

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { Shell } from '@/components/layout/Shell'

// Phase A: Static Imports
import { HomeTab } from './tabs/HomeTab'
import { CreateTab } from './tabs/CreateTab'
import { MessagesTab } from './tabs/MessagesTab'
import { CommunitiesTab } from './tabs/CommunitiesTab'
import { GovernanceTab } from './tabs/GovernanceTab'
import { LedgerTab } from './tabs/LedgerTab'
import { WalletTab } from './tabs/WalletTab'
import { SettingsTab } from './tabs/SettingsTab'

function DashboardContent() {
  // Phase B: URL Search Params Source of Truth
  const searchParams = useSearchParams()
  // No useState. No useRouter (Shell handles navigation via Link)
  const activeTab = searchParams.get('tab') || 'home'

  return (
    <Shell activeTab={activeTab}>
      <main className="p-6 h-full">
        <div className={activeTab === 'home' ? 'h-full mt-0' : 'hidden'}>
          <HomeTab />
        </div>

        <div className={activeTab === 'create' ? 'h-full mt-0' : 'hidden'}>
          <CreateTab />
        </div>

        <div className={activeTab === 'messages' ? 'h-full mt-0' : 'hidden'}>
          <MessagesTab />
        </div>

        <div className={activeTab === 'communities' ? 'h-full mt-0' : 'hidden'}>
          <CommunitiesTab />
        </div>

        <div className={activeTab === 'governance' ? 'h-full mt-0' : 'hidden'}>
          <GovernanceTab />
        </div>

        <div className={activeTab === 'ledger' ? 'h-full mt-0' : 'hidden'}>
          <LedgerTab />
        </div>

        <div className={activeTab === 'wallet' ? 'h-full mt-0' : 'hidden'}>
          <WalletTab />
        </div>

        <div className={activeTab === 'settings' ? 'h-full mt-0' : 'hidden'}>
          <SettingsTab />
        </div>
      </main>
    </Shell>
  )
}

export default function AtlasDashboard() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center">Loading Application...</div>}>
      <DashboardContent />
    </Suspense>
  )
}