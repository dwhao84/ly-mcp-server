from fastmcp.tools import ToolResult

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
    async def get_legislator_profile(name: str = "黃國昌") -> ToolResult:
        """
        查詢指定立法委員基本資料，預設查詢黃國昌。
        """
        result = await lookup_legislator_profile(name)

        if not result["found"]:
            return ToolResult(
                content=f"找不到{name}的立法委員資料。",
                structured_content=result,
                meta=CARD_TOOL_META,
            )

        profile = result["legislator"]

        return ToolResult(
            content=f"已找到{profile['name']}委員的資料卡片。",
            structured_content=result,
            meta=CARD_TOOL_META,
        )
