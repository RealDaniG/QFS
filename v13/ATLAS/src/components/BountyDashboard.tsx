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
    const { isConnected, address } = useWalletAuth();
    const [activeTab, setActiveTab] = useState<Tab>('all');

    if (!isConnected) {
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
            </div>

            <div className="tab-content">
                {activeTab === 'all' ? <BountyList /> : <MyBounties />}
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
