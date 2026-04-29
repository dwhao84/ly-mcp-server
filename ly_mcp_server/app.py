from fastmcp import FastMCP

from ly_mcp_server.config import SERVER_NAME
from ly_mcp_server.tools import register_tools
from ly_mcp_server.widgets.legislator_card import register_legislator_card_resource


def create_app() -> FastMCP:
    mcp = FastMCP(SERVER_NAME)
    register_legislator_card_resource(mcp)
    register_tools(mcp)
    return mcp


mcp = create_app()
