'use client';

import { useState, FormEvent } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useProfileUpdate } from '@/hooks/useProfileUpdate';
import { useAuth } from '@/hooks/useAuth';

export default function ProfileEditor() {
    const { did } = useAuth();
    const { updateProfile, isUpdating } = useProfileUpdate();

    const [name, setName] = useState('');
    const [bio, setBio] = useState('');
    const [avatar, setAvatar] = useState('');

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!did) return;

        const pendingId = await updateProfile({
            name: name || undefined,
            bio: bio || undefined,
            avatar: avatar || undefined
        });

        // Reset or show success
        alert(`Profile update submitted to local pending store! (ID: ${pendingId})`);
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Edit Profile</CardTitle>
                <CardDescription>
                    Updates are recorded on the public ledger for transparency.
                    DID: {did ? `${did.slice(0, 16)}...` : 'Not connected'}
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="name">Display Name</Label>
                        <Input
                            id="name"
                            placeholder="Enter your public name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="bio">Bio</Label>
                        <Textarea
                            id="bio"
                            placeholder="Tell the network about yourself"
                            value={bio}
                            onChange={(e) => setBio(e.target.value)}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="avatar">Avatar CID / URL</Label>
                        <Input
                            id="avatar"
                            placeholder="ipfs://... or https://..."
                            value={avatar}
                            onChange={(e) => setAvatar(e.target.value)}
                        />
                    </div>

                    <Button type="submit" disabled={isUpdating}>
                        {isUpdating ? 'Submitting...' : 'Update Profile'}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
}
