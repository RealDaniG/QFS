import { NextResponse } from 'next/server';

/**
 * Mock Verify Endpoint
 * Accepts any signature and creates a mock session
 * TODO: Replace with real backend verification
 */
export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { nonce, signature, wallet_address } = body;

        if (!nonce || !signature || !wallet_address) {
            return NextResponse.json(
                { detail: 'Missing required fields' },
                { status: 400 }
            );
        }

        // Mock session token with ASCON prefix for v18 compliance
        const sessionToken = `ascon1.mock_${Date.now()}_${Math.random().toString(36).substring(7)}`;
        const expiresAt = Math.floor(Date.now() / 1000) + 86400; // 24 hours from now

        return NextResponse.json({
            session_token: sessionToken,
            wallet_address: wallet_address,
            expires_at: expiresAt,
            message: 'Mock authentication successful - replace with real backend'
        });

    } catch (error) {
        console.error('Auth verify error:', error);
        return NextResponse.json(
            { detail: 'Authentication failed' },
            { status: 500 }
        );
    }
}
