'use client'

import dynamic from 'next/dynamic'

const GovernanceInterface = dynamic(() => import('@/components/GovernanceInterface'), { ssr: false })

export function GovernanceTab() {
    return (
        <div className="max-w-6xl mx-auto p-6">
            <GovernanceInterface />
        </div>
    )
}
