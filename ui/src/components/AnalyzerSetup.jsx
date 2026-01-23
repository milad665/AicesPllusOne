import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Terminal, Copy } from 'lucide-react';

const AnalyzerSetup = () => {
    const codeSnippet = `docker run -d \\
  --name aices-analyzer \\
  -p 8000:8000 \\
  -v $(pwd)/data:/data \\
  -e API_HOST=0.0.0.0 \\
  -e API_PORT=8000 \\
  ghcr.io/milad665/aices-plus-one-analyzer:latest`;

    const copyToClipboard = () => {
        navigator.clipboard.writeText(codeSnippet);
    };

    return (
        <div className="p-6 max-w-4xl mx-auto space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight">Code Analyzer Setup</h1>
            </div>

            <Alert>
                <Terminal className="h-4 w-4" />
                <AlertTitle>Hybrid Deployment</AlertTitle>
                <AlertDescription>
                    The Code Analyzer runs on your infrastructure. This ensures your source code never leaves your network.
                </AlertDescription>
            </Alert>

            <Card>
                <CardHeader>
                    <CardTitle>1. Pull & Run Container</CardTitle>
                    <CardDescription>
                        Execute the following command on your server (Docker required).
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="relative rounded-md bg-stone-950 p-4">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="absolute right-2 top-2 text-stone-400 hover:text-white"
                            onClick={copyToClipboard}
                        >
                            <Copy className="h-4 w-4" />
                        </Button>
                        <pre className="overflow-x-auto text-sm text-stone-50 font-mono">
                            <code>{codeSnippet}</code>
                        </pre>
                    </div>

                    <div className="space-y-2 text-sm text-muted-foreground">
                        <p><strong>Environment Variables:</strong></p>
                        <ul className="list-disc pl-5 space-y-1">
                            <li><code>API_HOST</code>: Host to bind (0.0.0.0 for container)</li>
                            <li><code>API_PORT</code>: Port (default 8000)</li>
                            <li><code>SSH_KEYS_DIR</code>: Directory to mount SSH keys (if needed)</li>
                        </ul>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>2. Network Configuration</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                        Ensure that your firewall allows inbound traffic on port <strong>8000</strong> from the AicesPlusOne Agent IP addresses.
                    </p>
                    {/* Placeholder for whitelisted IPs if available via API */}
                </CardContent>
            </Card>
        </div>
    );
};

export default AnalyzerSetup;
