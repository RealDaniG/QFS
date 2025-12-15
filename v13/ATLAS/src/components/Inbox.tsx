
import React, { useEffect, useState } from 'react';

interface InboxThread {
    peer: string;
    last_active: string;
    msg_id?: string;
}

interface InboxProps {
    token: string;
    currentUserWallet: string;
    onOpenChat: (peer: string) => void;
}

export const Inbox: React.FC<InboxProps> = ({ token, currentUserWallet, onOpenChat }) => {
    const [threads, setThreads] = useState<InboxThread[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchThreads = async () => {
            setLoading(true);
            try {
                // Pass token as query param for simplicity in V1 (Auth middleware handles header usually)
                // The backend impl accepts query param 'token' 
                const res = await fetch(`/v1/chat/threads?token=${token}`);
                if (res.ok) {
                    const data = await res.json();
                    // Sort by recency
                    data.sort((a: InboxThread, b: InboxThread) =>
                        new Date(b.last_active).getTime() - new Date(a.last_active).getTime()
                    );
                    setThreads(data);
                }
            } catch (e) {
                console.error("Failed to load threads", e);
            } finally {
                setLoading(false);
            }
        };

        if (token) fetchThreads();
    }, [token]);

    return (
        <div className="bg-white rounded-xl shadow border border-gray-100 p-4 w-full md:w-80 h-96 overflow-y-auto">
            <h3 className="font-bold text-gray-800 mb-4 px-2">Messages</h3>

            {loading && <div className="text-gray-400 text-sm px-2">Loading...</div>}

            {!loading && threads.length === 0 && (
                <div className="text-gray-400 text-sm px-2 py-4 text-center">
                    No conversations yet.
                </div>
            )}

            <div className="flex flex-col gap-1">
                {threads.map(thread => (
                    <button
                        key={thread.peer}
                        onClick={() => onOpenChat(thread.peer)}
                        className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-lg transition-colors text-left"
                    >
                        {/* Avatar Stub */}
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-purple-400 to-blue-500 flex-shrink-0"></div>

                        <div className="flex-1 min-w-0">
                            <div className="font-medium text-sm text-gray-900 truncate">
                                {thread.peer.slice(0, 8)}...{thread.peer.slice(-6)}
                            </div>
                            <div className="text-xs text-gray-500">
                                {new Date(thread.last_active).toLocaleDateString()}
                            </div>
                        </div>
                    </button>
                ))}
            </div>

            {/* New Chat Button Stub for Future */}
            <div className="mt-4 pt-4 border-t text-center">
                <button className="text-blue-600 text-sm font-medium hover:underline">
                    + Start New Chat
                </button>
            </div>
        </div>
    );
};
