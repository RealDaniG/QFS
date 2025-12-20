import React, { useState, useEffect } from 'react';

// Types derived from Spec
interface ExplanationData {
    summary: string;
    breakdown: {
        base_reward: Record<string, any>;
        bonuses: Array<{ label: string, value: string }>;
        caps: Array<{ label: string, value: string }>;
        total_reward: Record<string, any>;
    };
    policy_info: {
        version: string;
        hash: string;
    };
    verification: {
        hash: string;
        consistent: boolean;
    };
}

interface ExplanationAuditPanelProps {
    explanationId?: string;
    explanationData?: ExplanationData; // Optional direct injection
}

export const ExplanationAuditPanel: React.FC<ExplanationAuditPanelProps> = ({
    explanationId,
    explanationData: initialData
}) => {
    const [data, setData] = useState<ExplanationData | null>(initialData || null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (explanationId && !initialData) {
            setLoading(true);
            // Fetch logic would go here
            // fetch(`/api/v1/audit/explanation/${explanationId}`)...
            setLoading(false);
            // Mock data for display verification
            setData({
                summary: "Received value-node reward of 50.0 ATR",
                breakdown: {
                    base_reward: { "ATR": "45.0 ATR" },
                    bonuses: [{ label: "Humor", value: "+5.0 ATR" }],
                    caps: [],
                    total_reward: { "ATR": "50.0 ATR" }
                },
                policy_info: {
                    version: "Humor:v1.0|Artistic:v1.0",
                    hash: "a1b2c3d4..."
                },
                verification: {
                    hash: "f9e8d7c6...",
                    consistent: true
                }
            });
        }
    }, [explanationId, initialData]);

    if (loading) return <div>Loading Explanation Audit...</div>;
    if (error) return <div>Error loading audit: {error}</div>;
    if (!data) return <div>No explanation data available.</div>;

    return (
        <div className="explanation-audit-panel p-4 border rounded shadow-sm bg-white">
            <h3 className="text-lg font-bold mb-4">Explanation Audit</h3>

            {/* Summary Card */}
            <div className="summary-card bg-blue-50 p-4 rounded mb-4">
                <div className="text-xl font-mono text-blue-800">{data.summary}</div>
                <div className="text-xs text-blue-500 mt-1">Hash: {data.verification.hash}</div>
            </div>

            {/* Waterfall Breakdown */}
            <div className="breakdown mb-6">
                <h4 className="font-semibold mb-2">Reward Breakdown</h4>
                <div className="space-y-2">
                    <div className="flex justify-between text-gray-600">
                        <span>Base Reward</span>
                        <span>{JSON.stringify(data.breakdown.base_reward)}</span>
                    </div>
                    {data.breakdown.bonuses.map((b, i) => (
                        <div key={i} className="flex justify-between text-green-600">
                            <span>+ {b.label}</span>
                            <span>{b.value}</span>
                        </div>
                    ))}
                    {data.breakdown.caps.map((c, i) => (
                        <div key={i} className="flex justify-between text-red-600">
                            <span>- {c.label}</span>
                            <span>{c.value}</span>
                        </div>
                    ))}
                    <div className="flex justify-between font-bold border-t pt-2 mt-2">
                        <span>Total</span>
                        <span>{JSON.stringify(data.breakdown.total_reward)}</span>
                    </div>
                </div>
            </div>

            {/* Policy Info */}
            <div className="policy-info text-sm text-gray-500 border-t pt-4">
                <div className="flex items-center gap-2">
                    <span className="font-semibold">Policy Context:</span>
                    <span className="bg-gray-200 px-2 py-1 rounded text-xs font-mono">{data.policy_info.version}</span>
                </div>
                <div className="mt-2 text-xs font-mono truncate">
                    Policy Hash: {data.policy_info.hash}
                </div>
            </div>

            {/* Verification Status */}
            <div className="mt-4">
                {data.verification.consistent ? (
                    <div className="bg-green-100 text-green-800 px-3 py-1 rounded text-center text-sm font-bold">
                        ✅ CRYPTOGRAPHICALLY VERIFIED
                    </div>
                ) : (
                    <div className="bg-red-100 text-red-800 px-3 py-1 rounded text-center text-sm font-bold">
                        ❌ VERIFICATION FAILED
                    </div>
                )}
            </div>
        </div>
    );
};
