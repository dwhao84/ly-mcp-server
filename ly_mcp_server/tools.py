from mcp import types

from ly_mcp_server.legislators import lookup_legislator_profile
from ly_mcp_server.ly_client import fetch_legislature_dataset
from ly_mcp_server.widgets.legislator_card import CARD_TOOL_META


def register_tools(mcp) -> None:
    @mcp.tool()
    async def search_legislature_dataset(
        dataset_id: str = "9",
        page: int = 1,
        select_term: str = "all",
    ) -> dict:
        """
        查詢立法院開放資料 API。
        """
        return await fetch_legislature_dataset(
            dataset_id=dataset_id,
            page=page,
            select_term=select_term,
        )

    @mcp.tool()
    async def get_legislator_profile_data(name: str = "黃國昌") -> dict:
        """
        提供委員資料卡 widget 讀取指定立法委員的結構化資料。
        """
        return await lookup_legislator_profile(name)

    @mcp.tool(meta=CARD_TOOL_META)
    async def get_legislator_profile(name: str = "黃國昌") -> types.CallToolResult:
        """
        查詢指定立法委員基本資料，預設查詢黃國昌。
        """
        result = await lookup_legislator_profile(name)

        if not result["found"]:
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"找不到{name}的立法委員資料。",
                    )
                ],
                structuredContent=result,
                _meta=CARD_TOOL_META,
                isError=False,
            )

        profile = result["legislator"]

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"已找到{profile['name']}委員的資料卡片。",
                )
            ],
            structuredContent=result,
            _meta=CARD_TOOL_META,
            isError=False,
        )
