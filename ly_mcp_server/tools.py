from fastmcp.tools import ToolResult

from ly_mcp_server.legislators import lookup_legislator_profile, lookup_legislators_by_party
from ly_mcp_server.ly_client import fetch_legislature_dataset
from ly_mcp_server.widgets.legislator_card import CARD_TOOL_META, PARTY_LIST_TOOL_META


def register_tools(mcp) -> None:
    @mcp.tool()
    async def search_legislature_dataset(
        dataset_id: str = "9",
        page: int = 1,
        select_term: str = "all",
    ) -> dict:
        """
        低階除錯用：查詢立法院開放資料 API，回傳原始資料集內容。
        不要用這個工具回答「國民黨有哪些人」、「民進黨立委名單」或任何需要卡片顯示的立委查詢。
        若要查立委資料卡，請使用 get_legislator_profile；若要查政黨有哪些立委，請使用 get_legislators_by_party。
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

    @mcp.tool()
    async def get_legislators_by_party_data(party: str = "台灣民眾黨") -> dict:
        """
        提供政黨立委名單 widget 讀取指定政黨的結構化資料。
        """
        return await lookup_legislators_by_party(party)

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

    @mcp.tool(meta=PARTY_LIST_TOOL_META)
    async def get_legislators_by_party(party: str = "台灣民眾黨") -> ToolResult:
        """
        查詢指定政黨有哪些立法委員，並用卡片 widget 顯示每位委員的檔案資料。

        適用於：
        - 國民黨有哪些人
        - 民進黨有哪些立委
        - 民眾黨立委名單
        - 顯示某政黨黨員資料卡
        """
        result = await lookup_legislators_by_party(party)

        return ToolResult(
            content=f"{result['message']}以下以卡片顯示每位委員的檔案資料。",
            structured_content=result,
            meta=PARTY_LIST_TOOL_META,
        )
