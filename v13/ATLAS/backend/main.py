from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, wallet, chat, bounties, system, evidence, v1_auth
from fastapi import APIRouter

app = FastAPI(title="ATLAS v18 Backend", version="18.0.0-beta.1")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(v1_auth.router)  # V1 compatibility layer
app.include_router(wallet.router)
app.include_router(chat.router)
app.include_router(bounties.router)
app.include_router(system.router)
app.include_router(evidence.router)

# V1 Stubs for Verification
v1_wallets = APIRouter(prefix="/api/v1/wallets", tags=["wallets-v1"])


@v1_wallets.get("/")
async def list_wallets_stub():
    return []


v1_tx = APIRouter(prefix="/api/v1/transactions", tags=["transactions-v1"])


@v1_tx.get("/")
async def list_tx_stub():
    return []


app.include_router(v1_wallets)
app.include_router(v1_tx)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "18.9.5",
        "services": {"v18_clusters": "ready", "architecture": "modular"},
    }


if __name__ == "__main__":
    import uvicorn

    # Use 0.0.0.0 to ensure availability, port 8000 as agreed
    uvicorn.run(app, host="0.0.0.0", port=8001)
