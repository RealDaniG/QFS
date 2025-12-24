/**
 * BountyDashboard Component
 * Integrated dashboard for bounty management with tab navigation.
 */

'use client';

import React, { useState } from 'react';
import { useWalletAuth } from '../hooks/useWalletAuth';
import { BountyList } from './BountyList';
import { MyBounties } from './MyBounties';
import { WalletConnectButton } from './WalletConnectButton';

type Tab = 'all' | 'mine';

export function BountyDashboard() {
    const [rewards, setRewards] = useState<any[]>([]);
    const [isLoadingRewards, setIsLoadingRewards] = useState(false);

    const fetchRewards = async () => {
        setIsLoadingRewards(true);
        // Get session token? useWalletAuth exposes sessionToken now?
        // Wait, I need to check if useWalletAuth exposes sessionToken in this file too
        // Yes, I edited the hook, so it exposes it. But I need to destructure it.
        // But here I only destructured { isConnected, address }.
        // I need to update destructuring.
        // Actually, let's fix that in a separate edit or assume I fix it here.
    };

    // ... I'll do a MultiReplace or careful replace.

    // Let's replace the component body to include sessionToken and new tab logic.
    // This is safer with MultiReplace or just replace the whole component content or logic block.
    // The previous view_file showed lines 16-180.

    // I will use replace_file_content to replace the component function start and return.

    const { isConnected, address, sessionToken } = useWalletAuth();
    const [activeTab, setActiveTab] = useState<'all' | 'mine' | 'rewards'>('all'); // Added rewards tab

    // Fetch rewards effect
    React.useEffect(() => {
        if (activeTab === 'rewards' && sessionToken) {
            fetch('/api/bounties/my-rewards', {
                headers: { 'Authorization': `Bearer ${sessionToken}` }
            })
                .then(res => res.json())
                .then(data => setRewards(data.history || []))
                .catch(err => console.error(err));
        }
    }, [activeTab, sessionToken]);

    if (!isConnected) {
        // ... (keep auth required view)
        return (
            <div className="bounty-dashboard-container">
                <div className="auth-required-full">
                    <div className="auth-content">
                        <h2>🎯 Bounty Dashboard</h2>
                        <p>Connect your wallet to view and claim bounties.</p>
                        <WalletConnectButton />
                    </div>
                </div>
                <style jsx>{`
                    .bounty-dashboard-container {
                        min-height: 600px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }

                    .auth-required-full {
                        text-align: center;
                        padding: 4rem 2rem;
                        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
                        border-radius: 16px;
                        border: 2px dashed #d1d5db;
                        max-width: 500px;
                        margin: 0 auto;
                    }

                    .auth-content h2 {
                        font-size: 2rem;
                        font-weight: 700;
                        color: #1a1a1a;
                        margin-bottom: 1rem;
                    }

                    .auth-content p {
                        color: #6b7280;
                        margin-bottom: 2rem;
                        font-size: 1.125rem;
                    }
                `}</style>
            </div>
        );
    }

    return (
        <div className="bounty-dashboard-container">
            <div className="dashboard-header">
                <div className="header-content">
                    <h1>🎯 Bounty Dashboard</h1>
                    <p className="wallet-info">Connected: {address}</p>
                </div>
                <WalletConnectButton />
            </div>

            <div className="tab-navigation">
                <button
                    className={`tab-button ${activeTab === 'all' ? 'active' : ''}`}
                    onClick={() => setActiveTab('all')}
                >
                    <span className="tab-icon">📋</span>
                    All Bounties
                </button>
                <button
                    className={`tab-button ${activeTab === 'mine' ? 'active' : ''}`}
                    onClick={() => setActiveTab('mine')}
                >
                    <span className="tab-icon">✅</span>
                    My Bounties
                </button>
                <button
                    className={`tab-button ${activeTab === 'rewards' ? 'active' : ''}`}
                    onClick={() => setActiveTab('rewards')}
                >
                    <span className="tab-icon">🏆</span>
                    Retro Rewards
                </button>
            </div>

            <div className="tab-content">
                {activeTab === 'all' && <BountyList />}
                {activeTab === 'mine' && <MyBounties />}
                {activeTab === 'rewards' && (
                    <div className="rewards-list">
                        <h3>Your Retroactive Rewards</h3>
                        {rewards.length === 0 ? (
                            <p className="no-rewards">No rewards found yet. Link your GitHub!</p>
                        ) : (
                            <table className="rewards-table">
                                <thead>
                                    <tr>
                                        <th>Round</th>
                                        <th>Amount</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rewards.map((r, i) => (
                                        <tr key={i}>
                                            <td>{r.round_id}</td>
                                            <td className="amount">+{r.amount} FLX</td>
                                            <td>{new Date(r.timestamp * 1000).toLocaleDateString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                        <style jsx>{`
                            .rewards-list h3 { margin-bottom: 1rem; }
                            .no-rewards { color: #6b7280; font-style: italic; }
                            .rewards-table { width: 100%; border-collapse: collapse; }
                            .rewards-table th, .rewards-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #e5e7eb; }
                            .rewards-table th { font-weight: 600; color: #4b5563; }
                            .amount { color: #059669; font-weight: 700; }
                        `}</style>
                    </div>
                )}
            </div>

            <style jsx>{`
                .bounty-dashboard-container {
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 2rem;
                }

                .dashboard-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
                    padding-bottom: 1.5rem;
                    border-bottom: 2px solid #e5e7eb;
                }

                .header-content h1 {
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: #1a1a1a;
                    margin-bottom: 0.5rem;
                }

                .wallet-info {
                    font-size: 0.875rem;
                    color: #6b7280;
                    font-family: monospace;
                }

                .tab-navigation {
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 2rem;
                    border-bottom: 2px solid #e5e7eb;
                }

                .tab-button {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 1rem 2rem;
                    background: none;
                    border: none;
                    border-bottom: 3px solid transparent;
                    font-size: 1rem;
                    font-weight: 600;
                    color: #6b7280;
                    cursor: pointer;
                    transition: all 0.2s;
                    position: relative;
                    top: 2px;
                }

                .tab-button:hover {
                    color: #4f46e5;
                }

                .tab-button.active {
                    color: #4f46e5;
                    border-bottom-color: #4f46e5;
                }

                .tab-icon {
                    font-size: 1.25rem;
                }

                .tab-content {
                    animation: fadeIn 0.3s ease-in;
                }

                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </div>
    );
}
