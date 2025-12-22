'use client'

import { useState, useEffect } from 'react'

export interface SystemStatus {
    backend: 'online' | 'offline'
    version: string
    port: string
    headHash: string
    architecture: string
    loading: boolean
}

export function useSystemStatus() {
    const [status, setStatus] = useState<SystemStatus>({
        backend: 'offline',
        version: 'v18.ALPHA',
        port: '8001',
        headHash: '0x' + '0'.repeat(16) + '...',
        architecture: 'Modular',
        loading: true
    })

    const fetchStatus = async () => {
        try {
            // Use 127.0.0.1:8001 only (standard port)
            const ports = ['8001']
            let healthData = null
            let activePort = '8000'

            for (const p of ports) {
                try {
                    const res = await fetch(`http://127.0.0.1:${p}/health`)
                    if (res.ok) {
                        healthData = await res.json()
                        activePort = p
                        break
                    }
                } catch (e) {
                    continue
                }
            }

            if (healthData) {
                // Also fetch evidence head from the same port
                let headHash = '0x' + '0'.repeat(16) + '...'
                try {
                    const headRes = await fetch(`http://127.0.0.1:${activePort}/api/evidence/head`)
                    if (headRes.ok) {
                        const headData = await headRes.json()
                        headHash = headData.head_hash
                    }
                } catch (e) {
                    // Ignore head fetch error if main health succeeded
                }

                setStatus({
                    backend: 'online',
                    version: healthData.version || 'v18.ALPHA',
                    port: activePort,
                    headHash: headHash,
                    architecture: healthData.services?.architecture || 'Modular',
                    loading: false
                })
            } else {
                setStatus(prev => ({ ...prev, backend: 'offline', loading: false }))
            }
        } catch (error) {
            setStatus(prev => ({ ...prev, backend: 'offline', loading: false }))
        }
    }

    useEffect(() => {
        fetchStatus()
        const interval = setInterval(fetchStatus, 10000) // Poll every 10s
        return () => clearInterval(interval)
    }, [])

    return { status, refresh: fetchStatus }
}
