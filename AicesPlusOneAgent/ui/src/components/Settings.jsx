import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useOrganization, useAuth, useUser } from "@clerk/clerk-react";
import { Server, Settings as SettingsIcon, Shield, Code, Terminal, Copy, Check } from 'lucide-react';

export default function Settings() {
    const { organization, isLoaded: orgLoaded } = useOrganization();
    const { user } = useUser();
    const { getToken } = useAuth();

    // Tenant ID logic: Org ID or fallback to User ID (Personal)
    const tenantId = organization?.id || user?.id;

    const [config, setConfig] = useState({
        url: '',
        use_mtls: false,
        whitelisted_ips: []
    });
    const [newTokenDesc, setNewTokenDesc] = useState('');
    const [createdToken, setCreatedToken] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [copied, setCopied] = useState(false);

    // Configure Axios Interceptor for Auth
    useEffect(() => {
        const interceptor = axios.interceptors.request.use(async (config) => {
            const token = await getToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });
        return () => axios.interceptors.request.eject(interceptor);
    }, [getToken]);

    useEffect(() => {
        if (tenantId) {
            fetchConfig();
        }
    }, [tenantId]);

    const fetchConfig = async () => {
        try {
            const res = await axios.get(`/api/tenants/${tenantId}`);
            if (res.data?.analyzer_config) {
                setConfig(res.data.analyzer_config);
            }
        } catch (err) {
            console.error("Failed to load tenant config", err);
        }
    };

    const handleSaveConfig = async () => {
        setLoading(true);
        setMessage(null);
        try {
            await axios.put(`/api/tenants/${tenantId}/config`, {
                url: config.url,
                use_mtls: config.use_mtls
            });
            setMessage({ type: 'success', text: 'Configuration saved successfully.' });
        } catch (err) {
            setMessage({ type: 'error', text: 'Failed to save configuration.' });
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateToken = async () => {
        if (!newTokenDesc) return;
        setLoading(true);
        setCreatedToken(null);
        try {
            const res = await axios.post(`/api/tenants/${tenantId}/tokens`, {
                description: newTokenDesc
            });
            setCreatedToken(res.data.token);
            setNewTokenDesc('');
        } catch (err) {
            setMessage({ type: 'error', text: 'Failed to generate token.' });
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!orgLoaded) return <div className="p-8 text-slate-500">Loading...</div>;
    if (!tenantId) return <div className="p-8 text-slate-500">Please select an Organization or sign in.</div>;

    const sampleDockerCompose = `services:
  analyzer:
    image: ghcr.io/milad665/aices-plus-one-analyzer:latest
    container_name: aices-analyzer
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data              # Persist analyzer data
    environment:
      - API_HOST=0.0.0.0
      # Option 1: Map repositories via JSON
      - GIT_REPOSITORIES=[{"name":"main-repo","url":"git@github.com:org/repo.git","default_branch":"main"}]
      # SSH Key for private repos (paste content or path)
      - GIT_SSH_KEY="-----BEGIN OPENSSH PRIVATE KEY-----..."
      # OR mount key file and use:
      # - GIT_SSH_KEY_PATH=/data/id_rsa`;

    return (
        <div className="p-8 max-w-5xl mx-auto space-y-8 h-full overflow-y-auto bg-[#F8FAFC]">
            <header>
                <h1 className="text-3xl font-bold text-slate-900 mb-2">Tenant Settings</h1>
                <p className="text-slate-500">Configure your Code Analyzer connection and manage access tokens.</p>
            </header>

            {message && (
                <div className={`p-4 rounded-lg border ${message.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-red-50 border-red-200 text-red-700'}`}>
                    {message.text}
                </div>
            )}

            {/* Code Analyzer Setup Instructions */}
            <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                    <Server className="text-sky-600" />
                    Code Analyzer Setup
                </h2>

                <div className="prose prose-slate max-w-none text-slate-600 mb-8">
                    <p>
                        The <strong>Aices+1 Code Analyzer</strong> is a lightweight container that runs within your infrastructure.
                        It scans your local repositories and securely transmits architectural metadata to the Aices+1 Agent.
                        Your source code never leaves your network.
                    </p>

                    {/* Mermaid Diagram Logic via Image or Description */}
                    <div className="my-6 p-4 bg-slate-50 rounded-lg border border-slate-200 flex justify-center">
                        {/* Simple visual representation if mermaid not available directly */}
                        <div className="flex items-center gap-4 text-sm font-semibold text-slate-700">
                            <div className="p-4 bg-white border border-slate-200 rounded shadow-sm text-center">
                                <span className="block text-sky-600 mb-1">Your Infrastructure</span>
                                <div className="p-2 bg-slate-100 rounded border border-slate-200">
                                    Code Analyzer Container
                                </div>
                            </div>
                            <div className="h-0.5 w-12 bg-slate-300"></div>
                            <div className="p-4 bg-indigo-50 border border-indigo-100 rounded shadow-sm text-center">
                                <span className="block text-indigo-600 mb-1">Aices+1 Cloud</span>
                                <div className="p-2 bg-white rounded border border-indigo-100">
                                    Agent & Knowledge Graph
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div>
                        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2">
                            <Terminal size={16} /> 1. Docker Compose Setup
                        </h3>
                        <p className="text-sm text-slate-500 mb-3">Create a <code>docker-compose.yml</code> file in your infrastructure:</p>
                        <div className="relative group">
                            <pre className="bg-slate-900 text-slate-50 p-4 rounded-lg text-sm overflow-x-auto font-mono">
                                {sampleDockerCompose}
                            </pre>
                            <button
                                onClick={() => copyToClipboard(sampleDockerCompose)}
                                className="absolute top-2 right-2 p-2 bg-white/10 hover:bg-white/20 rounded text-white transition-opacity opacity-0 group-hover:opacity-100"
                            >
                                {copied ? <Check size={16} /> : <Copy size={16} />}
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Connection Configuration */}
            <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <SettingsIcon className="text-slate-600" />
                    Connection Settings
                </h2>
                <div className="space-y-4 max-w-xl">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Analyzer Public URL</label>
                        <input
                            type="text"
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all"
                            placeholder="https://analyzer.your-company.com"
                            value={config.url}
                            onChange={(e) => setConfig({ ...config, url: e.target.value })}
                        />
                        <p className="text-xs text-slate-400 mt-1">The URL where the Aices+1 Agent can reach your analyzer.</p>
                    </div>

                    <div className="flex items-center gap-3 py-2">
                        <input
                            type="checkbox"
                            id="mtls"
                            className="w-4 h-4 text-sky-600 rounded border-slate-300 focus:ring-sky-500"
                            checked={config.use_mtls}
                            onChange={(e) => setConfig({ ...config, use_mtls: e.target.checked })}
                        />
                        <label htmlFor="mtls" className="text-sm font-medium text-slate-700">Enable mTLS Security</label>
                    </div>

                    <button
                        onClick={handleSaveConfig}
                        disabled={loading}
                        className="px-6 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg font-medium transition-colors shadow-sm shadow-sky-500/20"
                    >
                        {loading ? 'Saving...' : 'Save Configuration'}
                    </button>
                </div>
            </section>

            {/* Certificates Section (Stub) */}
            <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm opacity-60">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                        <Shield className="text-slate-600" />
                        mTLS Certificates
                    </h2>
                    <span className="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded border border-amber-200">COMING SOON</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {['Client Certificate (.crt)', 'Client Key (.key)', 'CA Certificate (.crt)'].map((label) => (
                        <div key={label}>
                            <label className="block text-sm font-medium text-slate-700 mb-2">{label}</label>
                            <div className="h-10 bg-slate-50 border border-slate-200 rounded-lg border-dashed flex items-center px-4 text-slate-400 text-sm">
                                Upload file...
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Service Tokens Section */}
            <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <Code className="text-slate-600" />
                    Service Tokens
                </h2>
                <p className="text-sm text-slate-500 mb-4">Generate tokens to authenticate MCP tools and external integrations.</p>

                <div className="flex gap-4 mb-6">
                    <input
                        type="text"
                        placeholder="Token Description (e.g. CI/CD Pipeline)"
                        className="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 outline-none transition-all"
                        value={newTokenDesc}
                        onChange={(e) => setNewTokenDesc(e.target.value)}
                    />
                    <button
                        onClick={handleGenerateToken}
                        disabled={loading}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium whitespace-nowrap transition-colors shadow-sm shadow-indigo-500/20"
                    >
                        Generate Token
                    </button>
                </div>

                {createdToken && (
                    <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg mb-6">
                        <p className="text-emerald-800 text-sm mb-2 font-bold flex items-center gap-2">
                            <Check size={16} /> Token Generated Successfully
                        </p>
                        <div className="flex items-center gap-2">
                            <code className="block flex-1 bg-white border border-emerald-100 p-3 rounded font-mono text-slate-700 break-all shadow-sm">
                                {createdToken}
                            </code>
                            <button
                                onClick={() => copyToClipboard(createdToken)}
                                className="p-3 bg-white border border-emerald-100 rounded text-emerald-600 hover:bg-emerald-50"
                            >
                                {copied ? <Check size={18} /> : <Copy size={18} />}
                            </button>
                        </div>
                        <p className="text-xs text-emerald-600 mt-2">Make sure to copy this token now. You won't be able to see it again.</p>
                    </div>
                )}
            </section>
        </div>
    );
}
