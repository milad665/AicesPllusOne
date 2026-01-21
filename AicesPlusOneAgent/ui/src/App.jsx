import React, { useState, useEffect, useCallback } from 'react';
import Split from 'react-split';
import axios from 'axios';
import CodeEditor from './components/Editor';
import Viewer from './components/Viewer';

// View types corresponding to C4 levels
const VIEWS = [
  { id: 'context', label: 'Context View', key: 'ContextView' },
  { id: 'container', label: 'Container View', key: 'ContainerView' },
  { id: 'component', label: 'Component View', key: 'ComponentView' },
];

function App() {
  const [architecture, setArchitecture] = useState(null);
  const [activeView, setActiveView] = useState(VIEWS[0]);
  const [script, setScript] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDirty, setIsDirty] = useState(false);

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
      // If 404/Empty, it might just need regeneration. 
      // If 503, agent down.
      console.error("Failed to fetch:", err);
      // Don't set error globally if it's just "empty"
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
      setScript(architecture[activeView.key].C4PlantUmlScript || '');
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
    <div className="flex h-screen flex-col bg-gray-900 text-white">
      {/* Header */}
      <header className="flex h-16 items-center justify-between border-b border-gray-700 px-6 bg-gray-800 shadow-md">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold tracking-tight text-blue-400">Aices Plus One</h1>
          <span className="text-sm text-gray-400 px-2 py-1 bg-gray-700 rounded border border-gray-600">v1.0</span>
        </div>

        {/* View Tabs */}
        <div className="flex space-x-1 bg-gray-700/50 p-1 rounded-lg">
          {VIEWS.map((view) => (
            <button
              key={view.id}
              onClick={() => setActiveView(view)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeView.id === view.id
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-300 hover:text-white hover:bg-gray-600'
                }`}
            >
              {view.label}
            </button>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          {error && <span className="text-red-400 text-sm mr-2">{error}</span>}

          <button
            onClick={handleSave}
            disabled={loading || !isDirty}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${loading || !isDirty
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-500 text-white shadow-sm ring-1 ring-white/10'
              }`}
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>

          <button
            onClick={handleRegenerate}
            disabled={loading}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors border ${loading
                ? 'bg-gray-700 border-gray-600 text-gray-500 cursor-not-allowed'
                : 'bg-transparent border-red-500/50 text-red-400 hover:bg-red-500/10 hover:border-red-400'
              }`}
          >
            {loading ? 'Regenerating...' : 'Regenerate Entirely'}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden relative">
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
          <div className="bg-[#1e1e1e] border-r border-gray-800">
            <CodeEditor value={script} onChange={handleEditorChange} />
          </div>
          <div className="bg-gray-50 relative">
            {loading && !script && (
              <div className="absolute inset-0 flex items-center justify-center bg-white/80 z-10 backdrop-blur-sm">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
              </div>
            )}
            <Viewer script={script} />
          </div>
        </Split>
      </main>
    </div>
  );
}

export default App;
