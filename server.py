from fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("立法院 Open Data MCP")

BASE_URL = "https://data.ly.gov.tw/odw/openDatasetJson.action"


@mcp.tool()
async def search_legislature_dataset(
    dataset_id: str = "9",
    page: int = 1,
    select_term: str = "all",
) -> dict:
    """
    查詢立法院開放資料 API。
    """

    params = {
        "id": dataset_id,
        "selectTerm": select_term,
        "page": page,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
