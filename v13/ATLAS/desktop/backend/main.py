from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, wallet, chat, bounties, system

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
app.include_router(wallet.router)
app.include_router(chat.router)
app.include_router(bounties.router)
app.include_router(system.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "18.0.0-beta.1"}


if __name__ == "__main__":
    import uvicorn

    # Use 0.0.0.0 to ensure availability, port 8000 as agreed
    uvicorn.run(app, host="0.0.0.0", port=8000)
