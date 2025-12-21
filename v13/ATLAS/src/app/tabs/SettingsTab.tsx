'use client'

import dynamic from 'next/dynamic'

const ProfileEditor = dynamic(() => import('@/components/ProfileEditor'), { ssr: false })
const GuardsList = dynamic(() => import('@/components/GuardsList'), { ssr: false })

export function SettingsTab() {
    return (
        <div className="max-w-4xl mx-auto space-y-8 p-6">
            <div className="space-y-6">
                <h2 className="text-2xl font-bold tracking-tight">Profile Settings</h2>
                <ProfileEditor />
            </div>

            <div className="space-y-6">
                <h2 className="text-2xl font-bold tracking-tight">Network Safety</h2>
                <GuardsList />
            </div>
        </div>
    )
}
