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
    // v18 Rule: Session token handles access to local services
    const [sessionToken, setSessionToken] = useState<string | null>(null);
    const [session, setSession] = useState<AuthSession | null>(null)

    // Check for existing session on mount
    useEffect(() => {
        const storedSession = localStorage.getItem('atlas_session')
        if (storedSession) {
            const parsed = JSON.parse(storedSession)
            if (parsed.expiresAt > Date.now() / 1000) {
                setSession(parsed)
                setSessionToken(parsed.sessionToken) // Compatibility with other hooks
                setIsAuthenticated(true)
            } else {
                localStorage.removeItem('atlas_session')
            }
        }
    }, [])

    const authenticate = async () => {
        if (!address || !isConnected) return

        setIsAuthenticating(true)

        try {
            // 1. Get challenge from backend
            const challengeRes = await fetch('http://localhost:8000/api/auth/challenge', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wallet_address: address })
            })

            if (!challengeRes.ok) throw new Error('Failed to get challenge')

            const { message } = await challengeRes.json()

            // 2. Sign message
            const signature = await signMessageAsync({ message })

            // 3. Verify signature and get session
            const verifyRes = await fetch('http://localhost:8000/api/auth/verify', {
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
                await fetch('http://localhost:8000/api/auth/logout', {
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
        sessionToken, // Exposed for compatibility
        authenticate,
        // Alias authenticate to triggerAuth for compatibility if needed
        triggerAuth: authenticate,
        logout
    }
}
