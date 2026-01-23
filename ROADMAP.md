# Aices Plus One Roadmap

This roadmap outlines the strategic direction for the Aices Plus One project, encompassing the Code Analyzer Service and the C4 Architecture Agent.

## Phase 1: Foundation & Visibility (Completed)
**Goal:** Provide a robust, user-friendly interface for viewing and managing architecture diagrams, separating generation cost from viewing speed.

- [x] **Web UI Dashboard**
    - Split-pane interface: PlantUML Script Editor vs. Diagram Viewer.
    - Real-time updates: Edit script -> Update diagram.
- [x] **Storage & Persistence**
    - Decouple storage from logic (StorageProvider pattern).
    - Support for Google Cloud Storage (GCS).
- [x] **Agent Logic Refinement**
    - Separation of "Regeneration" (AI) from "Retrieval" (Storage).
    - Read-only MCP tools for speed.

## Phase 2: IDE & Workflow Integration (In Progress)
**Goal:** Bring architectural context directly into the developer's workflow where code is written.

- [x] **VS Code Extension (Basic)**
    - Show "Component" view relevant to the currently open file.
- [ ] **Interactive Diagram Manipulation**
    - Drag-and-drop structural editing in the UI.
    - Bi-directional sync: Diagram changes suggest code refactors.

## Phase 3: Deep Context & Knowledge Graph
**Goal:** Transform the system from a passive observer to an active architectural partner with deep semantic understanding.

- [ ] **Knowledge Graph Implementation**
    - Migrate from simple key-value/vector storage to a **Graph Database** (e.g., Neo4j, FalkorDB).
    - Model relationships between Code, Architecture, and Business Concepts as graph nodes/edges.
- [ ] **Coding Standards & Best Practices**
    - **Store/Retrieve Standards**: MCP tools to save "Good Practice" and "Bad Practice" examples.
    - **Semantic Search**: AI searches the Knowledge Graph for coding standards relevant to the current task.
    - **Automated Reviews**: Agent checks code against stored standards in the Knowledge Graph.
- [ ] **Project Documentation Integration**
    - Index READMEs, ADRs, and Docs into the Knowledge Graph.
    - Link documentation nodes to architectural component nodes.

## Phase 4: Enterprise Platform & Commercialization
**Goal:** Scale the solution for multi-tenant, secure, commercial deployment.

### Architecture & Deployment
- [ ] **Cloud-Native Agent Deployment**
    - Deploy AicesPlusOne Agent, Knowledge Graph, and Storage to **Google Cloud Platform**.
    - Auto-scaling configuration.
- [ ] **Hybrid Code Analyzer Deployment**
    - Containerize the **Code Analyzer Service** for client-side deployment.
    - Support Docker & K8s for on-premise or private cloud (client network) execution.
    - Secure mTLS tunneling between Client Analyzer and Cloud Agent.

### Multi-Tenancy & Security
- [ ] **Strict Tenant Isolation**
    - **Data Partitioning**: Architecture data, Knowledge Graphs, and Coding Standards stored with strict logical or physical separation per tenant.
    - **Namespace Isolation**: Vector databases and Graph stores namespaced by `tenant_id`.
    - **Hybrid Connectivity**: Tenants can configure their own **Code Analyzer** instances (URL, IP Whitelisting).
    - **mTLS Security**: Support for tenant-managed mTLS certificates for secure Agent-to-Analyzer communication.
- [ ] **Admin & Billing**
    - **Super Admin Dashboard**: Global view of all tenants, subscriptions, and revenue.
    - **Usage Analytics**: Aggregate token usage and API calls for billing calculations.
- [ ] **GDPR Compliance & Privacy**
    - **Right to be Forgotten**: Automated workflows to delete all data associated with a user or tenant upon request.
    - **Data Residency**: Option to host tenant data in specific geographic regions (EU/US).
    - **Audit Logs**: Comprehensive, immutable logs of all data access and modifications.
    - **PII Redaction**: Auto-redaction of PII from code snippets or documentation before storage.
- [ ] **Authentication & SSO**
    - Integrate with external Identity Providers (Auth0, Okta, Google Workspace).
    - Support Single Sign-On (SSO) for enterprise clients.

### Commercial Features
- [ ] **Subscription & Billing**
    - Monthly subscription model per tenant.
    - Usage tracking (API calls, Storage, AI tokens).
- [ ] **Tenant Dashboard**
    - Configuration management.
    - User/Role administration.
    - Billing history and usage reports.
