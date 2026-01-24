import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useOrganization, useAuth, useUser } from "@clerk/clerk-react";

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

    // Configure Axios Interceptor for Auth
    // Note: App.jsx / DashboardView might already set this, but good to be safe if this mounts independently
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

    if (!orgLoaded) return <div className="p-8 text-white">Loading...</div>;
    if (!tenantId) return <div className="p-8 text-white">Please select an Organization or sign in.</div>;

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-8 text-white overflow-y-auto h-full">
            <h1 className="text-3xl font-bold mb-4">Tenant Settings</h1>

            {message && (
                <div className={`p-4 rounded border ${message.type === 'success' ? 'bg-green-900/30 border-green-500' : 'bg-red-900/30 border-red-500'}`}>
                    {message.text}
                </div>
            )}

            <div className="bg-gray-800 p-4 rounded border border-gray-700">
                <p className="text-sm text-gray-400">Tenant ID: <span className="font-mono text-white">{tenantId}</span></p>
            </div>

            {/* Analyzer Config Section */}
            <section className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h2 className="text-xl font-semibold mb-4 text-blue-400">Code Analyzer Configuration</h2>
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">Analyzer URL</label>
                        <input
                            type="text"
                            className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="http://localhost:8000"
                            value={config.url}
                            onChange={(e) => setConfig({ ...config, url: e.target.value })}
                        />
                    </div>

                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            id="mtls"
                            className="w-4 h-4"
                            checked={config.use_mtls}
                            onChange={(e) => setConfig({ ...config, use_mtls: e.target.checked })}
                        />
                        <label htmlFor="mtls">Enable mTLS</label>
                    </div>

                    <div className="pt-2">
                        <button
                            onClick={handleSaveConfig}
                            disabled={loading}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-sm font-medium transition-colors"
                        >
                            {loading ? 'Saving...' : 'Save Configuration'}
                        </button>
                    </div>
                </div>
            </section>

            {/* Certificates Section */}
            <section className="bg-gray-800 p-6 rounded-lg border border-gray-700 opacity-50 pointer-events-none">
                <div className="flex justify-between">
                    <h2 className="text-xl font-semibold mb-4 text-blue-400">Certificates</h2>
                    <span className="text-xs bg-yellow-600/20 text-yellow-400 px-2 py-1 rounded border border-yellow-600/50 h-fit">Coming Soon</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <label className="block text-sm font-medium mb-2">Client Certificate (.crt)</label>
                        <input type="file" disabled className="text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-700 file:text-gray-500" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Client Key (.key)</label>
                        <input type="file" disabled className="text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-700 file:text-gray-500" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">CA Certificate (.crt)</label>
                        <input type="file" disabled className="text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-700 file:text-gray-500" />
                    </div>
                </div>
            </section>

            {/* Service Tokens Section */}
            <section className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h2 className="text-xl font-semibold mb-4 text-blue-400">Service Tokens</h2>
                <div className="flex gap-4 mb-6">
                    <input
                        type="text"
                        placeholder="Token Description (e.g. CI/CD Pipeline)"
                        className="flex-1 bg-gray-900 border border-gray-600 rounded px-3 py-2 outline-none"
                        value={newTokenDesc}
                        onChange={(e) => setNewTokenDesc(e.target.value)}
                    />
                    <button
                        onClick={handleGenerateToken}
                        disabled={loading}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded text-sm font-medium whitespace-nowrap"
                    >
                        Generate Token
                    </button>
                </div>

                {createdToken && (
                    <div className="p-4 bg-green-900/30 border border-green-500/50 rounded mb-6">
                        <p className="text-green-400 text-sm mb-1 font-bold">New Token Generated (Copy it now, it won't be shown again):</p>
                        <code className="block bg-black p-2 rounded text-green-300 font-mono break-all">{createdToken}</code>
                    </div>
                )}
            </section>
        </div>
    );
}
