
import React, { useState, useEffect, useRef } from 'react';
import { SecureMessageClient, SecureMessageV2Payload } from '../security/secureMessageV2';
import { useChatWebSocket } from '../hooks/useChatWebSocket';

interface ChatWindowProps {
    token: string;
    currentUserWallet: string;
    peerWallet: string;
    onClose?: () => void;
}

interface DisplayMessage {
    id: string; // nonce or hash
    text: string;
    sender: string;
    ts: number;
    pending?: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
    token,
    currentUserWallet,
    peerWallet,
    onClose
}) => {
    const [messages, setMessages] = useState<DisplayMessage[]>([]);
    const [input, setInput] = useState('');
    const [cryptoReady, setCryptoReady] = useState(false);

    // Crypto Client Ref (persists across renders)
    const cryptoClient = useRef(new SecureMessageClient());
    // Auto-scroll ref
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Initialize Crypto (Derived Key)
    useEffect(() => {
        const initCrypto = async () => {
            // TODO: In real app, perform ECDH or fetch shared secret.
            // For V1 MVP: Deterministic key for ANY pair (unsafe, dev only)
            // or a hardcoded "room" secret.
            // To make it functional for demo, we'll sort wallets and hash them
            // to get a consistent "room key".
            const sortedWallets = [currentUserWallet, peerWallet].sort().join(':');
            const encoder = new TextEncoder();
            const hashBuffer = await window.crypto.subtle.digest('SHA-256', encoder.encode(sortedWallets));
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

            await cryptoClient.current.initFromSecret(hashHex);
            setCryptoReady(true);
        };
        initCrypto();
    }, [currentUserWallet, peerWallet]);

    // Handle Incoming Messages
    const handleIncoming = async (payload: SecureMessageV2Payload) => {
        try {
            // Decrypt
            const plaintext = await cryptoClient.current.decrypt(payload);

            // Add to UI
            // Assuming sender is in payload metadata or inferred
            // (Our backend echoes messages, so we see our own too)
            const sender = payload.sender || (payload.ciphertext ? 'Unknown' : 'System');

            setMessages(prev => {
                // Deduplicate by hash/nonce
                if (prev.some(m => m.id === payload.hash)) return prev;
                return [...prev, {
                    id: payload.hash,
                    text: plaintext,
                    sender: sender,
                    ts: payload.ts
                }].sort((a, b) => a.ts - b.ts);
            });
        } catch (e) {
            console.error("Failed to decrypt message", e);
        }
    };

    // WebSocket Hook
    const { isConnected, sendMessage } = useChatWebSocket({
        token,
        onMessage: handleIncoming
    });

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || !cryptoReady || !isConnected) return;

        try {
            // Encrypt
            const encrypted = await cryptoClient.current.encrypt(input);

            // Add metadata for routing
            // (Note: SecureMessageV2Payload defines strict fields for crypto, 
            // but we extend it for the socket protocol)
            const socketPayload = {
                ...encrypted,
                recipient: peerWallet,
                sender: currentUserWallet
            };

            // Send
            sendMessage(socketPayload);

            // Optimistic UI update (optional, but WS echo is safer for sync)
            /*
            setMessages(prev => [...prev, {
                id: encrypted.hash,
                text: input,
                sender: currentUserWallet,
                ts: encrypted.ts,
                pending: true
            }]);
            */

            setInput('');
        } catch (e) {
            console.error("Send failed", e);
        }
    };

    return (
        <div className="flex flex-col h-96 w-80 bg-white shadow-xl rounded-t-lg border border-gray-200 fixed bottom-0 right-4">
            {/* Header */}
            <div className="bg-blue-600 text-white p-3 rounded-t-lg flex justify-between items-center">
                <div className="flex flex-col">
                    <span className="font-bold text-sm">Chat with {peerWallet.slice(0, 6)}...</span>
                    <span className="text-xs opacity-75">
                        {isConnected ? (cryptoReady ? "Secure & Connected" : "Initializing Crypto...") : "Connecting..."}
                    </span>
                </div>
                <button onClick={onClose} className="text-white hover:text-gray-200">✕</button>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2 bg-gray-50">
                {messages.map(m => {
                    const isMe = m.sender === currentUserWallet;
                    return (
                        <div key={m.id} className={`max-w-[80%] p-2 rounded-lg text-sm ${isMe ? 'bg-blue-500 text-white self-end' : 'bg-white border self-start'}`}>
                            <div>{m.text}</div>
                            <div className={`text-[10px] mt-1 ${isMe ? 'text-blue-100' : 'text-gray-400'}`}>
                                {new Date(m.ts * 1000).toLocaleTimeString()}
                            </div>
                        </div>
                    );
                })}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-2 border-t bg-white flex gap-2">
                <input
                    className="flex-1 border rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-500"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSend()}
                    placeholder="Type a message..."
                    disabled={!isConnected || !cryptoReady}
                />
                <button
                    onClick={handleSend}
                    disabled={!isConnected || !cryptoReady}
                    className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
                >
                    Send
                </button>
            </div>
        </div>
    );
};
