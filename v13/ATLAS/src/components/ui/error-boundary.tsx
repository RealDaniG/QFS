"use client";

import React, { ErrorInfo, ReactNode } from "react";
import { AlertCircle, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
    children?: ReactNode;
    fallback?: ReactNode;
    name?: string;
}

interface State {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
    public state: State = {
        hasError: false
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error(`Error in ${this.props.name || 'Component'}:`, error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <Card className="border-destructive/50 bg-destructive/5 my-4">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-destructive">
                            <AlertCircle className="h-5 w-5" />
                            Something went wrong
                        </CardTitle>
                        <CardDescription>
                            The {this.props.name || 'component'} failed to load properly.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm font-mono bg-destructive/10 p-2 rounded overflow-auto max-h-32">
                            {this.state.error?.message}
                        </p>
                    </CardContent>
                    <CardFooter>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => this.setState({ hasError: false })}
                            className="gap-2"
                        >
                            <RefreshCcw className="h-4 w-4" />
                            Try again
                        </Button>
                    </CardFooter>
                </Card>
            );
        }

        return this.props.children;
    }
}
