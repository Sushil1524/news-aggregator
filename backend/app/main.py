from fastapi import FastAPI
# from app.routes import auth, articles, comments, vocab, ai_tools
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, article, comments, bookmarks, admin, analytics, vocab
from contextlib import asynccontextmanager
from app.services.scheduler import start_scheduler
from app.services.analytics_scheduler import start_flusher_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start the scheduler
    start_scheduler()
    print("Scheduler started: fetching news every 15 minutes")
    start_flusher_scheduler() 
    print("Analytics flusher started: flushing views every 1 minutes")
    yield
    # Shutdown: optional cleanup
    print("Shutting down application...")

# app = FastAPI(title="Intelligent News Aggregator", lifespan=lifespan,docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI(title="Intelligent News Aggregator")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(article.router, prefix="/article", tags=["articles"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])
app.include_router(bookmarks.router, prefix="/bookmarks", tags=["Bookmarks"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])   
app.include_router(vocab.router, prefix="/vocab", tags=["vocab"])
# app.include_router(ai_tools.router, prefix="/ai", tags=["ai_tools"])

@app.get("/")
def root():
    return {"message": "Welcome to Intelligent News Aggregator API"}

