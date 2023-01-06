from _socket import gaierror

from fastapi import HTTPException
from steam import game_servers as gs


async def check_server_exists(ip_address: str, query_port: int):
    try:
        gs.a2s_info((ip_address, query_port))
    except (TimeoutError, ConnectionRefusedError, gaierror):
        raise HTTPException(status_code=400, detail="Server not found or steam services not answer.")