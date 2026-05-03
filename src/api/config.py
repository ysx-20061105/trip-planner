"""应用配置"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_settings():
    """获取应用配置"""
    return {
        "app_name": "智能旅行规划助手",
        "app_version": "1.0.0",
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        "llm_model_name": os.getenv("LLM_MODEL_NAME", "gpt-4o"),
        "amap_api_key": os.getenv("AMAP_API_KEY", ""),
        "unsplash_access_key": os.getenv("UNSPLASH_ACCESS_KEY", ""),
        "cors_origins": os.getenv("CORS_ORIGINS", "*"),
    }


def get_cors_origins_list():
    """获取CORS允许的源列表"""
    settings = get_settings()
    origins = settings["cors_origins"]
    if origins == "*":
        return ["*"]
    return [origin.strip() for origin in origins.split(",")]
