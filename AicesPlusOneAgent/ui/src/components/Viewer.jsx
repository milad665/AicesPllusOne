import React from 'react';
import plantumlEncoder from 'plantuml-encoder';

const Viewer = ({ script }) => {
    if (!script) {
        return (
            <div className="flex h-full items-center justify-center bg-gray-50 text-gray-400">
                No diagram to display
            </div>
        );
    }

    const encoded = plantumlEncoder.encode(script);
    const url = `http://www.plantuml.com/plantuml/svg/${encoded}`;

    return (
        <div className="h-full w-full overflow-auto bg-white p-4 flex items-center justify-center">
            <img src={url} alt="C4 Diagram" className="max-w-full max-h-full object-contain" />
        </div>
    );
};

export default Viewer;
