import os

import requests
steam_api_url = "https://api.steampowered.com/IGameServersService/GetServerList/v1/"


def get_info_server(host, port):
    api_key = os.getenv("STEAM_API")
    return requests.get(f"{steam_api_url}?key={api_key}&filter=addr\\{host}:{port}")