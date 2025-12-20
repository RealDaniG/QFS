/**
 * useAuth Hook
 * Manages user identity (DID + Keys) for Phase 1
 * Uses localStorage for persistence (Note: In Phase 2/3 this moves to secure wallet)
 */

'use client';

import { useState, useEffect } from 'react';
import { generateDIDKeyPair } from '@/lib/did/signer';
import { toString as uint8ArrayToString } from 'uint8arrays/to-string';
import { fromString as uint8ArrayFromString } from 'uint8arrays/from-string';

interface AuthState {
    did: string | null;
    privateKey: Uint8Array | null;
    publicKey: Uint8Array | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: Error | null;
}

const STORAGE_KEY = 'atlas_identity_v1';

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
                // Load existing identity
                const data = JSON.parse(stored);
                setState({
                    did: data.did,
                    privateKey: uint8ArrayFromString(data.privateKey, 'base16'),
                    publicKey: uint8ArrayFromString(data.publicKey, 'base16'),
                    isAuthenticated: true,
                    isLoading: false,
                    error: null,
                });
            } else {
                // Generate new identity
                const keypair = await generateDIDKeyPair();

                // Save to storage
                const storageData = {
                    did: keypair.did,
                    privateKey: uint8ArrayToString(keypair.privateKey, 'base16'),
                    publicKey: uint8ArrayToString(keypair.publicKey, 'base16'),
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
