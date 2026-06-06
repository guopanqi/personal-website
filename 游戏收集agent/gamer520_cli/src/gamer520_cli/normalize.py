import re
from urllib.parse import urlparse, urlunparse

ID_PATTERN = re.compile(r"/(\d+)\.html$", re.IGNORECASE)

VERSION_SUFFIXES = [
    "正式版",
    "支持者版",
    "豪华版",
    "数字豪华版",
    "传奇版",
    "先锋版",
    "终极版",
    "完整版",
    "典藏版",
    r"v\d+(?:\.\d+)*",
]


def normalize_url(url: str) -> str:
    url = url.strip()
    parsed = urlparse(url)
    scheme = "https"
    hostname = parsed.hostname.lower() if parsed.hostname else ""
    path = parsed.path.rstrip("/")
    query = ""
    fragment = ""
    result = urlunparse((scheme, hostname, path, parsed.params, query, fragment))
    return result


def extract_link_id(url: str) -> int | None:
    url = normalize_url(url)
    m = ID_PATTERN.search(url)
    if m:
        return int(m.group(1))
    return None


def is_url_valid(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc)
    except Exception:
        return False


def _strip_punctuation(title: str) -> str:
    return re.sub(
        r"[\u3000-\u303f\uff00-\uffef\[\]()（）,，.。!！?？:：;；、]+",
        "",
        title,
    )


def normalize_title_key(title: str) -> str:
    title = title.lower().strip()
    title = _strip_punctuation(title)
    title = re.sub(r"\s+", "", title)
    return title


def normalize_title_for_search(title: str) -> str:
    title = title.lower().strip()
    title = _strip_punctuation(title)
    for suffix in VERSION_SUFFIXES:
        title = re.sub(suffix, "", title)
    title = re.sub(r"\s+", "", title)
    return title
