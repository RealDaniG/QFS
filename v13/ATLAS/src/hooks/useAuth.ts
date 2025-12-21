/**
 * useAuth Hook
 * Manages user identity (DID + Keys) for Phase 1
 */

'use client';

import { useState, useEffect } from 'react';
import { generateDIDKeyPair } from '@/lib/did/signer';

interface AuthState {
    did: string | null;
    privateKey: Uint8Array | null;
    publicKey: Uint8Array | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: Error | null;
}

const STORAGE_KEY = 'atlas_identity_v1';

// Inline helpers to avoid uint8arrays dependency
function hexToBytes(hex: string): Uint8Array {
    if (hex.length % 2 !== 0) throw new Error("Invalid hex string")
    const bytes = new Uint8Array(hex.length / 2)
    for (let i = 0; i < hex.length; i += 2) {
        bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16)
    }
    return bytes
}

function bytesToHex(bytes: Uint8Array): string {
    return Array.from(bytes)
        .map(b => b.toString(16).padStart(2, '0'))
        .join('')
}

export function useAuth() {
    const [state, setState] = useState<AuthState>({
        did: null,
        privateKey: null,
        publicKey: null,
        isAuthenticated: false,
        isLoading: true,
        error: null,
    });

    useEffect(() => {
        loadIdentity();
    }, []);

    const loadIdentity = async () => {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);

            if (stored) {
                const data = JSON.parse(stored);
                setState({
                    did: data.did,
                    privateKey: hexToBytes(data.privateKey),
                    publicKey: hexToBytes(data.publicKey),
                    isAuthenticated: true,
                    isLoading: false,
                    error: null,
                });
            } else {
                const keypair = await generateDIDKeyPair();

                const storageData = {
                    did: keypair.did,
                    privateKey: bytesToHex(keypair.privateKey),
                    publicKey: bytesToHex(keypair.publicKey),
                };
                localStorage.setItem(STORAGE_KEY, JSON.stringify(storageData));

                setState({
                    did: keypair.did,
                    privateKey: keypair.privateKey,
                    publicKey: keypair.publicKey,
                    isAuthenticated: true,
                    isLoading: false,
                    error: null,
                });
            }
        } catch (error) {
            console.error('Failed to load identity:', error);
            setState(prev => ({ ...prev, isLoading: false, error: error as Error }));
        }
    };

    const logout = () => {
        localStorage.removeItem(STORAGE_KEY);
        setState({
            did: null,
            privateKey: null,
            publicKey: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
        });
    };

    return { ...state, logout };
}
