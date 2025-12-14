
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { getGovernanceService } from '@/lib/governance/service';
import { GovernanceProposal } from '@/lib/governance/types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Vote, FileText, CheckCircle2, XCircle } from 'lucide-react';

export default function GovernanceInterface() {
    const { did } = useAuth();
    const [proposals, setProposals] = useState<GovernanceProposal[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const service = getGovernanceService();

    useEffect(() => {
        loadProposals();
    }, []);

    const loadProposals = () => {
        setIsLoading(true);
        // Simulate network delay
        setTimeout(() => {
            setProposals(service.getAllProposals());
            setIsLoading(false);
        }, 500);
    };

    const handleVote = async (proposalId: string, choice: 'yes' | 'no' | 'abstain') => {
        if (!did) return;
        await service.castVote(did, proposalId, choice);
        loadProposals(); // Refresh to show updated counts (optimistic)
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Protocol Governance</h2>
                    <p className="text-muted-foreground">Vote on parameter updates and policy changes.</p>
                </div>
                <Button>
                    <FileText className="mr-2 h-4 w-4" />
                    New Proposal
                </Button>
            </div>

            <Tabs defaultValue="active" className="w-full">
                <TabsList>
                    <TabsTrigger value="active">Active</TabsTrigger>
                    <TabsTrigger value="passed">Passed</TabsTrigger>
                    <TabsTrigger value="rejected">Rejected</TabsTrigger>
                </TabsList>

                <TabsContent value="active" className="space-y-4 mt-4">
                    {isLoading ? (
                        <div>Loading proposals...</div>
                    ) : proposals.filter(p => p.status === 'active').length === 0 ? (
                        <div className="text-center py-10 text-muted-foreground">No active proposals</div>
                    ) : (
                        proposals.filter(p => p.status === 'active').map(proposal => (
                            <ProposalCard key={proposal.id} proposal={proposal} onVote={handleVote} did={did} />
                        ))
                    )}
                </TabsContent>

                <TabsContent value="passed" className="mt-4">
                    {proposals.filter(p => p.status === 'passed' || p.status === 'executed').map(proposal => (
                        <ProposalCard key={proposal.id} proposal={proposal} onVote={handleVote} did={did} readonly />
                    ))}
                </TabsContent>
            </Tabs>
        </div>
    );
}

function ProposalCard({
    proposal,
    onVote,
    did,
    readonly = false
}: {
    proposal: GovernanceProposal;
    onVote: (id: string, choice: 'yes' | 'no' | 'abstain') => void;
    did: string | null;
    readonly?: boolean;
}) {
    const totalVotes = proposal.voteCount.yes + proposal.voteCount.no + proposal.voteCount.abstain;
    const yesPercent = totalVotes > 0 ? (proposal.voteCount.yes / totalVotes) * 100 : 0;

    return (
        <Card>
            <CardHeader>
                <div className="flex justify-between items-start">
                    <div>
                        <CardTitle className="text-lg">{proposal.title}</CardTitle>
                        <CardDescription className="mt-1">
                            ID: {proposal.id.slice(0, 12)}... • Proposer: {proposal.proposerDID.slice(0, 16)}...
                        </CardDescription>
                    </div>
                    <Badge variant={proposal.status === 'active' ? 'default' : 'secondary'}>
                        {proposal.status.toUpperCase()}
                    </Badge>
                </div>
            </CardHeader>
            <CardContent className="space-y-4">
                <p className="text-sm">{proposal.description}</p>

                {proposal.proposedChanges && (
                    <div className="bg-muted p-3 rounded-md text-sm font-mono">
                        {Object.entries(proposal.proposedChanges).map(([key, val]) => (
                            <div key={key} className="flex justify-between">
                                <span className="text-muted-foreground">{key}:</span>
                                <span>{val?.toString()}</span>
                            </div>
                        ))}
                    </div>
                )}

                <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                        <span>Current Votes ({totalVotes})</span>
                        <span>{yesPercent.toFixed(1)}% Yes</span>
                    </div>
                    <Progress value={yesPercent} className="h-2" />
                </div>
            </CardContent>
            {!readonly && (
                <CardFooter className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => onVote(proposal.id, 'no')} disabled={!did}>
                        <XCircle className="mr-2 h-4 w-4 text-red-500" />
                        Reject
                    </Button>
                    <Button onClick={() => onVote(proposal.id, 'yes')} disabled={!did}>
                        <CheckCircle2 className="mr-2 h-4 w-4" />
                        Approve
                    </Button>
                </CardFooter>
            )}
        </Card>
    );
}
