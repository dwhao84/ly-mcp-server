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
CARD_TEMPLATE_URI = "ui://widget/legislator-card-v4.html"
CARD_MIME_TYPE = "text/html+skybridge"
CARD_TOOL_META = {
    "openai/outputTemplate": CARD_TEMPLATE_URI,
    "openai/toolInvocation/invoking": "查詢立委資料中...",
    "openai/toolInvocation/invoked": "立委資料已載入",
    "openai/widgetAccessible": True,
    "openai/resultCanProduceWidget": True,
    "ui": {
        "resourceUri": CARD_TEMPLATE_URI,
        "visibility": ["model", "app"],
    },
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
        color-scheme: light;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }

      body {
        margin: 0;
        padding: 18px;
        background: transparent;
      }

      .card {
        position: relative;
        overflow: hidden;
        border: 1px solid #e5e7eb;
        border-radius: 28px;
        background: #ffffff;
        color: #111827;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
      }

      .hero {
        position: relative;
        display: flex;
        gap: 18px;
        align-items: flex-end;
        padding: 24px;
        min-height: 156px;
      }

      .hero::after {
        position: absolute;
        inset: auto 0 0;
        height: 1px;
        content: "";
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
      }

      .avatar {
        width: 116px;
        height: 136px;
        flex: 0 0 auto;
        border: 1px solid #e5e7eb;
        border-radius: 26px;
        object-fit: cover;
        object-position: top center;
        background: #f9fafb;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
      }

      .avatarFallback {
        display: grid;
        place-items: center;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: 0.08em;
      }

      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
        border: 1px solid #e5e7eb;
        border-radius: 999px;
        padding: 6px 10px;
        background: #ffffff;
        color: #6b7280;
        font-size: 12px;
        font-weight: 750;
      }

      .name {
        margin: 0 0 6px;
        font-size: clamp(30px, 8vw, 46px);
        line-height: 1.15;
        letter-spacing: -0.04em;
      }

      .subtitle {
        margin: 0;
        color: #6b7280;
        font-size: 15px;
        line-height: 1.45;
      }

      .content {
        display: grid;
        gap: 14px;
        padding: 20px 24px 24px;
      }

      .field {
        display: grid;
        gap: 4px;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 13px 14px;
        background: #ffffff;
      }

      .field:last-child {
        border-bottom: 1px solid #e5e7eb;
      }

      .label {
        color: #6b7280;
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
        margin-top: 14px;
      }

      .chip {
        border-radius: 999px;
        padding: 7px 11px;
        background: #f3f7ff;
        color: #1f4f9a;
        font-size: 13px;
        font-weight: 750;
      }

      .empty {
        padding: 18px;
        border: 1px dashed #d1d5db;
        border-radius: 18px;
        color: #6b7280;
        background: #ffffff;
      }

      .grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }

      .wide {
        grid-column: 1 / -1;
      }

      .loading .hero {
        align-items: center;
      }

      .skeleton {
        position: relative;
        overflow: hidden;
        border-radius: 999px;
        background: #eef2f7;
      }

      .skeleton::after {
        position: absolute;
        inset: 0;
        content: "";
        transform: translateX(-100%);
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.78), transparent);
        animation: shimmer 1.35s ease-in-out infinite;
      }

      .skeletonAvatar {
        width: 116px;
        height: 136px;
        flex: 0 0 auto;
        border-radius: 26px;
      }

      .skeletonPill {
        width: 132px;
        height: 27px;
        margin-bottom: 12px;
      }

      .skeletonName {
        width: min(280px, 54vw);
        height: 46px;
        margin-bottom: 10px;
      }

      .skeletonSubtitle {
        width: 148px;
        height: 18px;
      }

      .skeletonChip {
        width: 72px;
        height: 30px;
      }

      .skeletonField {
        gap: 12px;
      }

      .skeletonLabel {
        width: 72px;
        height: 13px;
      }

      .skeletonValue {
        width: 72%;
        height: 18px;
      }

      .skeletonValueShort {
        width: 46%;
      }

      @keyframes shimmer {
        100% {
          transform: translateX(100%);
        }
      }

      @media (max-width: 560px) {
        body {
          padding: 12px;
        }

        .hero {
          align-items: center;
          padding: 18px;
        }

        .avatar {
          width: 92px;
          height: 112px;
          border-radius: 22px;
        }

        .skeletonAvatar {
          width: 92px;
          height: 112px;
          border-radius: 22px;
        }

        .content {
          padding: 16px 18px 18px;
        }

        .grid {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <main id="root" class="card loading">
      <section class="hero">
        <div class="skeleton skeletonAvatar"></div>
        <div>
          <div class="skeleton skeletonPill"></div>
          <div class="skeleton skeletonName"></div>
          <div class="skeleton skeletonSubtitle"></div>
          <div class="chips">
            <div class="skeleton skeletonChip"></div>
            <div class="skeleton skeletonChip"></div>
            <div class="skeleton skeletonChip"></div>
          </div>
        </div>
      </section>
      <section class="content">
        <div class="grid">
          <section class="field skeletonField">
            <div class="skeleton skeletonLabel"></div>
            <div class="skeleton skeletonValue skeletonValueShort"></div>
          </section>
          <section class="field skeletonField">
            <div class="skeleton skeletonLabel"></div>
            <div class="skeleton skeletonValue"></div>
          </section>
          <section class="field skeletonField">
            <div class="skeleton skeletonLabel"></div>
            <div class="skeleton skeletonValue"></div>
          </section>
          <section class="field skeletonField">
            <div class="skeleton skeletonLabel"></div>
            <div class="skeleton skeletonValue"></div>
          </section>
          <section class="field wide skeletonField">
            <div class="skeleton skeletonLabel"></div>
            <div class="skeleton skeletonValue"></div>
            <div class="skeleton skeletonValue skeletonValueShort"></div>
          </section>
          <section class="field wide skeletonField">
            <div class="skeleton skeletonLabel"></div>
            <div class="skeleton skeletonValue"></div>
            <div class="skeleton skeletonValue"></div>
          </section>
        </div>
      </section>
    </main>

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

      function normalizeOutput(payload) {
        const value = payload || {};

        if (value.legislator) {
          return value;
        }

        if (value.structuredContent?.legislator) {
          return value.structuredContent;
        }

        if (value.toolOutput?.legislator) {
          return value.toolOutput;
        }

        if (value.toolOutput?.structuredContent?.legislator) {
          return value.toolOutput.structuredContent;
        }

        if (value.result?.structuredContent?.legislator) {
          return value.result.structuredContent;
        }

        if (value.result?.legislator) {
          return value.result;
        }

        return value.structuredContent || value.toolOutput || value;
      }

      function renderFromOutput(payload) {
        const output = normalizeOutput(payload);
        const legislator = output.legislator;
        const root = document.getElementById("root");

        if (!legislator || output.found === false) {
          return false;
        }

        const committees = splitItems(legislator.committee).slice(-3);
        const phones = splitItems(legislator.tel).slice(0, 3).join("\\n");
        const degree = splitItems(legislator.degree).slice(0, 3).join("\\n");
        const experience = splitItems(legislator.experience).slice(0, 4).join("\\n");
        const photo = legislator.imageUrl || "";
        const initials = String(legislator.name || "?").slice(0, 2);

        root.className = "card";
        root.innerHTML = `
          <section class="hero">
            ${
              photo
                ? `<img class="avatar" src="${escapeHtml(photo)}" alt="${escapeHtml(legislator.name)}照片" />`
                : `<div class="avatar avatarFallback">${escapeHtml(initials)}</div>`
            }
            <div>
              <div class="eyebrow">立法院委員資料卡</div>
              <h1 class="name">${escapeHtml(legislator.name)}</h1>
              <p class="subtitle">${escapeHtml(legislator.ename || "")}</p>
              <div class="chips">
                <span class="chip">${escapeHtml(legislator.party || "政黨未提供")}</span>
                <span class="chip">${escapeHtml(legislator.areaName || "選區未提供")}</span>
                <span class="chip">第 ${escapeHtml(legislator.term || "")} 屆</span>
              </div>
            </div>
          </section>
          <section class="content">
            <div class="grid">
              ${field("就任日期", legislator.onboardDate)}
              ${field("聯絡電話", phones)}
              ${field("近期委員會", committees.join("\\n"))}
              ${field("服務處地址", legislator.addr)}
              <div class="wide">${field("學歷", degree)}</div>
              <div class="wide">${field("經歷摘要", experience)}</div>
            </div>
          </section>
        `;
        return true;
      }

      function getToolInputName(payload) {
        return (
          payload?.toolInput?.name ||
          payload?.input?.name ||
          window.openai?.toolInput?.name ||
          "黃國昌"
        );
      }

      function renderEmpty(message) {
        const root = document.getElementById("root");
        root.className = "empty";
        root.textContent = message || "找不到可顯示的立委資料。";
      }

      async function hydrateWithToolCall(name) {
        if (typeof window.openai?.callTool !== "function") return false;

        try {
          const result = await window.openai.callTool("get_legislator_profile_data", { name });
          return renderFromOutput(result);
        } catch (error) {
          console.error("Unable to hydrate legislator card", error);
          return false;
        }
      }

      async function render(payload = {}) {
        const bootPayload = {
          toolOutput: window.openai?.toolOutput,
          toolResponseMetadata: window.openai?.toolResponseMetadata,
          toolInput: window.openai?.toolInput,
          ...payload,
        };

        if (renderFromOutput(bootPayload)) return;

        const name = getToolInputName(bootPayload);
        if (await hydrateWithToolCall(name)) return;

        renderEmpty(`找不到 ${name} 的可顯示委員資料。`);
      }

      render();
      window.addEventListener("openai:set_globals", (event) => {
        render(event.detail?.globals || event.detail || {});
      });

      window.addEventListener("message", (event) => {
        if (event.source !== window.parent) return;
        const message = event.data;
        if (!message || message.jsonrpc !== "2.0") return;
        if (message.method !== "ui/notifications/tool-result") return;

        const result = message.params || {};
        render(result);
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
        "openai/widgetDomain": "https://ly-mcp-server.onrender.com",
        "openai/widgetCSP": {
            "resource_domains": ["https://www.ly.gov.tw"],
        },
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


async def lookup_legislator_profile(name: str = "黃國昌") -> dict:
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
        "legislator": {
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
        },
    }


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
                types.TextContent(type="text", text=f"找不到{name}的立法委員資料。")
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
