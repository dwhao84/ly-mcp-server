import ssl

import httpx

from ly_mcp_server.config import BASE_URL, LY_HEADERS


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
        headers=LY_HEADERS,
    ) as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
