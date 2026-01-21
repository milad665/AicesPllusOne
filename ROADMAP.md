# Aices Plus One Roadmap

This roadmap outlines the strategic direction for the Aices Plus One project, encompassing the Code Analyzer Service and the C4 Architecture Agent.

## Phase 1: Foundation & Visibility (Current Focus)
**Goal:** Provide a robust, user-friendly interface for viewing and managing architecture diagrams, separating generation cost from viewing speed.

- [ ] **Web UI Dashboard**
    - Split-pane interface: PlantUML Script Editor vs. Diagram Viewer.
    - Real-time updates: Edit script -> Update diagram.
    - Control logic: Explicit buttons for "Regenerate" vs "View".
- [ ] **Storage & Persistence**
    - Decouple storage from logic.
    - Support for Cloud Storage Buckets (GCS) for persistence.
    - Store dual formats: JSON structure + PlantUML text.
- [ ] **Agent Logic Refinement**
    - Strictly separate "Regeneration" (Expensive, AI-driven) from "Retrieval" (Cheap, Storage-driven).
    - MCP Tool update: `get_c4_architecture` becomes read-only.

## Phase 2: IDE & Workflow Integration
**Goal:** Bring architectural context directly into the developer's workflow where code is written.

- [ ] **IDE Extensions**
    - VS Code / Cursor extension to show the "Component" view relevant to the currently open file.
    - "Architectural Linter": Warn if code violations contradict the C4 model.
- [ ] **Interactive Diagram Manipulation**
    - Drag-and-drop structural editing in the UI.
    - Bi-directional sync: Diagram changes suggest code refactors.

## Phase 3: Deep Context & Intelligence
**Goal:** Transform the system from a passive observer to an active architectural partner.

- [ ] **Project Documentation Store**
    - Store and index non-code artifacts (PRDs, Design Docs).
    - Link business requirements to architectural components.
- [ ] **Agent Memory Integration**
    - "Institutional Memory": Agent remembers why decisions were made.
    - Auto-capture architectural decisions during chat sessions.
- [ ] **Bug & Issue Mapping**
    - Overlay bug hotspots onto the C4 diagram.
    - "Healing": Suggest architectural fixes for recurring bug patterns.

## Phase 4: Expanded Ecosystem
**Goal:** Support complex, polyglot enterprise environments.

- [ ] **Language Support Expansion**
    - C++, Go, Rust, C#.
- [ ] **Enterprise Features**
    - SSO Integration.
    - Role-Based Access Control (RBAC) for architecture views.
    - Version History & "Time Travel" for architecture evolution.
