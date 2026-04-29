# 立法院 Open Data MCP Server

這是一個使用 FastMCP 建立的立法院 Open Data MCP server。服務目前提供立法院開放資料查詢，以及立法委員資料卡 widget。

## 專案結構

```text
.
├── Procfile
├── requirements.txt
├── server.py
└── ly_mcp_server/
    ├── app.py
    ├── config.py
    ├── legislators.py
    ├── ly_client.py
    ├── tools.py
    └── widgets/
        ├── legislator_card.html
        └── legislator_card.py
```

- `server.py`：部署入口，讀取 `PORT` 後啟動 MCP server。
- `ly_mcp_server/app.py`：建立 `FastMCP` instance，集中註冊 tools 與 resources。
- `ly_mcp_server/config.py`：集中管理立法院 API、server、widget URI 與 domain 設定。
- `ly_mcp_server/ly_client.py`：處理立法院 Open Data API 請求與 SSL context。
- `ly_mcp_server/legislators.py`：處理立委資料查找與回傳資料正規化。
- `ly_mcp_server/tools.py`：定義並註冊 MCP tools。
- `ly_mcp_server/widgets/`：放置 widget resource 的 Python 註冊邏輯與 HTML/CSS/JS。

## 本機啟動

建議使用虛擬環境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

預設會啟動在：

```text
http://0.0.0.0:8000/mcp
```

也可以指定 port：

```bash
PORT=8123 python server.py
```

## 目前 MCP Tools

### `search_legislature_dataset`

查詢立法院開放資料 API。

參數：

- `dataset_id`：資料集 ID，預設 `"9"`。
- `page`：頁碼，預設 `1`。
- `select_term`：屆期條件，預設 `"all"`。

### `get_legislator_profile_data`

提供 widget 讀取指定立法委員的結構化資料。

參數：

- `name`：立法委員姓名，預設 `"黃國昌"`。

### `get_legislator_profile`

查詢指定立法委員基本資料，並回傳可觸發資料卡 widget 的 MCP tool result。

參數：

- `name`：立法委員姓名，預設 `"黃國昌"`。

## Widget Resource

目前資料卡 template URI：

```text
ui://widget/legislator-card-v5.html
```

legacy URI 仍保留：

```text
ui://widget/legislator-card-v3.html
```

Widget HTML 在 `ly_mcp_server/widgets/legislator_card.html`，metadata 與 resource 註冊在 `ly_mcp_server/widgets/legislator_card.py`。

## 如何延伸

### 新增一個立法院資料集查詢 tool

1. 先確認立法院 Open Data 的資料集 ID 與查詢參數。
2. 若只是原始資料查詢，可以直接在 `ly_mcp_server/tools.py` 新增 tool，呼叫 `fetch_legislature_dataset()`。
3. 若需要整理資料格式，建議在獨立 domain module 實作轉換邏輯，例如 `bills.py`、`committees.py`，再由 `tools.py` 呼叫。
4. 保持 tool 回傳結構穩定，避免 widget 或 MCP client 需要同時調整。

範例方向：

```python
@mcp.tool()
async def search_some_dataset(page: int = 1) -> dict:
    return await fetch_legislature_dataset(
        dataset_id="DATASET_ID",
        page=page,
        select_term="all",
    )
```

### 新增一個 domain service

當資料需要查找、過濾、欄位正規化或組合多個 API response 時，不建議把邏輯直接寫在 `tools.py`。

建議做法：

- 在 `ly_mcp_server/` 下新增 domain module，例如 `bills.py`。
- 在 module 裡提供語意清楚的函式，例如 `lookup_bill()` 或 `search_bills()`。
- `tools.py` 只負責 MCP tool 參數、呼叫 domain function、包裝 MCP result。

### 新增一個 widget

1. 在 `ly_mcp_server/widgets/` 新增 HTML 檔，例如 `bill_card.html`。
2. 新增對應 Python module，例如 `bill_card.py`。
3. 在 Python module 裡定義 template URI、resource meta、tool meta 與 `register_*_resource(mcp)`。
4. 在 `ly_mcp_server/app.py` 呼叫新的 resource 註冊函式。
5. 在 `tools.py` 新增帶有 `meta={...}` 的 tool，讓 tool result 能對應到 widget。

### 調整部署設定

部署入口目前維持 `python server.py`，`Procfile` 不需要更動。

若要改 path、host、transport 或預設 port，優先修改 `ly_mcp_server/config.py`，不要分散在各檔案中。

## 驗證建議

基本驗證：

```bash
python -m compileall server.py ly_mcp_server
python - <<'PY'
import asyncio
from ly_mcp_server.app import mcp

async def main():
    for name in [
        "search_legislature_dataset",
        "get_legislator_profile_data",
        "get_legislator_profile",
    ]:
        tool = await mcp.get_tool(name)
        assert tool.name == name
    print("ok")

asyncio.run(main())
PY
```

啟動檢查：

```bash
PORT=8123 python server.py
```

`streamable-http` MCP endpoint 需要符合 MCP client 的 headers 與 protocol。直接用瀏覽器或一般 `curl` 打 `/mcp` 可能會看到 `Not Acceptable: Client must accept text/event-stream`，這代表 server 有回應，但呼叫方式不是完整 MCP client request。
