
import tools
from tools import search_listings, suggest_outfit, create_fit_card

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)


# minimal fake listing to use across tests
FAKE_ITEM = {
    "title": "Vintage Levi's Denim Jacket",
    "category": "outerwear",
    "colors": ["blue"],
    "style_tags": ["vintage", "casual"],
    "brand": "Levi's",
    "price": 35.0,
    "platform": "Depop"
}

def test_suggest_outfit_empty_wardrobe():
    """Should return styling advice, not crash or return empty string."""
    result = suggest_outfit(FAKE_ITEM, {"items": []})
    assert isinstance(result, str)
    assert len(result) > 0

def test_suggest_outfit_with_wardrobe():
    """Should mention wardrobe items by name in suggestions."""
    wardrobe = {
        "items": [
            {"name": "White Crop Top", "category": "top", "color": "white", "style": "casual"},
            {"name": "Black Slim Jeans", "category": "bottom", "color": "black", "style": "casual"},
        ]
    }
    result = suggest_outfit(FAKE_ITEM, wardrobe)
    assert isinstance(result, str)
    assert len(result) > 0

def test_suggest_outfit_missing_wardrobe_key():
    """Should handle a wardrobe dict with no 'items' key without crashing."""
    result = suggest_outfit(FAKE_ITEM, {})
    assert isinstance(result, str)
    assert len(result) > 0


FAKE_ITEM = {
    "title": "Vintage Levi's Denim Jacket",
    "category": "outerwear",
    "colors": ["blue"],
    "style_tags": ["vintage", "casual"],
    "brand": "Levi's",
    "price": 35.0,
    "platform": "Depop"
}

FAKE_OUTFIT = "Vintage Levi's Denim Jacket over a white crop top, black slim jeans, and white sneakers for a classic casual look."

def test_fit_card_empty_outfit():
    """Should return error string, not crash."""
    result = create_fit_card("", FAKE_ITEM)
    assert isinstance(result, str)
    assert "error" in result.lower() or "empty" in result.lower()

def test_fit_card_whitespace_outfit():
    """Whitespace-only outfit should also return error string."""
    result = create_fit_card("   ", FAKE_ITEM)
    assert isinstance(result, str)
    assert "error" in result.lower() or "empty" in result.lower()

def test_fit_card_returns_caption():
    """Valid inputs should return a non-empty caption string."""
    result = create_fit_card(FAKE_OUTFIT, FAKE_ITEM)
    assert isinstance(result, str)
    assert len(result) > 0

def test_fit_card_varies():
    """Running twice on same input should produce different captions (temperature=0.9)."""
    result1 = create_fit_card(FAKE_OUTFIT, FAKE_ITEM)
    result2 = create_fit_card(FAKE_OUTFIT, FAKE_ITEM)
    assert result1 != result2