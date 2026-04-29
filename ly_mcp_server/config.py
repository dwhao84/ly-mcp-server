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

SERVER_NAME = "立法院 Open Data MCP"
SERVER_HOST = "0.0.0.0"
SERVER_PATH = "/mcp"
SERVER_TRANSPORT = "streamable-http"
DEFAULT_PORT = 8000

CARD_TEMPLATE_URI = "ui://widget/legislator-card-v4.html"
LEGACY_CARD_TEMPLATE_URI = "ui://widget/legislator-card-v3.html"
CARD_MIME_TYPE = "text/html+skybridge"
WIDGET_DOMAIN = "https://ly-mcp-server.onrender.com"
