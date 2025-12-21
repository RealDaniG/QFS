# desktop-runtime.md

## 1. Desktop-First, Single-Node Execution

ATLAS v19 adopts a **Single-Node Local Model**. The application is distributed as a self-contained desktop executable (Electron) that bundles both the frontend (Next.js Static Export) and the backend (Python FastAPI).

### The Runtime Model

* **Canonical Runtime**: The Electron Bundle. Web-hosted versions are secondary or for documentation only.
* **Local Backend**: The Electron "Main Process" is responsible for spawning the Python backend as a child process on a predetermined local port (default: `8000`).
* **Lifecycle Management**:
  * **Start**: Electron App Launch -> Spawn Python Process.
  * **Stop**: Electron App Quit -> Kill Python Process (SIGTERM/SIGKILL).
* **P2P Node**: Runs inside the Desktop App's Renderer Process (Frontend), connecting via WebSocket to the local backend and potentially to other peers via WebRTC.

## 2. Static Export & Electron Compatibility

To ensure the Next.js frontend runs reliably inside the `file://` protocol or local web server of Electron:

1. **Static Export**:
    * `next.config.mjs` must strictly set `output: 'export'`.
    * No `getServerSideProps` or Node.js runtime functions can be used in page components.
    * API Routes (`/pages/api` or `/app/api`) are **disabled** in the Next.js layer; all API calls must target the Python backend (`http://localhost:8000`).
2. **Image Optimization**:
    * The default Next.js Image Optimization API does not work in static exports.
    * `unoptimized: true` must be set in `next.config.mjs` images config.
3. **Boot Checks**:
    * The `desktop/main.js` script performs health checks on the Python backend before loading the main UI window to ensure the API is ready.

## 3. Environment Variable Validation

Due to the packaged nature of the desktop app, environment variables must be handled rigorously.

* **Build-Time**: Public variables (e.g., `NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID`) are baked into the static bundle.
* **Validation**:
  * On startup, the app checks for the presence of critical keys.
  * **Explicit Error UI**: If the WalletConnect Project ID is missing or invalid, the app displays a blocking error screen rather than failing silently during connection attempts.
* **Read-Only Fallback**: If backend keys (e.g., `OPENAI_API_KEY` - *if applicable*) are missing, the app should gracefully degrade to a "Read-Only" or "Local-Only" mode where possible, rather than crashing.

## 4. Post-Build Verification

A valid build must pass the following checks:

1. **Process Spawn**: Python backend starts without errors.
2. **Port Binding**: Backend binds successfully to port 8000 (locks managed if multiple instances).
3. **IPC Bridge**: The `preload.js` bridge successfully passes messages between Renderer and Main process.
