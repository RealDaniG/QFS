'use client'

import dynamic from 'next/dynamic'

const WalletInterface = dynamic(() => import('@/components/WalletInterface'), { ssr: false })

export function WalletTab() {
    return (
        <div className="max-w-6xl mx-auto p-6">
            <WalletInterface />
        </div>
    )
}
