"""地图服务API路由"""

from fastapi import APIRouter, HTTPException, Query

from models.schemas import (
    POISearchResponse,
    RouteRequest,
    RouteResponse,
    WeatherResponse,
)
from ..services.mcp_agent import query_mcp_agent

router = APIRouter(prefix="/map", tags=["地图服务"])


@router.get(
    "/poi",
    response_model=POISearchResponse,
    summary="搜索POI",
    description="根据关键词搜索POI(兴趣点)",
)
async def search_poi(
    keywords: str = Query(..., description="搜索关键词", example="故宫"),
    city: str = Query(..., description="城市", example="北京"),
    citylimit: bool = Query(True, description="是否限制在城市范围内"),
):
    try:
        result = await query_mcp_agent(
            f"请使用高德地图maps_text_search工具搜索POI，关键词：{keywords}，城市：{city}，citylimit：{citylimit}"
        )
        return POISearchResponse(
            success=True,
            message="POI搜索成功",
            data=[],
        )
    except Exception as e:
        print(f"❌ POI搜索失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"POI搜索失败: {str(e)}",
        )


@router.get(
    "/weather",
    response_model=WeatherResponse,
    summary="查询天气",
    description="查询指定城市的天气信息",
)
async def get_weather(
    city: str = Query(..., description="城市名称", example="北京"),
):
    try:
        result = await query_mcp_agent(
            f"请使用高德地图maps_weather工具查询{city}的天气信息"
        )
        return WeatherResponse(
            success=True,
            message="天气查询成功",
            data=[],
        )
    except Exception as e:
        print(f"❌ 天气查询失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"天气查询失败: {str(e)}",
        )


@router.post(
    "/route",
    response_model=RouteResponse,
    summary="规划路线",
    description="规划两点之间的路线",
)
async def plan_route(request: RouteRequest):
    try:
        route_type_map = {
            "walking": "maps_direction_walking",
            "driving": "maps_direction_driving",
            "transit": "maps_direction_transit_integrated",
        }
        tool_suffix = route_type_map.get(request.route_type, "maps_direction_walking")

        prompt = (
            f"请使用高德地图{tool_suffix}工具规划路线，"
            f"起点：{request.origin_address}，"
            f"终点：{request.destination_address}"
        )
        if request.origin_city:
            prompt += f"，起点城市：{request.origin_city}"
        if request.destination_city:
            prompt += f"，终点城市：{request.destination_city}"

        result = await query_mcp_agent(prompt)
        return RouteResponse(
            success=True,
            message="路线规划成功",
            data=None,
        )
    except Exception as e:
        print(f"❌ 路线规划失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"路线规划失败: {str(e)}",
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查地图服务是否正常",
)
async def health_check():
    try:
        return {
            "status": "healthy",
            "service": "map-service",
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}",
        )
