/**
 * useWalletAuth Hook
 * Manages EVM Wallet Authentication via the ATLAS Backend.
 */

'use client';

import { useState, useCallback } from 'react';
import { ethers } from 'ethers';
import { atlasFetch } from '@/lib/api';

// Types representing the backend response
interface LoginResponse {
    session_token: string;
    wallet_address: string;
    expires_at: number;
}

interface WalletAuthState {
    isConnected: boolean;
    address: string | null;
    sessionToken: string | null;
    isLoading: boolean;
    error: string | null;
}

const SESSION_KEY = 'atlas_session_v1';

export function useWalletAuth() {
    const [state, setState] = useState<WalletAuthState>(() => {
        // Load session from local storage on init
        if (typeof window !== 'undefined') {
            const stored = localStorage.getItem(SESSION_KEY);
            if (stored) {
                try {
                    const session = JSON.parse(stored);
                    const now = Date.now() / 1000;
                    if (session.expires_at > now) {
                        return {
                            isConnected: true,
                            address: session.wallet_address,
                            sessionToken: session.session_token,
                            isLoading: false,
                            error: null
                        };
                    } else {
                        localStorage.removeItem(SESSION_KEY);
                    }
                } catch (e) {
                    localStorage.removeItem(SESSION_KEY);
                }
            }
        }
        return {
            isConnected: false,
            address: null,
            sessionToken: null,
            isLoading: false,
            error: null
        };
    });

    const connect = useCallback(async () => {
        setState(prev => ({ ...prev, isLoading: true, error: null }));
        try {
            if (!window.ethereum) {
                throw new Error("No crypto wallet found. Please install MetaMask.");
            }

            const provider = new ethers.BrowserProvider(window.ethereum);
            const signer = await provider.getSigner();
            const address = await signer.getAddress();

            // 1. Get Nonce
            // v18: Endpoint is /api/v1/auth/nonce
            const nonceRes = await atlasFetch('/api/v1/auth/nonce', { auth: false });
            if (!nonceRes.ok) throw new Error("Failed to fetch nonce");
            const { nonce } = await nonceRes.json();

            // 2. Sign Nonce
            const signature = await signer.signMessage(nonce);

            // 3. Login
            // v18: Endpoint is /api/v1/auth/login
            const loginRes = await atlasFetch('/api/v1/auth/login', {
                method: 'POST',
                auth: false,
                body: JSON.stringify({
                    nonce,
                    signature,
                    wallet_address: address
                })
            });

            if (!loginRes.ok) {
                const errData = await loginRes.json();
                throw new Error(errData.detail || "Login failed");
            }

            const sessionData: LoginResponse = await loginRes.json();

            // v18.5: Verify Ascon token prefix
            if (!sessionData.session_token.startsWith('ascon1.')) {
                console.warn("Received non-Ascon token. Expected 'ascon1.' prefix for v18 Distributed compliance.");
            }

            // Store session
            localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));

            setState({
                isConnected: true,
                address: sessionData.wallet_address,
                sessionToken: sessionData.session_token,
                isLoading: false,
                error: null
            });

        } catch (err: any) {
            console.error("Wallet Auth Error:", err);
            setState(prev => ({
                ...prev,
                isLoading: false,
                error: err.message || "Authentication failed"
            }));
        }
    }, []);

    const logout = useCallback(async () => {
        // Optional: Call backend logout to revoke token
        if (state.sessionToken) {
            try {
                await atlasFetch('/api/v1/auth/logout', {
                    method: 'POST',
                    body: JSON.stringify({ session_token: state.sessionToken })
                });
            } catch (e) {
                // Ignore backend logout error, client cleanup is priority
            }
        }

        localStorage.removeItem(SESSION_KEY);
        setState({
            isConnected: false,
            address: null,
            sessionToken: null,
            isLoading: false,
            error: null
        });
    }, [state.sessionToken]);

    return {
        ...state,
        connect,
        logout
    };
}
