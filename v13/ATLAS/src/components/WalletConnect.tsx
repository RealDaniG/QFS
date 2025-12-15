
import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';

// Props for the component
interface WalletConnectProps {
    onConnect?: (wallet: string, token: string) => void;
    apiUrl?: string;
}

export const WalletConnect: React.FC<WalletConnectProps> = ({
    onConnect,
    apiUrl = "/v1/auth"
}) => {
    const [wallet, setWallet] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Check if Ethereum provider exists
    useEffect(() => {
        // Capture referral code from URL
        const params = new URLSearchParams(window.location.search);
        const refCode = params.get("ref");
        if (refCode) {
            localStorage.setItem("pending_referral", refCode);
            // Optional: Strip from URL for clean UI
            window.history.replaceState({}, '', window.location.pathname);
        }

        if (window.ethereum) {
            window.ethereum.on('accountsChanged', (accounts: string[]) => {
                if (accounts.length > 0) {
                    setWallet(accounts[0]);
                } else {
                    setWallet(null);
                }
            });
        }
    }, []);

    const connectWallet = async () => {
        setLoading(true);
        setError(null);

        try {
            if (!window.ethereum) {
                throw new Error("MetaMask is not installed!");
            }

            // 1. Request Account Access
            const provider = new ethers.providers.Web3Provider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            const signer = provider.getSigner();
            const address = await signer.getAddress();
            setWallet(address);

            // 2. Request Challenge
            const challengeResponse = await fetch(`${apiUrl}/challenge`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wallet: address })
            });

            if (!challengeResponse.ok) throw new Error("Failed to get challenge");
            const { nonce } = await challengeResponse.json();

            // 3. Sign Challenge
            const signature = await signer.signMessage(nonce);

            // 4. Login
            const loginResponse = await fetch(`${apiUrl}/connect-wallet`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    wallet: address,
                    nonce,
                    signature,
                    referral_code: localStorage.getItem("pending_referral") || undefined
                })
            });

            if (!loginResponse.ok) throw new Error("Authentication failed");
            const { token } = await loginResponse.json();

            // Success
            localStorage.setItem('atlas_token', token);
            localStorage.removeItem("pending_referral"); // Clear used code
            if (onConnect) onConnect(address, token);

        } catch (err: any) {
            setError(err.message || "Connection failed");
        } finally {
            setLoading(false);
        }
    };

    const disconnect = () => {
        setWallet(null);
        localStorage.removeItem('atlas_token');
    };

    return (
        <div className="flex flex-col items-center gap-4 p-4 border rounded-lg shadow-sm">
            {error && (
                <div className="text-red-500 text-sm bg-red-50 p-2 rounded">
                    {error}
                </div>
            )}

            {wallet ? (
                <div className="flex items-center gap-2">
                    <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-700">Connected</span>
                        <span className="text-xs font-mono text-gray-500">
                            {wallet.slice(0, 6)}...{wallet.slice(-4)}
                        </span>
                    </div>
                    <button
                        onClick={disconnect}
                        className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded"
                    >
                        Disconnect
                    </button>
                    {/* Visual indicator of "Green" status (Generic for now) */}
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                </div>
            ) : (
                <button
                    onClick={connectWallet}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 font-medium transition-colors"
                >
                    {loading ? "Connecting..." : "Connect Wallet"}
                </button>
            )}
        </div>
    );
};
