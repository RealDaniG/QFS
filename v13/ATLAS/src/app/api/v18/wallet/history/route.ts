import { NextResponse } from 'next/server';

// v18 Rule: History must be deterministic and verifiable
export async function GET() {
    const history = [
        {
            id: 'tx_18_001',
            type: 'reward',
            reason: 'Coherence Contribution',
            amount: 50.00,
            timestamp: Date.now() - 3600000,
            ref: 'evt_1'
        },
        {
            id: 'tx_18_002',
            type: 'reward',
            reason: 'Distributed Computing Bonus',
            amount: 25.50,
            timestamp: Date.now() - 7200000,
            ref: 'evt_2'
        },
        {
            id: 'tx_18_003',
            type: 'reward',
            reason: 'Sentinel Governance Participation',
            amount: 100.00,
            timestamp: Date.now() - 86400000,
            ref: 'evt_3'
        }
    ];

    return NextResponse.json(history);
}
