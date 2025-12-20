'use client';

import { useState, useEffect, useCallback } from 'react';
import { atlasFetch } from '../lib/api';
import { useWalletAuth } from './useWalletAuth';

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
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchHistory = useCallback(async () => {
        if (!isConnected || !sessionToken) return;

        try {
            const res = await atlasFetch('/api/v18/chat/history');
            if (res.ok) {
                const data = await res.json();
                // Map to our interface
                setMessages(data.map((msg: any) => ({
                    ...msg,
                    isOwn: msg.sender === address || msg.sender === 'You'
                })));
            }
        } catch (e) {
            console.error("Failed to fetch chat history:", e);
        } finally {
            setIsLoading(false);
        }
    }, [isConnected, sessionToken, address]);

    useEffect(() => {
        fetchHistory();
        const interval = setInterval(fetchHistory, 10000);
        return () => clearInterval(interval);
    }, [fetchHistory]);

    const sendMessage = async (text: string) => {
        if (!isConnected || !sessionToken || !text.trim()) return;

        // Optimistic update
        const newMessage: ChatMessage = {
            id: `temp_${Date.now()}`,
            sender: 'You',
            text: text,
            timestamp: new Date().toISOString(),
            isOwn: true
        };
        setMessages(prev => [...prev, newMessage]);

        try {
            const res = await atlasFetch('/api/v18/chat/send', {
                method: 'POST',
                body: JSON.stringify({ text })
            });

            if (res.ok) {
                const data = await res.json();
                // Replace optimistic message with real message if needed,
                // or just refresh history
                setMessages(prev => prev.filter(m => m.id !== newMessage.id));
                setMessages(prev => [...prev, {
                    ...data.message,
                    isOwn: true
                }]);
            }
        } catch (e) {
            console.error("Failed to send message:", e);
            // Optionally remove optimistic message on failure
        }
    };

    return {
        messages,
        isLoading,
        sendMessage,
        refresh: fetchHistory
    };
}
