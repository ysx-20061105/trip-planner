"""POI相关API路由"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..services.mcp_agent import query_mcp_agent
from ..services.unsplash_service import get_unsplash_service

router = APIRouter(prefix="/poi", tags=["POI"])


class POIDetailResponse(BaseModel):
    """POI详情响应"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.get(
    "/detail/{poi_id}",
    response_model=POIDetailResponse,
    summary="获取POI详情",
    description="根据POI ID获取详细信息,包括图片",
)
async def get_poi_detail(poi_id: str):
    try:
        result = await query_mcp_agent(
            f"请使用高德地图工具查询POI详情，POI ID为: {poi_id}"
        )
        return POIDetailResponse(
            success=True,
            message="获取POI详情成功",
            data={"raw": result},
        )
    except Exception as e:
        print(f"❌ 获取POI详情失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取POI详情失败: {str(e)}",
        )


@router.get(
    "/search",
    summary="搜索POI",
    description="根据关键词搜索POI",
)
async def search_poi(keywords: str, city: str = "北京"):
    try:
        result = await query_mcp_agent(
            f"请使用高德地图maps_text_search工具搜索{city}的{keywords}相关POI"
        )
        return {
            "success": True,
            "message": "搜索成功",
            "data": result,
        }
    except Exception as e:
        print(f"❌ 搜索POI失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索POI失败: {str(e)}",
        )


@router.get(
    "/photo",
    summary="获取景点图片",
    description="根据景点名称从Unsplash获取图片",
)
async def get_attraction_photo(name: str):
    try:
        unsplash_service = get_unsplash_service()

        photo_url = unsplash_service.get_photo_url(f"{name} China landmark")
        if not photo_url:
            photo_url = unsplash_service.get_photo_url(name)

        return {
            "success": True,
            "message": "获取图片成功",
            "data": {
                "name": name,
                "photo_url": photo_url,
            },
        }
    except Exception as e:
        print(f"❌ 获取景点图片失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取景点图片失败: {str(e)}",
        )
