'use client';

import { useEffect, useState } from 'react';
import { useP2P } from '@/lib/p2p/P2PContext';
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

export function useSecureChat(spaceId: string = 'general') {
    const { isConnected, connectToSpace, sendMessage: sendP2PMessage, messages: p2pMessages, currentSpaceId } = useP2P();
    const { address } = useWalletAuth();
    const [isLoading, setIsLoading] = useState(true);

    // Auto-connect to space on mount
    useEffect(() => {
        if (!isConnected || currentSpaceId !== spaceId) {
            connectToSpace(spaceId).catch(console.error);
        }
    }, [spaceId, isConnected, currentSpaceId, connectToSpace]);

    // Format messages for UI
    const formattedMessages: ChatMessage[] = p2pMessages.map((msg: any, index) => {
        return {
            id: msg.id || `msg-${index}`,
            sender: msg.sender || address || 'Anonymous',
            text: msg.content || msg.text || '',
            timestamp: msg.timestamp ? new Date(msg.timestamp).toISOString() : new Date().toISOString(),
            isOwn: msg.isOwn !== undefined ? msg.isOwn : (msg.sender === address),
            status: msg.status || 'read'
        };
    });

    useEffect(() => {
        if (isConnected && currentSpaceId === spaceId) {
            setIsLoading(false);
        }
    }, [isConnected, currentSpaceId, spaceId]);

    const sendMessage = async (text: string) => {
        const payload = {
            content: text,
            timestamp: Date.now(),
            sender: address
        };
        await sendP2PMessage(payload);
    };

    return {
        messages: formattedMessages,
        sendMessage,
        isLoading
    };
}
