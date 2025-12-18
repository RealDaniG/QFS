
import { TreasuryEngine } from '../src/lib/economics/treasury-engine';
import { LedgerEvent } from '../src/types/storage';

async function runTests() {
    console.log('Starting TreasuryEngine Verification...');

    const treasury = new TreasuryEngine();
    const aliceDID = 'did:key:alice';
    const bobDID = 'did:key:bob';

    // Test 1: Content Reward
    console.log('Test 1: Content Creation Reward');
    const contentEvent: LedgerEvent = {
        event_id: 'evt_1',
        event_type: 'ContentCreated',
        timestamp: Date.now(),
        sequence_number: 1,
        actor: aliceDID,
        modules: ['Content'],
        inputs: { contentType: 'post' },
        outcome: { coherence_score: 0.8 },
        policy_version: '1',
        previous_event_hash: '0',
        event_hash: 'h1',
        signature: 's1',
        signer_did: 'node1'
    };

    treasury.processLedgerEvent(contentEvent);

    const aliceBalance = treasury.getBalance(aliceDID);
    // Base 10.0 * 0.8 = 8.0 FLX
    console.assert(aliceBalance.balance === 8.0, `Expected 8.0, got ${aliceBalance.balance}`);
    console.log(aliceBalance.balance === 8.0 ? 'PASS' : 'FAIL');

    // Test 2: Interaction Reward
    console.log('Test 2: Interaction (Like) Reward');
    const likeEvent: LedgerEvent = {
        event_id: 'evt_2',
        event_type: 'InteractionCreated',
        timestamp: Date.now(),
        sequence_number: 2,
        actor: bobDID,
        modules: ['Interaction'],
        inputs: { interactionType: 'like', target: 'post_1' },
        outcome: { status: 'confirmed' },
        policy_version: '1',
        previous_event_hash: 'h1',
        event_hash: 'h2',
        signature: 's2',
        signer_did: 'node1'
    };

    treasury.processLedgerEvent(likeEvent);
    const bobBalance = treasury.getBalance(bobDID);
    // Like reward = 0.1
    console.assert(bobBalance.balance === 0.1, `Expected 0.1, got ${bobBalance.balance}`);
    console.log(bobBalance.balance === 0.1 ? 'PASS' : 'FAIL');

    // Test 3: Idempotency (Replay Attack Protection)
    console.log('Test 3: Idempotency');
    treasury.processLedgerEvent(contentEvent); // Replay evt_1
    const aliceBalance2 = treasury.getBalance(aliceDID);
    console.assert(aliceBalance2.balance === 8.0, `Expected 8.0 (unchanged), got ${aliceBalance2.balance}`);
    console.log(aliceBalance2.balance === 8.0 ? 'PASS' : 'FAIL');

    // Test 4: Transaction History
    console.log('Test 4: Transaction History');
    const history = treasury.getHistory(aliceDID);
    console.assert(history.length === 1, `Expected 1 transaction, got ${history.length}`);
    console.log(history.length === 1 ? 'PASS' : 'FAIL');

    console.log('Verification Complete.');
}

runTests().catch(console.error);
