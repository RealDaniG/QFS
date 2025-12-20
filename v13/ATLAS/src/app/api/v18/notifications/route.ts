import { NextResponse } from 'next/server';

/**
 * Notifications API
 * Returns user notifications
 */

interface Notification {
    id: string;
    type: 'reward' | 'security' | 'system' | 'mention';
    title: string;
    message: string;
    timestamp: number;
    read: boolean;
    data?: any;
}

// Mock database - replace with real database later
const mockNotifications: Notification[] = [
    {
        id: '1',
        type: 'reward',
        title: 'Reward Distributed',
        message: 'You received 12.50 FLX for your last post "Deterministic QFS...".',
        timestamp: Date.now() - 1000 * 60 * 5,
        read: false,
        data: { amount: 12.5, currency: 'FLX' }
    },
    {
        id: '2',
        type: 'security',
        title: 'Session Sealed',
        message: 'Your current v18 session has been successfully sealed with ASCON-128.',
        timestamp: Date.now() - 1000 * 60 * 30,
        read: true
    },
    {
        id: '3',
        type: 'system',
        title: 'Coherence Ranking Updated',
        message: 'Network-wide coherence ranking epoch #14 has been finalized.',
        timestamp: Date.now() - 1000 * 60 * 60 * 2,
        read: true
    },
    {
        id: '4',
        type: 'mention',
        title: 'New Mention',
        message: '@alice mentioned you in "QFS Economics Discussion"',
        timestamp: Date.now() - 1000 * 60 * 60 * 4,
        read: false
    }
];

export async function GET(request: Request) {
    // TODO: Get user from session
    // const session = await getSession(request);

    // TODO: Fetch from real database
    // const notifications = await db.notifications.findMany({
    //   where: { userId: session.wallet_address },
    //   orderBy: { timestamp: 'desc' }
    // });

    return NextResponse.json(mockNotifications);
}

export async function POST(request: Request) {
    try {
        const { notificationIds, action } = await request.json();

        if (action === 'markRead') {
            // TODO: Update in real database
            // await db.notifications.updateMany({
            //   where: { id: { in: notificationIds } },
            //   data: { read: true }
            // });

            // For now, just return success
            return NextResponse.json({ success: true, marked: notificationIds.length });
        }

        return NextResponse.json({ success: false, error: 'Invalid action' }, { status: 400 });

    } catch (error) {
        console.error('Notifications API error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to update notifications' },
            { status: 500 }
        );
    }
}
