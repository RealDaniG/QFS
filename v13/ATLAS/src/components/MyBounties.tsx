/**
 * MyBounties Component
 * Displays bounties claimed by the authenticated user.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useWalletAuth } from '../hooks/useWalletAuth';

interface Bounty {
    id: string;
    title: string;
    reward: number;
    status: string;
    claimant: string | null;
}

export function MyBounties() {
    const { isConnected, sessionToken, address } = useWalletAuth();
    const [bounties, setBounties] = useState<Bounty[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isConnected && sessionToken) {
            fetchMyBounties();
        }
    }, [isConnected, sessionToken]);

    const fetchMyBounties = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('/api/bounties/my-bounties', {
                headers: {
                    'Authorization': `Bearer ${sessionToken}`
                }
            });

            if (!res.ok) {
                if (res.status === 403) {
                    throw new Error('Authentication required');
                }
                throw new Error('Failed to fetch your bounties');
            }

            const data = await res.json();
            setBounties(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (!isConnected) {
        return (
            <div className="my-bounties-container">
                <div className="auth-required">
                    <h3>🔒 Authentication Required</h3>
                    <p>Please connect your wallet to view your bounties.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="my-bounties-container">
            <div className="my-bounties-header">
                <div>
                    <h2>My Bounties</h2>
                    <p className="wallet-address">Connected: {address}</p>
                </div>
                <button onClick={fetchMyBounties} disabled={loading}>
                    {loading ? 'Loading...' : '🔄 Refresh'}
                </button>
            </div>

            {error && (
                <div className="error-message">
                    ⚠️ {error}
                </div>
            )}

            {loading && bounties.length === 0 ? (
                <div className="loading-state">Loading your bounties...</div>
            ) : (
                <div className="bounty-list">
                    {bounties.map((bounty) => (
                        <div key={bounty.id} className="bounty-item">
                            <div className="bounty-info">
                                <h3>{bounty.title}</h3>
                                <div className="bounty-meta">
                                    <span className="bounty-id">ID: {bounty.id}</span>
                                    <span className={`status-badge status-${bounty.status.toLowerCase()}`}>
                                        {bounty.status}
                                    </span>
                                </div>
                            </div>
                            <div className="bounty-reward">
                                <span className="reward-label">Reward</span>
                                <span className="reward-value">{bounty.reward} CHR</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {!loading && bounties.length === 0 && (
                <div className="empty-state">
                    <div className="empty-icon">📋</div>
                    <h3>No Bounties Claimed Yet</h3>
                    <p>Visit the Bounty List to claim your first bounty!</p>
                </div>
            )}

            <style jsx>{`
                .my-bounties-container {
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 2rem;
                }

                .my-bounties-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
                }

                .my-bounties-header h2 {
                    font-size: 2rem;
                    font-weight: 700;
                    color: #1a1a1a;
                    margin-bottom: 0.25rem;
                }

                .wallet-address {
                    font-size: 0.875rem;
                    color: #6b7280;
                    font-family: monospace;
                }

                .my-bounties-header button {
                    padding: 0.75rem 1.5rem;
                    background: #4f46e5;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: background 0.2s;
                }

                .my-bounties-header button:hover:not(:disabled) {
                    background: #4338ca;
                }

                .my-bounties-header button:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }

                .auth-required {
                    text-align: center;
                    padding: 4rem 2rem;
                    background: #f9fafb;
                    border-radius: 12px;
                    border: 2px dashed #d1d5db;
                }

                .auth-required h3 {
                    font-size: 1.5rem;
                    margin-bottom: 0.5rem;
                    color: #374151;
                }

                .error-message {
                    padding: 1rem;
                    background: #fee2e2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    color: #991b1b;
                    margin-bottom: 1rem;
                }

                .loading-state {
                    text-align: center;
                    padding: 3rem;
                    color: #6b7280;
                }

                .bounty-list {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }

                .bounty-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 1.5rem;
                    transition: box-shadow 0.2s, transform 0.2s;
                }

                .bounty-item:hover {
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    transform: translateX(4px);
                }

                .bounty-info {
                    flex: 1;
                }

                .bounty-info h3 {
                    font-size: 1.125rem;
                    font-weight: 600;
                    color: #111827;
                    margin-bottom: 0.5rem;
                }

                .bounty-meta {
                    display: flex;
                    gap: 1rem;
                    align-items: center;
                }

                .bounty-id {
                    font-size: 0.75rem;
                    color: #6b7280;
                    font-family: monospace;
                }

                .status-badge {
                    padding: 0.25rem 0.75rem;
                    border-radius: 9999px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }

                .status-open {
                    background: #d1fae5;
                    color: #065f46;
                }

                .status-claimed {
                    background: #dbeafe;
                    color: #1e40af;
                }

                .bounty-reward {
                    display: flex;
                    flex-direction: column;
                    align-items: flex-end;
                    padding-left: 2rem;
                }

                .reward-label {
                    font-size: 0.75rem;
                    color: #6b7280;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }

                .reward-value {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #059669;
                }

                .empty-state {
                    text-align: center;
                    padding: 4rem 2rem;
                    background: #f9fafb;
                    border-radius: 12px;
                }

                .empty-icon {
                    font-size: 4rem;
                    margin-bottom: 1rem;
                }

                .empty-state h3 {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: #374151;
                    margin-bottom: 0.5rem;
                }

                .empty-state p {
                    color: #6b7280;
                }
            `}</style>
        </div>
    );
}
