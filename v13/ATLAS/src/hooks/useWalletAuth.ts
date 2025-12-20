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

import { useAuthStore } from '@/lib/store/useAuthStore';

const SESSION_KEY = 'atlas_session_v1';

export function useWalletAuth() {
    const { isConnected, address, sessionToken, isLoading, error, setState, logout: storeLogout } = useAuthStore();

    const connect = useCallback(async () => {
        setState({ isLoading: true, error: null });
        try {
            if (!(window as any).ethereum) {
                throw new Error("No crypto wallet found. Please install MetaMask.");
            }

            const provider = new ethers.BrowserProvider((window as any).ethereum);
            const signer = await provider.getSigner();
            const address = await signer.getAddress();

            // 1. Get Nonce
            const nonceRes = await atlasFetch('/api/v18/auth/nonce', {
                method: 'GET',
                auth: false
            });
            if (!nonceRes.ok) throw new Error("Failed to fetch nonce");
            const { nonce } = await nonceRes.json();

            // 2. Sign Nonce
            const signature = await signer.signMessage(nonce);

            // 3. Login / Verify
            const loginRes = await atlasFetch('/api/v18/auth/verify', {
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

            const sessionData = await loginRes.json();

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
            setState({
                isLoading: false,
                error: err.message || "Authentication failed"
            });
        }
    }, [setState]);

    const logout = useCallback(async () => {
        if (sessionToken) {
            try {
                await atlasFetch('/api/v1/auth/logout', {
                    method: 'POST',
                    body: JSON.stringify({ session_token: sessionToken })
                });
            } catch (e) {
                // Ignore backend logout error
            }
        }
        storeLogout();
    }, [sessionToken, storeLogout]);

    return {
        isConnected,
        address,
        sessionToken,
        isLoading,
        error,
        connect,
        logout
    };
}
