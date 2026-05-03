"""FastAPI主应用"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_mcp_adapters.client import MultiServerMCPClient

from .config import get_settings, get_cors_origins_list
from .routes import trip, poi, map as map_routes
from .services.mcp_agent import init_mcp_agent
from agent.agent import get_trip_planner_agent

settings = get_settings()

app = FastAPI(
    title=settings["app_name"],
    version=settings["app_version"],
    description="基于多智能体的智能旅行规划助手API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trip.router, prefix="/api")
app.include_router(poi.router, prefix="/api")
app.include_router(map_routes.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 60)
    print(f"🚀 {settings['app_name']} v{settings['app_version']}")
    print("=" * 60)

    # 初始化MCP Agent（供POI、地图路由使用）
    print("\n🔧 正在初始化MCP Agent...")
    await init_mcp_agent()

    # 初始化旅行规划多智能体系统（供trip路由使用）
    print("\n🔧 正在初始化旅行规划多智能体系统...")
    client = MultiServerMCPClient({
        "amap": {
            "transport": "sse",
            "url": f"https://mcp.amap.com/sse?key={settings['amap_api_key']}",
        }
    })
    tools = await client.get_tools()
    get_trip_planner_agent(
        apiKey=settings["llm_api_key"],
        baseUrl=settings["llm_base_url"],
        modelName=settings["llm_model_name"],
        tools=tools,
    )

    print("\n" + "=" * 60)
    print("📚 API文档: http://localhost:8000/docs")
    print("📖 ReDoc文档: http://localhost:8000/redoc")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    print("\n" + "=" * 60)
    print("👋 应用正在关闭...")
    print("=" * 60 + "\n")


@app.get("/")
async def root():
    return {
        "name": settings["app_name"],
        "version": settings["app_version"],
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings["app_name"],
        "version": settings["app_version"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
