import { NextResponse } from 'next/server';

// v18 Rule: Feed must be deterministic and support Ascon-signed verification
export async function GET() {
    const feedData = [
        {
            id: 'evt_1',
            type: 'announcement',
            author: 'ATLAS FOUNDATION',
            content: 'ATLAS v18 Alpha is now live on the distributed cluster. All nodes synchronized with Ascon-128 compliance.',
            timestamp: Date.now() - 3600000,
            reputation_score: 999,
            proof_hash: 'ascon.proof_8df3a1...'
        },
        {
            id: 'evt_2',
            type: 'market',
            author: 'Treasury Engine',
            content: 'Daily coherence reward of 1,000 FLX distributed to active v18 participants.',
            timestamp: Date.now() - 7200000,
            reputation_score: 142,
            proof_hash: 'ascon.proof_2e1c9b...'
        },
        {
            id: 'evt_3',
            type: 'security',
            author: 'AEGIS SENTINEL',
            content: 'New Distributed Compliance policy enforced: All v18 transactions require HSMF verification.',
            timestamp: Date.now() - 10800000,
            reputation_score: 500,
            proof_hash: 'ascon.proof_ff821a...'
        }
    ];

    return NextResponse.json(feedData);
}
