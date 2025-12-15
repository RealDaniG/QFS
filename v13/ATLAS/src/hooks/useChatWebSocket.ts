
import { useEffect, useRef, useState, useCallback } from 'react';
import { SecureMessageV2Payload } from '../security/secureMessageV2';

interface UseChatWebSocketProps {
    token: string | null;
    onMessage: (payload: SecureMessageV2Payload) => void;
    url?: string;
}

export const useChatWebSocket = ({ token, onMessage, url = "/v1/chat/ws" }: UseChatWebSocketProps) => {
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!token) return;

        // Construct URL with token
        // Handle absolute vs relative URL or ws/wss
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        // If url starts with /, prepend host. If full url, use as is.
        const wsUrl = url.startsWith('/')
            ? `${protocol}//${host}${url}?token=${token}`
            : `${url}?token=${token}`;

        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log("Chat WS Connected");
            setIsConnected(true);
            setError(null);
        };

        socket.onclose = (event) => {
            console.log("Chat WS Closed", event.code, event.reason);
            setIsConnected(false);
            // Reconnect logic could go here (exponential backoff)
        };

        socket.onerror = (err) => {
            console.error("Chat WS Error", err);
            setError("Connection error");
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // Expecting payload wrapper or direct SecureMessageV2Payload
                // The backend sends { ...SecureMessageV2Payload, id, type }
                // We cast and pass to handler
                onMessage(data as SecureMessageV2Payload);
            } catch (e) {
                console.error("Failed to parse incoming message", e);
            }
        };

        ws.current = socket;

        return () => {
            socket.close();
        };
    }, [token, url, onMessage]); // Re-connect if token changes

    const sendMessage = useCallback((payload: any) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(payload));
        } else {
            console.warn("Cannot send: WS not open");
        }
    }, []);

    return { isConnected, error, sendMessage };
};
