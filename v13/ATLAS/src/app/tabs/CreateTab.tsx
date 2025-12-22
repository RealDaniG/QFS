'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PlusCircle } from 'lucide-react'
import { useQFSFeed } from '@/hooks/useQFSFeed'
import { Button } from '@/components/ui/button'

import ContentComposer from '@/components/ContentComposer'

export function CreateTab() {
    const [isComposerOpen, setIsComposerOpen] = useState(false)
    return (
        <div className="max-w-2xl mx-auto">
            <Card>
                <CardHeader>
                    <CardTitle>Create Content</CardTitle>
                    <CardDescription>
                        Every action is transparent and economically accountable.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8">
                        <Button size="lg" onClick={() => setIsComposerOpen(true)}>
                            <PlusCircle className="h-5 w-5 mr-2" />
                            Open Content Composer
                        </Button>
                        <p className="text-muted-foreground mt-4">
                            Create posts, images, videos, polls with full economic transparency.
                        </p>
                    </div>
                    {/* Note: ContentComposer modal is handled in page.tsx normally, 
              but we can put a trigger here. */}
                </CardContent>
            </Card>
            <ContentComposer isOpen={isComposerOpen} onClose={() => setIsComposerOpen(false)} />
        </div>
    )
}
