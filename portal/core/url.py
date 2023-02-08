from urllib.parse import urlsplit


def prepare_url(params: str, redirect_url: str) -> str:
    """Add params to redirect url."""
    split_url = urlsplit(redirect_url)
    current_params = split_url.query
    if current_params:
        params = f"{current_params}&{params}"
    split_url = split_url._replace(query=params)
    return split_url.geturl()
