import React from 'react';
import Editor from '@monaco-editor/react';

const CodeEditor = ({ value, onChange, language = 'plantuml' }) => {
    return (
        <div className="h-full w-full overflow-hidden">
            <Editor
                height="100%"
                defaultLanguage={language}
                value={value}
                onChange={onChange}
                theme="vs-dark"
                options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                }}
            />
        </div>
    );
};

export default CodeEditor;
