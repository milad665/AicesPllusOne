import React, { useState, useEffect } from 'react';
import Split from 'react-split';
import axios from 'axios';
import { useAuth } from "@clerk/clerk-react";
import CodeEditor from './Editor';
import Viewer from './Viewer';
import { Helmet } from 'react-helmet-async';

// View types corresponding to levels
const VIEWS = [
    { id: 'context', label: 'Context View', key: 'ContextView' },
    { id: 'container', label: 'Container View', key: 'ContainerView' },
    { id: 'component', label: 'Component View', key: 'ComponentView' },
];

export default function DashboardView() {
    const { getToken } = useAuth();
    const [architecture, setArchitecture] = useState(null);
    const [activeView, setActiveView] = useState(VIEWS[0]);
    const [script, setScript] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isDirty, setIsDirty] = useState(false);

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

    // Fetch initial architecture
    const fetchArchitecture = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get('/api/architecture');
            if (response.data) {
                setArchitecture(response.data);
            }
        } catch (err) {
            console.error("Failed to fetch:", err);
            if (err.response?.status !== 404) {
                setError(err.response?.data?.detail || "Failed to load architecture");
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchArchitecture();
    }, []);

    // Sync script when architecture or active view changes
    useEffect(() => {
        if (architecture && architecture[activeView.key]) {
            setScript(architecture[activeView.key].PlantUmlScript || '');
            setIsDirty(false);
        } else {
            setScript('');
        }
    }, [architecture, activeView]);

    const handleRegenerate = async () => {
        if (!confirm("This will overwrite all current diagrams. Continue?")) return;

        setLoading(true);
        setError(null);
        try {
            const response = await axios.post('/api/architecture/regenerate');
            setArchitecture(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to regenerate");
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post('/api/architecture/update', {
                plantuml_script: script,
                view_type: activeView.id
            });
            setArchitecture(response.data);
            setIsDirty(false);
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to update");
        } finally {
            setLoading(false);
        }
    };

    const handleEditorChange = (value) => {
        setScript(value);
        setIsDirty(true);
    };

    return (
        <div className="flex h-full flex-col bg-white">
            <Helmet>
                <title>Dashboard - Aices+1</title>
            </Helmet>

            {/* Top Bar - View Controls */}
            <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 shadow-sm z-10">
                {/* View Tabs */}
                <div className="flex space-x-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
                    {VIEWS.map((view) => (
                        <button
                            key={view.id}
                            onClick={() => setActiveView(view)}
                            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeView.id === view.id
                                ? 'bg-white text-sky-700 shadow-sm border border-slate-200/50'
                                : 'text-slate-500 hover:text-slate-900 hover:bg-slate-200/50'
                                }`}
                        >
                            {view.label}
                        </button>
                    ))}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                    {error && <span className="text-red-500 text-sm mr-2">{error}</span>}

                    <button
                        onClick={handleSave}
                        disabled={loading || !isDirty}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${loading || !isDirty
                            ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200'
                            : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-500/20'
                            }`}
                    >
                        {loading ? 'Saving...' : 'Save Changes'}
                    </button>

                    <button
                        onClick={handleRegenerate}
                        disabled={loading}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors border ${loading
                            ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                            : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300'
                            }`}
                    >
                        {loading ? 'Regenerate' : 'Regenerate'}
                    </button>
                </div>
            </header>

            {/* Editor Content */}
            <div className="flex-1 overflow-hidden relative">
                <Split
                    className="flex h-full"
                    sizes={[40, 60]}
                    minSize={200}
                    gutterSize={4}
                    gutterAlign="center"
                    snapOffset={30}
                    dragInterval={1}
                    direction="horizontal"
                    cursor="col-resize"
                >
                    <div className="bg-white border-r border-slate-200">
                        <CodeEditor value={script} onChange={handleEditorChange} theme="light" />
                    </div>
                    <div className="bg-slate-50 relative flex flex-col">
                        {loading && !script && (
                            <div className="absolute inset-0 flex items-center justify-center bg-white/80 z-10 backdrop-blur-sm">
                                <div className="animate-spin rounded-full h-12 w-12 border-4 border-sky-500 border-t-transparent"></div>
                            </div>
                        )}
                        <div className="flex-1 overflow-auto p-4 flex items-center justify-center">
                            <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 min-w-[50%] min-h-[50%] flex items-center justify-center">
                                <Viewer script={script} />
                            </div>
                        </div>
                    </div>
                </Split>
            </div>
        </div>
    );
}
