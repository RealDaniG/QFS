# 🚀 Welcome to ATLAS X QFS

A modern, production-ready decentralized platform powered by the Quantitative Freedom System (QFS), designed to ensure economic coherence and transparency.

## ✨ Technology Stack

This scaffold provides a robust foundation built with:

### 🎯 Core Framework

- **⚡ Next.js 15** - The React framework for production with App Router
- **📘 TypeScript 5** - Type-safe JavaScript for better developer experience
- **🎨 Tailwind CSS 4** - Utility-first CSS framework for rapid UI development

### 🧩 UI Components & Styling

- **🧩 shadcn/ui** - High-quality, accessible components built on Radix UI
- **🎯 Lucide React** - Beautiful & consistent icon library
- **🌈 Framer Motion** - Production-ready motion library for React
- **🎨 Next Themes** - Perfect dark mode in 2 lines of code

### 📋 Forms & Validation

- **🎣 React Hook Form** - Performant forms with easy validation
- **✅ Zod** - TypeScript-first schema validation

### 🔄 State Management & Data Fetching

- **🐻 Zustand** - Simple, scalable state management
- **🔄 TanStack Query** - Powerful data synchronization for React
- **🌐 Axios** - Promise-based HTTP client

### 🗄️ Database & Backend

- **🗄️ Prisma** - Next-generation Node.js and TypeScript ORM
- **🔐 NextAuth.js** - Complete open-source authentication solution

### 🎨 Advanced UI Features

- **📊 TanStack Table** - Headless UI for building tables and datagrids
- **🖱️ DND Kit** - Modern drag and drop toolkit for React
- **📊 Recharts** - Redefined chart library built with React and D3
- **🖼️ Sharp** - High performance image processing

### 🌍 Internationalization & Utilities

- **🌍 Next Intl** - Internationalization library for Next.js
- **📅 Date-fns** - Modern JavaScript date utility library
- **🪝 ReactUse** - Collection of essential React hooks for modern development

## 🎯 Why This Scaffold?

- **🏎️ Fast Development** - Pre-configured tooling and best practices
- **🎨 Beautiful UI** - Complete shadcn/ui component library with advanced interactions
- **🔒 Type Safety** - Full TypeScript configuration with Zod validation
- **📱 Responsive** - Mobile-first design principles with smooth animations
- **🗄️ Database Ready** - Prisma ORM configured for rapid backend development
- **🔐 Auth Included** - NextAuth.js for secure authentication flows
- **📊 Data Visualization** - Charts, tables, and drag-and-drop functionality
- **🌍 i18n Ready** - Multi-language support with Next Intl
- **🚀 Production Ready** - Optimized build and deployment settings
- **🤖 AI-Friendly** - Structured codebase perfect for AI assistance

## 🧠 ATLAS Production Stack (QFS-Compliant)

**Core positioning**
- ATLAS Web = Deterministic View + Interaction Router over QFS
- Read-only projections: ledger, value-nodes, content (StorageEngine)
- Write actions: submit intent/governed transactions only; never mutate balances/rewards directly

**Frontend stack scope**
- Next.js 15 (App Router): Server Components for deterministic data reads; Edge rendering for presentation only
- TypeScript 5: Mirrors QFS policy schemas, ledger event typing
- Tailwind CSS 4: UI-only
- shadcn/ui + Radix: Governance/Explain-This/Appeals UIs
- Framer Motion: UX transitions/visualizations only; never influences ranking/economics
- React Hook Form + Zod: Client validation ≠ authority; server re-validation before QFS submission
- Zustand: UI state only (modals, preferences, drafts); never balances/reputation/governance outcomes
- TanStack Query: Fetch/cache ledger-derived views; cache is ephemeral/non-authoritative
- Axios: Versioned, deterministic APIs (read-only projections, intent submission, observability)

**Backend & database scope**
- Prisma + PostgreSQL: Non-authoritative (sessions, auth metadata, UI prefs, drafts, caches only)
- Balances/rewards/governance outcomes must be replayable from QFS logs, not DB
- NextAuth.js: Identity/session management, wallet/key association, role flags; auth ≠ authority

**Advanced UI features**
- TanStack Table: Ledger explorer, governance vote breakdowns, signal distributions
- Recharts: Reward flow visualization, signal observatory, non-mutating policy simulations
- DND Kit: UI composition/dashboard customization only; never ranking/priority/ordering

**Media & i18n**
- Sharp: UI-level image processing only; final content hash from StorageEngine
- Next Intl: Language never affects hashing/policy logic
- date-fns: Display-only; never consensus inputs

**AI constraint**
- AI is advisory only (summarization, suggestion, moderation assist)
- All effects route: observation → policy → governance → treasury

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to see your application running.

## 🤖 Powered by Z.ai

This scaffold is optimized for use with [Z.ai](https://chat.z.ai) - your AI assistant for:

- **💻 Code Generation** - Generate components, pages, and features instantly
- **🎨 UI Development** - Create beautiful interfaces with AI assistance  
- **🔧 Bug Fixing** - Identify and resolve issues with intelligent suggestions
- **📝 Documentation** - Auto-generate comprehensive documentation
- **🚀 Optimization** - Performance improvements and best practices

Ready to build something amazing? Start chatting with Z.ai at [chat.z.ai](https://chat.z.ai) and experience the future of AI-powered development!

## 📁 Project Structure

```
src/
├── app/                 # Next.js App Router pages
├── components/          # Reusable React components
│   └── ui/             # shadcn/ui components
├── hooks/              # Custom React hooks
└── lib/                # Utility functions and configurations
```

## 🧠 QFS × ATLAS Alignment (V13.7 / V13.8)

This ATLAS app is wired against the QFS V13.x economic substrate:

## 🗺️ ATLAS Web UI Roadmap (Canonical)

The canonical, machine-readable roadmap for the ATLAS Web UI (including explicit QFS/ATLAS invariants like read-only economics, deterministic replay, and “every number explainable”) is tracked here:

- `atlas_web_ui_roadmap_tracker.json`

- **V13.7 – ATLAS-ready**
  - RealLedger + QFSClient integration for deterministic transaction and
    state handling.
  - Secure-Chat engine + API adapters for encrypted, content-addressed
    messaging backed by QFS.
  - SignalAddons (e.g. humor) surfaced via APIs and tests, with all
    monetary effects still routed through QFS engines (TreasuryEngine + guards).

- **V13.8 – Value Nodes & Content-NFTs**
  - Spec and tests for users as deterministic value-nodes and content as
    NFT-style, content-addressed objects.
  - Replay-focused value-node tests live under `tests/value_node/` and
    do not modify core economics.

### Non-negotiable invariants

- QFS is the single source of truth for balances, rewards, and value.
- ATLAS UI and ATLAS API routes must not mutate economic state directly.
- All economic views are read-only representations derived from deterministic replay.
- Every visible number must have a “why?” path (explainability).
- Privacy-preserving by default (secure chat, content-addressed storage; hashes/metadata only in QFS logs).

### Phase B status (ATLAS API boundaries)

- API boundary tests now cover deterministic 401/4xx/5xx vs 2xx behavior for:
  - `src/api/routes/wallets.py`
  - `src/api/routes/metrics.py`
  - `src/api/routes/proofs.py`
- Coverage has been recomputed and recorded in `v13_test_coverage_status.json`.

### Phase C status (transactions + read-only economic views)

- Transactions API boundary tests are in place (`src/tests/test_transactions_api_boundary.py`) and `src/api/routes/transactions.py` is schema-safe.
- Read-only economic view helpers exist (`src/core/economic_views.py`) to support explainable UI rendering without client-side balance mutation.

For a full protocol-side description, see:

- `docs/QFS_ATLAS_MISSION_CONSTRAINTS.md`
- `docs/QFS_V13_7_SCOPE.md`
- `docs/QFS_V13_8_FULL_ENGINE_OVERVIEW.md`

## 🎨 Available Features & Components

This scaffold includes a comprehensive set of modern web development tools:

### 🧩 UI Components (shadcn/ui)

- **Layout**: Card, Separator, Aspect Ratio, Resizable Panels
- **Forms**: Input, Textarea, Select, Checkbox, Radio Group, Switch
- **Feedback**: Alert, Toast (Sonner), Progress, Skeleton
- **Navigation**: Breadcrumb, Menubar, Navigation Menu, Pagination
- **Overlay**: Dialog, Sheet, Popover, Tooltip, Hover Card
- **Data Display**: Badge, Avatar, Calendar

### 📊 Advanced Data Features

- **Tables**: Powerful data tables with sorting, filtering, pagination (TanStack Table)
- **Charts**: Beautiful visualizations with Recharts
- **Forms**: Type-safe forms with React Hook Form + Zod validation

### 🎨 Interactive Features

- **Animations**: Smooth micro-interactions with Framer Motion
- **Drag & Drop**: Modern drag-and-drop functionality with DND Kit
- **Theme Switching**: Built-in dark/light mode support

### 🔐 Backend Integration

- **Authentication**: Ready-to-use auth flows with NextAuth.js
- **Database**: Type-safe database operations with Prisma
- **API Client**: HTTP requests with Axios + TanStack Query
- **State Management**: Simple and scalable with Zustand

### 🌍 Production Features

- **Internationalization**: Multi-language support with Next Intl
- **Image Optimization**: Automatic image processing with Sharp
- **Type Safety**: End-to-end TypeScript with Zod validation
- **Essential Hooks**: 100+ useful React hooks with ReactUse for common patterns

## 🤝 Get Started with Z.ai

1. **Clone this scaffold** to jumpstart your project
2. **Visit [chat.z.ai](https://chat.z.ai)** to access your AI coding assistant
3. **Start building** with intelligent code generation and assistance
4. **Deploy with confidence** using the production-ready setup

---

Built with ❤️ for the developer community. Supercharged by [Z.ai](https://chat.z.ai) 🚀
