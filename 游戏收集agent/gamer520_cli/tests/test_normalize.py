from gamer520_cli.normalize import (
    extract_link_id,
    is_url_valid,
    normalize_title_for_search,
    normalize_title_key,
    normalize_url,
)


def test_normalize_url_lowercases_domain():
    assert normalize_url("https://GAMER520.com/114951.html") == "https://gamer520.com/114951.html"


def test_normalize_url_removes_query():
    assert (
        normalize_url("https://www.gamer520.com/114951.html?foo=bar")
        == "https://www.gamer520.com/114951.html"
    )


def test_normalize_url_removes_fragment():
    assert (
        normalize_url("https://www.gamer520.com/114951.html#section")
        == "https://www.gamer520.com/114951.html"
    )


def test_normalize_url_removes_trailing_slash():
    assert (
        normalize_url("https://www.gamer520.com/114951.html/")
        == "https://www.gamer520.com/114951.html"
    )


def test_normalize_url_upgrades_http():
    assert (
        normalize_url("http://www.gamer520.com/114951.html")
        == "https://www.gamer520.com/114951.html"
    )


def test_extract_link_id():
    assert extract_link_id("https://www.gamer520.com/114951.html") == 114951
    assert extract_link_id("https://www.gamer520.com/100001.html") == 100001


def test_extract_link_id_none():
    assert extract_link_id("https://example.com/page.html") is None


def test_is_url_valid():
    assert is_url_valid("https://www.gamer520.com/114951.html") is True
    assert is_url_valid("https://example.com/page.html") is True


def test_is_url_valid_empty():
    assert is_url_valid("") is False


def test_normalize_title_key_lowercase_and_strip():
    result = normalize_title_key("  Hello World  ")
    assert result == "helloworld"


def test_normalize_title_key_removes_punctuation():
    result = normalize_title_key("Hello, World!")
    assert result == "helloworld"


def test_normalize_title_key_keeps_version_suffix():
    result = normalize_title_key("Game Name 豪华版")
    assert "豪华版" in result
    assert "gamename" in result


def test_normalize_title_for_search_removes_version_suffix():
    result = normalize_title_for_search("Game Name 豪华版")
    assert result == "gamenameluxuryedition" or result == "gamename"


def test_normalize_title_for_search_removes_version_number():
    result = normalize_title_for_search("RPG Maker v1.2.3")
    assert "rp" in result and "maker" in result and "123" not in result


def test_normalize_title_for_search_handles_chinese():
    result = normalize_title_for_search("《仁王 3》 Nioh 3")
    assert "仁王" in result or "ni" in result
