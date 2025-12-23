import { useAccount, useSignMessage } from 'wagmi'
import { useState, useEffect } from 'react'

interface AuthSession {
    sessionToken: string
    walletAddress: string
    expiresAt: number
}

export function useWalletAuth() {
    const { address, isConnected } = useAccount()
    const { signMessageAsync } = useSignMessage()
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [isAuthenticating, setIsAuthenticating] = useState(false)
    const [sessionToken, setSessionToken] = useState<string | null>(null);
    const [session, setSession] = useState<AuthSession | null>(null)

    const baseUrl = process.env.NEXT_PUBLIC_API_URL || ''

    // Check for existing session on mount
    useEffect(() => {
        const storedSession = localStorage.getItem('atlas_session')
        if (storedSession) {
            try {
                const parsed = JSON.parse(storedSession)
                if (parsed.expiresAt > Date.now() / 1000) {
                    setSession(parsed)
                    setSessionToken(parsed.sessionToken)
                    setIsAuthenticated(true)
                } else {
                    localStorage.removeItem('atlas_session')
                }
            } catch (e) {
                localStorage.removeItem('atlas_session')
            }
        }
    }, [])

    // Electron Provider Detection
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const provider = window.ethereum ||
                (window as any).electronProvider ||
                (window as any).web3?.currentProvider;

            if (!provider) {
                console.warn('No Web3 provider detected in Electron/Browser');
            }
        }
    }, []);

    const authenticate = async () => {
        if (!address || !isConnected) return

        setIsAuthenticating(true)
        try {
            // 1. Get challenge from backend
            const challengeRes = await fetch(`${baseUrl}/api/v18/auth/challenge`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wallet_address: address })
            })

            if (!challengeRes.ok) throw new Error('Failed to get challenge')
            const { message } = await challengeRes.json()

            // 2. Sign message
            const signature = await signMessageAsync({ message })

            // 3. Verify signature and get session
            const verifyRes = await fetch(`${baseUrl}/api/v18/auth/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    wallet_address: address,
                    signature,
                    message
                })
            })

            if (!verifyRes.ok) throw new Error('Signature verification failed')
            const sessionData = await verifyRes.json()

            // 4. Store session
            localStorage.setItem('atlas_session', JSON.stringify(sessionData))
            setSession(sessionData)
            setSessionToken(sessionData.sessionToken)
            setIsAuthenticated(true)

        } catch (error) {
            console.error('Authentication failed:', error)
            setIsAuthenticated(false)
        } finally {
            setIsAuthenticating(false)
        }
    }

    const logout = async () => {
        if (session) {
            try {
                await fetch(`${baseUrl}/api/v18/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${session.sessionToken}`
                    }
                })
            } catch (e) {
                console.warn("Logout failed on backend", e);
            }
        }

        localStorage.removeItem('atlas_session')
        setSession(null)
        setSessionToken(null)
        setIsAuthenticated(false)
    }

    return {
        isConnected,
        isAuthenticated,
        isAuthenticating,
        address,
        session,
        sessionToken,
        authenticate,
        triggerAuth: authenticate,
        logout
    }
}
