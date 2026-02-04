# Model Context Protocol (MCP) - Technical Reference
**Last Updated:** February 2026
**Protocol Version:** 2025-11-25

## 1. Overview
The Model Context Protocol (MCP) is an open-source standard designed to enable seamless, secure integration between AI applications (hosts) and external data sources or tools (servers). It follows a hub-and-spoke architecture where the host orchestrates interactions between the user, the LLM, and various MCP servers.

---

## 2. Core Architecture & Transport
MCP abstracts communication to allow for both local and remote deployments.

### 2.1 Message Format
*   **JSON-RPC 2.0**: All communications use this standard.
*   **Requests**: `id`, `method`, `params`.
*   **Responses**: `id`, `result` | `error`.
*   **Notifications**: No `id`, used for one-way updates (e.g., `list_changed`).

### 2.2 Transport Mechanisms
| Transport | Use Case | Protocol Specifics |
| :--- | :--- | :--- |
| **Stdio** | Local processes (Filesystem, DB) | JSON-RPC over stdin/stdout; newline delimited. |
| **Streamable HTTP** | Remote/Cloud servers | POST for client-to-server; **SSE (Server-Sent Events)** for server-to-client. |

---

## 3. Lifecycle Management
The lifecycle ensures synchronization and capability discovery.

1.  **Initialization**:
    *   `initialize` Request: Client proposes `protocolVersion` and capabilities (`roots`, `sampling`).
    *   `initialize` Response: Server responds with version, capabilities (`tools`, `resources`), and metadata.
    *   Version Negotiation: Server may propose its latest version if mismatch occurs.
2.  **Operational Phase**: Standard exchange of tool calls, resource reads, and prompt retrievals.
3.  **Shutdown Phase**: Graceful termination via closing the transport stream or connection.

---

## 4. Core Primitives & Interactions
| Primitive | Controller | Primary Methods | Description |
| :--- | :--- | :--- | :--- |
| **Tools** | **Model** | `tools/list`, `tools/call` | Executable functions the AI model can invoke. |
| **Resources** | **Application** | `resources/list`, `resources/read` | Data sources (logs, files) provided as context. |
| **Prompts** | **User** | `prompts/list`, `prompts/get` | Pre-defined templates to guide AI behavior. |

---

## 5. Security & Authentication
MCP utilizes a "Security-by-Design" philosophy.

### 5.1 Security Models
*   **Local (Stdio)**: Relies on OS-level process isolation and host application permissions.
*   **Remote (HTTP/SSE)**: 
    *   **DNS Rebinding Protection**: Prevents malicious web-based access to local servers.
    *   **Host Header Validation**: Verifies server identity.
    *   **CORS**: Restricts origins for web-based clients.

### 5.2 Authentication Patterns
*   **OAuth 2.0**: Standard for remote servers; supported via SDK `OAuthHelpers`.
*   **API Keys/Bearer Tokens**: Standard HTTP headers.
*   **ext-auth (Authorization Extensions)**: Fine-grained access control for specific tools or resources.

---

## 6. Advanced Integration Patterns

### 6.1 Dynamic Resource Templates (RFC 6570)
Allows servers to expose large datasets via parameterized URIs (e.g., `file:///{path}`) instead of static lists.
*   **Completion**: Uses `completion/complete` for contextual autocompletion of parameters.
*   **Late Binding**: Resources are only read when the specific URI is constructed.

### 6.2 Agentic Workflows via Sampling
The `sampling/createMessage` method allows a server to request a completion from the host's LLM.
*   **Intelligence/Speed Priority**: Servers can specify requirements for the sub-task.
*   **Human-in-the-Loop**: Hosts can require user approval for server-initiated sampling.

### 6.3 Hierarchical Orchestration
*   **Pipelining**: Host passes output of Server A as context to Server B.
*   **Contextual Grafting**: Server uses sampling to pull context from another server via the host.

---

## 7. Developer Ecosystem (v2 SDKs)
Official support for major ecosystems as of early 2026:
*   **TypeScript**: Monorepo with Express/Hono middleware.
*   **Python**: ASGI-compatible; `uv` support; high-level `MCPServer` API.
*   **Go/C#/.NET**: Stable versions optimized for enterprise/concurrency.
*   **Kotlin/Swift**: Optimized for JVM/Android and macOS/iOS respectively.

### 7.1 Developer Tools
*   **MCP Inspector**: Visual debugger (`@modelcontextprotocol/inspector`) for testing tools, resources, and auth in a sandbox.

---

## 8. Technical Summary Table (Spec 2025-11-25)
| Method / Feature | Function |
| :--- | :--- |
| `resources/templates/list` | Lazy-loading of massive data structures. |
| `sampling/createMessage` | Enables server-led agentic reasoning. |
| `notifications/resources/updated` | Triggers reactive agent loops. |
| **Content Blocks** | Multi-modal support (Text, Image, Audio). |
| **Annotations** | Metadata for priority, audience, and caching. |