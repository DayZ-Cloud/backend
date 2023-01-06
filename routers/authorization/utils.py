def generate_recent_url(data: dict) -> str:
    return f"https://hotlinetrade.страж.shop/api/v1/recent/{data['token']}/{data['key']}/"