import { NextResponse } from 'next/server';

/**
 * Mock Nonce Endpoint
 * Returns a nonce for wallet signature
 */
export async function GET() {
    const nonce = `atlas_nonce_${Date.now()}_${Math.random().toString(36).substring(7)}`;

    return NextResponse.json({
        nonce,
        timestamp: Date.now()
    });
}
