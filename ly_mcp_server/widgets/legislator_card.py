from importlib import resources

from ly_mcp_server.config import (
    CARD_MIME_TYPE,
    CARD_TEMPLATE_URI,
    LEGACY_CARD_TEMPLATE_URI,
    PARTY_LIST_TEMPLATE_URI,
    WIDGET_DOMAIN,
)

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

CARD_RESOURCE_META = {
    "openai/widgetDescription": "顯示立法委員照片、政黨、選區、委員會、聯絡方式與簡歷的資料卡。",
    "openai/widgetPrefersBorder": True,
    "openai/widgetDomain": WIDGET_DOMAIN,
    "openai/widgetCSP": {
        "resource_domains": ["https://www.ly.gov.tw"],
    },
    "ui": {
        "prefersBorder": True,
        "domain": WIDGET_DOMAIN,
        "csp": {
            "connectDomains": [],
            "resourceDomains": ["https://www.ly.gov.tw"],
        },
    },
}

PARTY_LIST_TOOL_META = {
    "openai/outputTemplate": PARTY_LIST_TEMPLATE_URI,
    "openai/toolInvocation/invoking": "查詢政黨立委名單中...",
    "openai/toolInvocation/invoked": "政黨立委名單已載入",
    "openai/widgetAccessible": True,
    "openai/resultCanProduceWidget": True,
    "ui": {
        "resourceUri": PARTY_LIST_TEMPLATE_URI,
        "visibility": ["model", "app"],
    },
}

PARTY_LIST_RESOURCE_META = {
    "openai/widgetDescription": "依政黨以卡片顯示每位立法委員的照片、政黨、選區、委員會、聯絡方式、學歷與經歷檔案資料。",
    "openai/widgetPrefersBorder": True,
    "openai/widgetDomain": WIDGET_DOMAIN,
    "openai/widgetCSP": {
        "resource_domains": ["https://www.ly.gov.tw"],
    },
    "ui": {
        "prefersBorder": True,
        "domain": WIDGET_DOMAIN,
        "csp": {
            "connectDomains": [],
            "resourceDomains": ["https://www.ly.gov.tw"],
        },
    },
}


def create_legislator_card_html() -> str:
    return (
        resources.files(__package__)
        .joinpath("legislator_card.html")
        .read_text(encoding="utf-8")
        .strip()
    )


def create_party_list_html() -> str:
    return (
        resources.files(__package__)
        .joinpath("legislator_party_list.html")
        .read_text(encoding="utf-8")
        .strip()
    )


def register_legislator_card_resource(mcp) -> None:
    @mcp.resource(
        LEGACY_CARD_TEMPLATE_URI,
        name="立委資料卡片",
        mime_type=CARD_MIME_TYPE,
        meta=CARD_RESOURCE_META,
    )
    @mcp.resource(
        CARD_TEMPLATE_URI,
        name="立委資料卡片",
        mime_type=CARD_MIME_TYPE,
        meta=CARD_RESOURCE_META,
    )
    async def legislator_card_template() -> str:
        return create_legislator_card_html()

    @mcp.resource(
        PARTY_LIST_TEMPLATE_URI,
        name="政黨立委名單",
        mime_type=CARD_MIME_TYPE,
        meta=PARTY_LIST_RESOURCE_META,
    )
    async def legislator_party_list_template() -> str:
        return create_party_list_html()
