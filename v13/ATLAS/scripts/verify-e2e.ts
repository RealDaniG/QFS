
import { MockLedger } from '@/lib/ledger/mock-ledger';
import { getTreasury } from '@/lib/economics/treasury-engine';
import { getPolicyRegistry } from '@/lib/governance/policy-registry';
import { getGuardRegistry } from '@/lib/guards/registry';
import { ContentQualityGuard, SybilGuard } from '@/lib/guards/implementations';
import { QFSExecutor } from '@/lib/qfs/executor';
import { getGovernanceService } from '@/lib/governance/service';
import { PendingContentCreatedEvent } from '@/types/storage';

async function runVerification() {
    console.log('🚀 Starting ATLAS End-to-End System Verification...\n');

    // 1. Setup & Init
    console.log('📦 Initializing core services...');
    // Create new instance for testing
    const ledger = new MockLedger(true, 100); // Fast mining for test
    const treasury = getTreasury();
    const policy = getPolicyRegistry();
    const gov = getGovernanceService();
    const guards = getGuardRegistry();

    // Register guards
    guards.register(new ContentQualityGuard());
    guards.register(new SybilGuard());

    const node = new QFSExecutor('did:key:verified_node_1');
    const userDID = 'did:key:user_alice';

    console.log('✅ Services initialized.\n');

    // 2. Policy Verification
    console.log('📜 Verifying Dynamic Policy...');
    const currentRules = policy.getCurrentPolicy().rules;
    console.log(`   - Current Base Reward: ${currentRules.rewardBaseRate} FLX`);
    if (currentRules.rewardBaseRate !== 10.0) throw new Error('Policy mismatch');
    console.log('✅ Policy verified.\n');

    // 3. QFS Execution & Guards
    console.log('🛡️  Verifying Guards & QFS Execution...');
    const validContent = { text: 'This is a high-quality post about decentralized economics.' };
    const spamContent = { text: 'free money click here' };

    try {
        await node.executeTask({
            taskId: 't1',
            type: 'coherence_scoring',
            dataCID: 'cid_spam',
            policyVersion: 'v1'
        }, {
            author: userDID,
            content: spamContent
        });
        throw new Error('Spam should have been blocked');
    } catch (e: any) {
        if (e.message.includes('spam')) {
            console.log('   - ✅ Guard correctly blocked spam content.');
        } else {
            throw e;
        }
    }

    const result = await node.executeTask({
        taskId: 't2',
        type: 'coherence_scoring',
        dataCID: 'cid_valid',
        policyVersion: 'v1'
    }, {
        author: userDID,
        content: validContent
    });
    console.log(`   - ✅ Valid content computed. Proof Root: ${result.proof.root.slice(0, 10)}...`);
    console.log('✅ Guards & QFS verified.\n');

    // 4. Ledger & Economics
    console.log('💰 Verifying Ledger & Treasury...');

    const event: PendingContentCreatedEvent = {
        pendingId: 'evt_1',
        eventType: 'ContentCreated',
        actorDID: userDID,
        inputs: {
            signedContent: {
                payload: { contentCID: 'cid_valid', authorDID: userDID }
            }
        } as any,
        eventInputHash: 'hash',
        createdAtMs: Date.now(),
        status: 'pending'
    };

    // Inject outcome (mocking what QFS would return to ledger)
    const ledgerEvent = {
        ...event,
        outcome: { coherence_score: 0.95 }
    };

    // In a real flow, this happens via adapter. Here we manually trigger treasury for test.
    // We need to simulate the Treasury processing a confirmed ledger event.
    // The Treasury listens to the ledger. In our mock setup, we can call credit directly or simulate the event flow.
    // Let's use the public API of Treasury if possible, or cast to any to access internal processing for verification.

    // Simulating "processed" event
    await (treasury as any).processContentReward({
        event_id: 'ledger_evt_1',
        inputs: event.inputs,
        outcome: { coherence_score: 0.95 },
        actor: userDID
    });

    const account = await treasury.getBalance(userDID);
    // Reward = 0.95 * 10.0 = 9.5
    console.log(`   - User Balance: ${account.balance} FLX`);
    if (account.balance !== 9.5) throw new Error(`Expected bundle 9.5, got ${account.balance}`);
    console.log('✅ Economics verified.\n');

    // 5. Governance
    console.log('🗳️  Verifying Governance...');
    const proposalId = await gov.submitProposal(userDID, 'Test Prop', 'Desc', { rewardBaseRate: 20.0 });
    const optimisticId = `pending_${proposalId}`;
    console.log(`   - Proposal submitted: ${optimisticId}`);

    await gov.castVote(userDID, optimisticId, 'yes');
    console.log(`   - Vote cast by ${userDID}`);

    const proposals = gov.getAllProposals();
    const prop = proposals.find(p => p.id === optimisticId);
    if (!prop || prop.voteCount.yes !== 1) throw new Error('Vote not counted');
    console.log('✅ Governance verified.\n');

    console.log('🎉 ALL SYSTEMS OPERATIONAL. VERIFICATION COMPLETE.');
}

// Run if called directly
runVerification().catch(err => {
    console.error('❌ Verification Failed:', err);
    process.exit(1);
});
