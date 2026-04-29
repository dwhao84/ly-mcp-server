from fastmcp import FastMCP
import httpx
import os
import ssl

mcp = FastMCP("立法院 Open Data MCP")

BASE_URL = "https://data.ly.gov.tw/odw/openDatasetJson.action"


def create_ly_ssl_context() -> ssl.SSLContext:
    """
    建立保留憑證驗證的 SSL context。

    data.ly.gov.tw 的憑證鏈在新版 Python/OpenSSL 嚴格 X509 檢查下會因
    Missing Subject Key Identifier 失敗；這裡只關閉嚴格模式，不關閉憑證驗證。
    """
    context = ssl.create_default_context()
    strict_flag = getattr(ssl, "VERIFY_X509_STRICT", 0)
    if strict_flag:
        context.verify_flags &= ~strict_flag
    return context


async def fetch_legislature_dataset(
    dataset_id: str = "9",
    page: int = 1,
    select_term: str = "all",
) -> dict:
    params = {
        "id": dataset_id,
        "selectTerm": select_term,
        "page": page,
    }

    async with httpx.AsyncClient(
        timeout=20,
        verify=create_ly_ssl_context(),
        trust_env=False,
    ) as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()


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
async def get_legislator_profile(name: str = "黃國昌") -> dict:
    """
    查詢指定立法委員基本資料，預設查詢黃國昌。
    """
    data = await fetch_legislature_dataset(dataset_id="9", page=1, select_term="all")
    legislators = data.get("jsonList", [])
    legislator = next(
        (item for item in legislators if item.get("name") == name),
        None,
    )

    if not legislator:
        return {
            "found": False,
            "name": name,
            "message": f"找不到{name}的立法委員資料。",
        }

    pic_url = legislator.get("picUrl") or ""

    return {
        "found": True,
        "name": legislator.get("name"),
        "ename": legislator.get("ename"),
        "party": legislator.get("party"),
        "partyGroup": legislator.get("partyGroup"),
        "areaName": legislator.get("areaName"),
        "committee": legislator.get("committee"),
        "tel": legislator.get("tel"),
        "fax": legislator.get("fax"),
        "addr": legislator.get("addr"),
        "degree": legislator.get("degree"),
        "experience": legislator.get("experience"),
        "term": legislator.get("term"),
        "onboardDate": legislator.get("onboardDate"),
        "imageUrl": pic_url.replace("http://", "https://"),
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
