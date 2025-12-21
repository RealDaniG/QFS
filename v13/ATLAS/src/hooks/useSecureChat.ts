'use client';

import { useState, useEffect, useCallback } from 'react';
import { atlasFetch } from '../lib/api';
import { useWalletAuth } from './useWalletAuth';
import { useP2P } from '../contexts/P2PContext';

export interface ChatMessage {
    id: string;
    sender: string;
    text: string;
    timestamp: string;
    isOwn: boolean;
    ledgerId?: string;
    status?: 'sent' | 'delivered' | 'read';
}

export function useSecureChat() {
    const { address, isConnected, sessionToken } = useWalletAuth();
    const { node, isReady } = useP2P();
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [sessionKey, setSessionKey] = useState<Uint8Array | null>(null);

    // 1. Fetch Session Key for Space
    useEffect(() => {
        if (!isConnected || !sessionToken || !address) return;

        const getSessionKey = async () => {
            try {
                // Mocking /api/p2p/session response for now since the route might not exist yet
                // In v19 real implementation, this comes from backend.
                // For "Empty AD" verification, we can use a deterministic test key or fetch it.
                // Converting backend session_keys.py logic to TS would be ideal, but for now let's assume backend gives it.

                // TEMPORARY: using a fixed test key to match Python scripts until API route is confirmed
                // Key: 00010203...0f (Same as scripts)
                const mockKey = new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]);
                setSessionKey(mockKey);
            } catch (e) {
                console.error("Failed to get session keys", e);
            }
        };
        getSessionKey();
    }, [isConnected, sessionToken, address]);

    // 2. Subscribe to P2P Messages
    useEffect(() => {
        if (!isReady || !node || !sessionKey) return;

        const handleP2PMessage = async (envelope: any, decrypted: any) => {
            console.log("Received P2P Message:", envelope);
            // In a real app, we would decrypt here using sessionKey if not already done by Node
            // But P2PNode stub just passes ciphertext. 
            // We need to implement decryption here or trust the node.

            // For now, let's just append the raw envelope data to UI to prove receipt
            setMessages(prev => [{
                id: `p2p-${Date.now()}-${Math.random()}`,
                sender: envelope.sender_pubkey,
                text: `[Encrypted] ${envelope.payload_ciphertext.substring(0, 10)}...`,
                timestamp: new Date().toISOString(),
                isOwn: envelope.sender_pubkey === address,
                status: 'read'
            }, ...prev]);
        };

        const spaceId = 'general'; // Default space
        node.joinSpace(spaceId, handleP2PMessage);

        return () => {
            // Cleanup if needed (node.leaveSpace)
            // node.leaveSpace(spaceId);
        };
    }, [isReady, node, sessionKey, address]);

    const fetchHistory = useCallback(async () => {
        if (!isConnected || !sessionToken) return;
        try {
            const res = await fetch('http://localhost:8000/api/chat/messages?room_id=general', {
                headers: { 'Authorization': `Bearer ${sessionToken}` }
            });
            if (res.ok) {
                const data = await res.json();
                // Merge strategies would go here. For now, replacing
                setMessages(data.messages.map((msg: any) => ({
                    id: msg.id,
                    sender: msg.author,
                    text: msg.content,
                    timestamp: new Date(msg.timestamp * 1000).toISOString(),
                    isOwn: msg.author === address,
                    status: 'read'
                })));
            }
        } catch (e) {
            console.error("Failed to fetch history", e);
        } finally {
            setIsLoading(false);
        }
    }, [isConnected, sessionToken, address]);

    // Polling fallback
    useEffect(() => {
        fetchHistory();
        const interval = setInterval(fetchHistory, 10000);
        return () => clearInterval(interval);
    }, [fetchHistory]);

    const sendMessage = async (text: string) => {
        if (!node || !sessionKey || !address || !sessionToken) {
            console.error("P2P not ready");
            return;
        }

        try {
            // Import dynamically to avoid cycle if possible, or assume it's available
            const { MessageCommitter } = await import('../lib/p2p/message-committer');

            // Using Wallet Address as Mock Private Key (See "MOCKQPC" decision in v19 plan)
            const committer = new MessageCommitter(
                'http://localhost:8000',
                address, // "Private Key"
                'general',
                sessionKey
            );

            const payload = { content: text, timestamp: Date.now() };
            const { envelope, evidenceHash } = await committer.createAndCommit(
                address,
                payload,
                "chat.message",
                sessionToken
            );

            console.log("Committed Evidence:", evidenceHash);

            await node.publishToSpace('general', envelope);

            // Optimistic Update
            setMessages(prev => [{
                id: `temp-${Date.now()}`,
                sender: address,
                text: text,
                timestamp: new Date().toISOString(),
                isOwn: true,
                status: 'sent'
            }, ...prev]);

        } catch (e) {
            console.error("Failed to send P2P message:", e);
        }
    };

    return {
        messages,
        isLoading,
        sendMessage,
        refresh: fetchHistory
    };
}
