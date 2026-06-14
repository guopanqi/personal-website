"""
Public scraping API and URL-to-scraper dispatch router.

To add a new site:
  1. Create scraper_<sitename>.py with scrape_list() and scrape_detail()
  2. Register the domain in _SCRAPERS below

Return shapes:
  scrape_list  -> list of {"title": str, "url": str, "date_text": str}
  scrape_detail -> {"title": str, "release_date": str, "genres": str, "description": str}
"""
from urllib.parse import urlparse

from . import scraper_gamer520

# domain fragment -> scraper module
_SCRAPERS = {
    "gamer520.com": scraper_gamer520,
}


def _get_scraper(url: str):
    netloc = urlparse(url).netloc.lower().removeprefix("www.")
    for domain, module in _SCRAPERS.items():
        if domain in netloc:
            return module
    supported = ", ".join(_SCRAPERS)
    raise ValueError(f"No scraper for '{netloc}'. Supported: {supported}")


def scrape_list(url: str) -> list[dict]:
    """Fetch a game list page; return [{title, url, date_text}, ...]."""
    return _get_scraper(url).scrape_list(url)


def scrape_detail(url: str) -> dict:
    """Fetch a game detail page; return {title, release_date, genres, description}."""
    return _get_scraper(url).scrape_detail(url)
