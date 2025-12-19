/**
 * BountyList Component
 * Displays available bounties with wallet authentication.
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

export function BountyList() {
    const { isConnected, sessionToken, address } = useWalletAuth();
    const [bounties, setBounties] = useState<Bounty[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [claiming, setClaiming] = useState<string | null>(null);

    useEffect(() => {
        if (isConnected && sessionToken) {
            fetchBounties();
        }
    }, [isConnected, sessionToken]);

    const fetchBounties = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('/api/bounties/', {
                headers: {
                    'Authorization': `Bearer ${sessionToken}`
                }
            });

            if (!res.ok) {
                if (res.status === 403) {
                    throw new Error('Missing scope: bounty:read');
                }
                throw new Error('Failed to fetch bounties');
            }

            const data = await res.json();
            setBounties(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleClaim = async (bountyId: string) => {
        setClaiming(bountyId);
        setError(null);
        try {
            const res = await fetch(`/api/bounties/${bountyId}/claim`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${sessionToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!res.ok) {
                if (res.status === 403) {
                    throw new Error('Missing scope: bounty:claim');
                }
                const errData = await res.json();
                throw new Error(errData.detail || 'Failed to claim bounty');
            }

            const result = await res.json();
            alert(`Success: ${result.message}`);

            // Refresh bounties
            await fetchBounties();
        } catch (err: any) {
            setError(err.message);
        } finally {
            setClaiming(null);
        }
    };

    if (!isConnected) {
        return (
            <div className="bounty-list-container">
                <div className="auth-required">
                    <h3>🔒 Authentication Required</h3>
                    <p>Please connect your wallet to view bounties.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bounty-list-container">
            <div className="bounty-list-header">
                <h2>Available Bounties</h2>
                <button onClick={fetchBounties} disabled={loading}>
                    {loading ? 'Loading...' : '🔄 Refresh'}
                </button>
            </div>

            {error && (
                <div className="error-message">
                    ⚠️ {error}
                </div>
            )}

            {loading && bounties.length === 0 ? (
                <div className="loading-state">Loading bounties...</div>
            ) : (
                <div className="bounty-grid">
                    {bounties.map((bounty) => (
                        <div key={bounty.id} className="bounty-card">
                            <div className="bounty-header">
                                <h3>{bounty.title}</h3>
                                <span className={`status-badge status-${bounty.status.toLowerCase()}`}>
                                    {bounty.status}
                                </span>
                            </div>

                            <div className="bounty-details">
                                <div className="reward">
                                    <span className="label">Reward:</span>
                                    <span className="value">{bounty.reward} CHR</span>
                                </div>

                                {bounty.claimant && (
                                    <div className="claimant">
                                        <span className="label">Claimed by:</span>
                                        <span className="value">{bounty.claimant}</span>
                                    </div>
                                )}
                            </div>

                            <div className="bounty-actions">
                                {bounty.status === 'OPEN' && (
                                    <button
                                        onClick={() => handleClaim(bounty.id)}
                                        disabled={claiming === bounty.id}
                                        className="claim-button"
                                    >
                                        {claiming === bounty.id ? 'Claiming...' : '🎯 Claim Bounty'}
                                    </button>
                                )}
                                {bounty.status === 'CLAIMED' && bounty.claimant === address && (
                                    <div className="claimed-by-you">
                                        ✅ Claimed by you
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {!loading && bounties.length === 0 && (
                <div className="empty-state">
                    <p>No bounties available at the moment.</p>
                </div>
            )}

            <style jsx>{`
                .bounty-list-container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }

                .bounty-list-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
                }

                .bounty-list-header h2 {
                    font-size: 2rem;
                    font-weight: 700;
                    color: #1a1a1a;
                }

                .bounty-list-header button {
                    padding: 0.75rem 1.5rem;
                    background: #4f46e5;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: background 0.2s;
                }

                .bounty-list-header button:hover:not(:disabled) {
                    background: #4338ca;
                }

                .bounty-list-header button:disabled {
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

                .loading-state, .empty-state {
                    text-align: center;
                    padding: 3rem;
                    color: #6b7280;
                }

                .bounty-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                    gap: 1.5rem;
                }

                .bounty-card {
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 1.5rem;
                    transition: box-shadow 0.2s, transform 0.2s;
                }

                .bounty-card:hover {
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    transform: translateY(-2px);
                }

                .bounty-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: start;
                    margin-bottom: 1rem;
                }

                .bounty-header h3 {
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: #111827;
                    flex: 1;
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

                .bounty-details {
                    margin-bottom: 1.5rem;
                }

                .bounty-details > div {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 0.5rem;
                }

                .label {
                    color: #6b7280;
                    font-size: 0.875rem;
                }

                .value {
                    color: #111827;
                    font-weight: 600;
                }

                .reward .value {
                    color: #059669;
                    font-size: 1.125rem;
                }

                .claimant .value {
                    font-family: monospace;
                    font-size: 0.75rem;
                }

                .bounty-actions {
                    margin-top: 1rem;
                }

                .claim-button {
                    width: 100%;
                    padding: 0.75rem;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 0.2s, box-shadow 0.2s;
                }

                .claim-button:hover:not(:disabled) {
                    transform: scale(1.02);
                    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
                }

                .claim-button:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }

                .claimed-by-you {
                    text-align: center;
                    padding: 0.75rem;
                    background: #d1fae5;
                    color: #065f46;
                    border-radius: 8px;
                    font-weight: 600;
                }
            `}</style>
        </div>
    );
}
