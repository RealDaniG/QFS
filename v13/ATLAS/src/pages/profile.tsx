
import React, { useEffect, useState } from 'react';
import { WalletConnect } from '../components/WalletConnect';

// Types (should ideally act as shared types or imported from generated client)
interface UserProfile {
    wallet: string;
    display_name?: string;
    avatar_url?: string;
    created_at: string;
    coherence_score: number;
    genesis_points: number;
    referral_code: string;
}

interface ReferralStats {
    referral_code: string;
    referral_count: number;
    recent_referees: any[];
}

export const ProfilePage: React.FC = () => {
    const [token, setToken] = useState<string | null>(localStorage.getItem('atlas_token'));
    const [wallet, setWallet] = useState<string | null>(null);
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [referralStats, setReferralStats] = useState<ReferralStats | null>(null);
    const [loading, setLoading] = useState(false);
    const [editMode, setEditMode] = useState(false);
    const [displayName, setDisplayName] = useState('');

    useEffect(() => {
        // Simple JWT decode to get wallet (sub) if token exists
        if (token) {
            try {
                const base64Url = token.split('.')[1];
                const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
                    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                }).join(''));
                const payload = JSON.parse(jsonPayload);
                setWallet(payload.sub);
                fetchProfile(payload.sub);
            } catch (e) {
                console.error("Invalid token", e);
                setToken(null);
            }
        }
    }, [token]);

    const fetchProfile = async (walletAddr: string) => {
        setLoading(true);
        try {
            const res = await fetch(`/v1/users/${walletAddr}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setProfile(data);
                setDisplayName(data.display_name || '');
                // Fetch stats too
                const statsRes = await fetch(`/v1/users/${walletAddr}/referrals`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (statsRes.ok) setReferralStats(await statsRes.json());
            }
        } finally {
            setLoading(false);
        }
    };

    const handleUpdate = async () => {
        if (!wallet || !token) return;

        try {
            const res = await fetch(`/v1/users/${wallet}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ display_name: displayName })
            });

            if (res.ok) {
                const updated = await res.json();
                setProfile(updated);
                setEditMode(false);
            }
        } catch (e) {
            console.error("Update failed", e);
        }
    };

    if (!token) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
                <h1 className="text-2xl font-bold mb-8 text-gray-800">Welcome to ATLAS x QFS</h1>
                <p className="mb-8 text-gray-600">Connect your wallet to access your profile and Coherence Score.</p>
                <WalletConnect onConnect={(w, t) => setToken(t)} />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-8">
            <header className="flex justify-between items-center mb-12">
                <h1 className="text-3xl font-bold text-gray-900">Your Identity</h1>
                <WalletConnect onConnect={(w, t) => setToken(t)} />
            </header>

            {loading && <div className="text-gray-500">Loading profile...</div>}

            {profile && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Profile Card */}
                    <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
                                {profile.avatar_url ? <img src={profile.avatar_url} alt="Profile Avatar" className="rounded-full" /> : (profile.display_name?.[0] || 'U')}
                            </div>
                            <div>
                                {editMode ? (
                                    <div className="flex gap-2">
                                        <input
                                            value={displayName}
                                            onChange={(e) => setDisplayName(e.target.value)}
                                            className="border p-1 rounded"
                                            placeholder="Display Name"
                                        />
                                        <button onClick={handleUpdate} className="text-green-600 font-bold">Save</button>
                                        <button onClick={() => setEditMode(false)} className="text-gray-400">Cancel</button>
                                    </div>
                                ) : (
                                    <h2 className="text-xl font-bold flex gap-2 items-center">
                                        {profile.display_name || "Anonymous User"}
                                        <button onClick={() => setEditMode(true)} className="text-xs text-blue-500 font-medium">EDIT</button>
                                    </h2>
                                )}
                                <p className="text-sm text-gray-400 font-mono">{profile.wallet}</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mt-6">
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <span className="text-xs text-gray-500 uppercase tracking-wider">Genesis Points</span>
                                <div className="text-2xl font-bold text-gray-900">{profile.genesis_points}</div>
                            </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <span className="text-xs text-gray-500 uppercase tracking-wider">Referral Code</span>
                                <div className="text-xl font-mono text-indigo-600 cursor-pointer"
                                    onClick={() => navigator.clipboard.writeText(window.location.origin + "?ref=" + profile.referral_code)}
                                    title="Click to copy invite link">
                                    {profile.referral_code}
                                </div>
                                <div className="text-xs text-gray-400 mt-1">
                                    {referralStats?.referral_count || 0} Invites Active
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Coherence Card */}
                    <div className="bg-gradient-to-br from-gray-900 to-black p-6 rounded-xl shadow-lg text-white border border-gray-800">
                        <h3 className="text-lg font-semibold mb-4 text-gray-300">QFS Coherence Status</h3>

                        <div className="flex items-center justify-between mb-8">
                            <span className="text-gray-400">Current Score</span>
                            <span className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                                {profile.coherence_score.toFixed(2)}
                            </span>
                        </div>

                        <div className="relative h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div
                                className="absolute top-0 left-0 h-full bg-blue-500 transition-all duration-1000"
                                style={{ width: `${Math.min(profile.coherence_score * 100, 100)}%` }}
                            ></div>
                        </div>
                        <p className="mt-4 text-xs text-gray-500">
                            Higher coherence increases your influence in the QFS Consensus and governance weight.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};
