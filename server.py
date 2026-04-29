import os

from ly_mcp_server.app import mcp
from ly_mcp_server.config import (
    DEFAULT_PORT,
    SERVER_HOST,
    SERVER_PATH,
    SERVER_TRANSPORT,
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", str(DEFAULT_PORT)))
    mcp.run(
        transport=SERVER_TRANSPORT,
        host=SERVER_HOST,
        port=port,
        path=SERVER_PATH,
    )
