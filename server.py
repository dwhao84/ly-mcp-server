from fastmcp import FastMCP
from mcp import types
import httpx
import os
import ssl

mcp = FastMCP("立法院 Open Data MCP")

BASE_URL = "https://data.ly.gov.tw/odw/openDatasetJson.action"
LY_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "identity",
}
CARD_TEMPLATE_URI = "ui://widget/legislator-card-v2.html"
CARD_MIME_TYPE = "text/html;profile=mcp-app"
CARD_TOOL_META = {
    "openai/outputTemplate": CARD_TEMPLATE_URI,
    "openai/toolInvocation/invoking": "查詢立委資料中...",
    "openai/toolInvocation/invoked": "立委資料已載入",
    "openai/widgetAccessible": True,
    "ui": {"resourceUri": CARD_TEMPLATE_URI},
}


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


def create_legislator_card_html() -> str:
    return """
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      :root {
        color-scheme: light dark;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }

      body {
        margin: 0;
        padding: 16px;
        background: transparent;
      }

      .card {
        overflow: hidden;
        border: 1px solid rgba(127, 127, 127, 0.22);
        border-radius: 24px;
        background: color-mix(in srgb, Canvas 94%, CanvasText 6%);
        color: CanvasText;
        box-shadow: 0 18px 60px rgba(0, 0, 0, 0.10);
      }

      .hero {
        display: flex;
        gap: 16px;
        align-items: center;
        padding: 20px;
        background:
          radial-gradient(circle at top left, rgba(43, 127, 255, 0.20), transparent 38%),
          linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(127, 127, 127, 0.08));
      }

      .avatar {
        width: 88px;
        height: 88px;
        flex: 0 0 auto;
        border: 3px solid rgba(255, 255, 255, 0.7);
        border-radius: 22px;
        object-fit: cover;
        background: rgba(127, 127, 127, 0.18);
      }

      .name {
        margin: 0 0 6px;
        font-size: 28px;
        line-height: 1.15;
      }

      .subtitle {
        margin: 0;
        color: color-mix(in srgb, CanvasText 72%, transparent);
        font-size: 15px;
        line-height: 1.45;
      }

      .content {
        display: grid;
        gap: 12px;
        padding: 18px 20px 20px;
      }

      .field {
        display: grid;
        gap: 4px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(127, 127, 127, 0.18);
      }

      .field:last-child {
        padding-bottom: 0;
        border-bottom: 0;
      }

      .label {
        color: color-mix(in srgb, CanvasText 55%, transparent);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      .value {
        margin: 0;
        font-size: 15px;
        line-height: 1.55;
        white-space: pre-line;
      }

      .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      .chip {
        border-radius: 999px;
        padding: 6px 10px;
        background: rgba(43, 127, 255, 0.13);
        color: color-mix(in srgb, CanvasText 88%, #2b7fff 12%);
        font-size: 13px;
        font-weight: 650;
      }

      .empty {
        padding: 18px;
        border: 1px dashed rgba(127, 127, 127, 0.35);
        border-radius: 18px;
        color: color-mix(in srgb, CanvasText 68%, transparent);
      }
    </style>
  </head>
  <body>
    <main id="root" class="empty">正在載入立委資料...</main>

    <script>
      function splitItems(value) {
        return String(value || "")
          .split(/[;；\\n]/)
          .map((item) => item.trim())
          .filter(Boolean);
      }

      function escapeHtml(value) {
        return String(value || "").replace(/[&<>"']/g, (char) => ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        }[char]));
      }

      function field(label, value) {
        if (!value) return "";
        return `
          <section class="field">
            <div class="label">${escapeHtml(label)}</div>
            <p class="value">${escapeHtml(value)}</p>
          </section>
        `;
      }

      function renderFromOutput(output) {
        const legislator = output.legislator;
        const root = document.getElementById("root");

        if (!legislator || output.found === false) {
          root.className = "empty";
          root.textContent = output.message || "找不到可顯示的立委資料。";
          return;
        }

        const committees = splitItems(legislator.committee).slice(-3);
        const phones = splitItems(legislator.tel).slice(0, 3).join("\\n");
        const degree = splitItems(legislator.degree).slice(0, 3).join("\\n");
        const experience = splitItems(legislator.experience).slice(0, 4).join("\\n");

        root.className = "card";
        root.innerHTML = `
          <section class="hero">
            <img class="avatar" src="${escapeHtml(legislator.imageUrl)}" alt="${escapeHtml(legislator.name)}照片" />
            <div>
              <h1 class="name">${escapeHtml(legislator.name)}</h1>
              <p class="subtitle">${escapeHtml(legislator.ename || "")}</p>
              <div class="chips" style="margin-top: 10px;">
                <span class="chip">${escapeHtml(legislator.party || "政黨未提供")}</span>
                <span class="chip">第 ${escapeHtml(legislator.term || "")} 屆</span>
              </div>
            </div>
          </section>
          <section class="content">
            ${field("選區", legislator.areaName)}
            ${field("近期委員會", committees.join("\\n"))}
            ${field("聯絡電話", phones)}
            ${field("學歷", degree)}
            ${field("經歷摘要", experience)}
          </section>
        `;
      }

      function render() {
        renderFromOutput(window.openai?.toolOutput || {});
      }

      render();
      window.addEventListener("message", (event) => {
        if (event.source !== window.parent) return;
        const message = event.data;
        if (!message || message.jsonrpc !== "2.0") return;
        if (message.method !== "ui/notifications/tool-result") return;

        const result = message.params || {};
        renderFromOutput(result.structuredContent || result);
      });
    </script>
  </body>
</html>
""".strip()


@mcp.resource(
    CARD_TEMPLATE_URI,
    name="立委資料卡片",
    mime_type=CARD_MIME_TYPE,
    meta={
        "openai/widgetDescription": "顯示立法委員照片、政黨、選區、委員會、聯絡方式與簡歷的資料卡。",
        "openai/widgetPrefersBorder": True,
        "ui": {
            "prefersBorder": True,
            "domain": "https://ly-mcp-server.onrender.com",
            "csp": {
                "connectDomains": [],
                "resourceDomains": ["https://www.ly.gov.tw"],
            },
        },
    },
)
async def legislator_card_template() -> str:
    return create_legislator_card_html()


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


@mcp.tool(meta=CARD_TOOL_META)
async def get_legislator_profile(name: str = "黃國昌") -> types.CallToolResult:
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
        return types.CallToolResult(
            content=[
                types.TextContent(type="text", text=f"找不到{name}的立法委員資料。")
            ],
            structuredContent={
                "found": False,
                "name": name,
                "message": f"找不到{name}的立法委員資料。",
            },
            _meta=CARD_TOOL_META,
            isError=False,
        )

    pic_url = legislator.get("picUrl") or ""

    profile = {
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

    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=f"已找到{profile['name']}委員的資料卡片。",
            )
        ],
        structuredContent={
            "found": True,
            "legislator": profile,
        },
        _meta=CARD_TOOL_META,
        isError=False,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
