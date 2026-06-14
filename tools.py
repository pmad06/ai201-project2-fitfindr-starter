"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    # Load all listings with load_listings() — already imported from utils.data_loader
    # Filter by max_price (inclusive) if provided
    # Filter by size if provided — case-insensitive, partial match 
    #   (e.g., "M" should match a listing sized "S/M")
    # Score each remaining listing by keyword overlap with `description`:
    #   - Tokenize description into lowercase words
    #   - Check each word against: title, description, category, style_tags, colors, brand
    #   - Score = number of matching keywords found across those fields
    # Drop listings with score == 0
    # Sort by score descending
    # Return the list of matching listing dicts (empty list if none match — no exceptions)
    try:
        listings = load_listings()

        # Filter by max_price
        if max_price is not None:
            listings = [l for l in listings if l.get("price", 0) <= max_price]

        # Filter by size (case-insensitive, partial match)
        if size is not None:
            size_lower = size.lower()
            listings = [
                l for l in listings
                if size_lower in (l.get("size") or "").lower()
            ]

        # Tokenize description into lowercase words
        keywords = set(description.lower().split())

        def score_listing(listing):
            # Collect all searchable text from relevant fields
            searchable_parts = [
                listing.get("title") or "",
                listing.get("description") or "",
                listing.get("category") or "",
                listing.get("brand") or "",
            ]
            # Flatten list fields
            searchable_parts += listing.get("style_tags") or []
            searchable_parts += listing.get("colors") or []

            # Build a single set of lowercase words from all fields
            field_words = set()
            for part in searchable_parts:
                field_words.update(part.lower().split())

            return len(keywords & field_words)

        # Score, drop zeros, sort descending
        scored = [(score_listing(l), l) for l in listings]
        scored = [(s, l) for s, l in scored if s > 0]
        scored.sort(key=lambda x: x[0], reverse=True)

        return [l for _, l in scored]

    except Exception:
        return []


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    # Check whether wardrobe['items'] is empty
    # If empty: call the LLM asking for general styling advice for the new item
    #   (what kinds of pieces pair well, what vibe it suits, etc.)
    # If not empty: format the wardrobe items into a readable list and ask
    #   the LLM to suggest 1-2 specific outfit combinations using the new item
    #   and named pieces from the wardrobe
    # Return the LLM's response as a string — never return empty string
    try:
        client = _get_groq_client()

        item_summary = (
            f"'{new_item.get('title', 'Unknown item')}' "
            f"({new_item.get('category', 'unknown category')}, "
            f"{', '.join(new_item.get('colors', [])) or 'unknown color'}, "
            f"style: {', '.join(new_item.get('style_tags', [])) or 'unspecified'})"
        )

        wardrobe_items = (wardrobe or {}).get("items") or []

        if not wardrobe_items:
            prompt = (
                f"I just found this thrifted piece: {item_summary}.\n\n"
                "I don't have my wardrobe catalogued yet. Please give me general "
                "styling advice for this item: what kinds of pieces pair well with it, "
                "what occasions or vibes it suits, and any tips for wearing it."
            )
        else:
            wardrobe_lines = "\n".join(
                f"- {item.get('name', 'Unnamed')} "
                f"({item.get('category', '?')}, {item.get('color', '?')}, "
                f"{item.get('style', '?')} style)"
                for item in wardrobe_items
            )
            prompt = (
                f"I just found this thrifted piece: {item_summary}.\n\n"
                f"Here is my current wardrobe:\n{wardrobe_lines}\n\n"
                "Please suggest 1-2 specific outfit combinations using the new item "
                "alongside named pieces from my wardrobe. Be concrete and mention "
                "the exact items by name."
            )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a personal stylist specializing in thrifted and "
                        "secondhand fashion. Give practical, specific outfit advice "
                        "in a friendly, concise tone."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        text = response.choices[0].message.content or ""
        return text if text.strip() else "This piece has great potential — try pairing it with classic basics in complementary colors to let it shine."

    except Exception:
        return "Unable to generate styling suggestions right now. Try pairing this piece with neutrals or items in a complementary color for a balanced look."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────
def create_fit_card(outfit: str, new_item: dict) -> str:
    # Guard against empty or whitespace-only outfit string — return an error message string
    # Build a prompt giving the LLM the item details and outfit suggestion
    # Ask for a 2-4 sentence Instagram/TikTok caption that:
    #   - Feels casual and authentic (like a real OOTD post)
    #   - Mentions item name, price, and platform naturally (once each)
    #   - Captures the outfit vibe in specific terms
    # Call the LLM with temperature=0.9 and return the response as a string
    if not outfit or not outfit.strip():
        return "Error: outfit description is empty — please provide a styled outfit before generating a fit card."

    try:
        client = _get_groq_client()

        title    = new_item.get("title", "this piece")
        price    = new_item.get("price")
        platform = new_item.get("platform", "a thrift platform")
        colors   = ", ".join(new_item.get("colors", [])) or "unique"
        tags     = ", ".join(new_item.get("style_tags", [])) or "effortless"
        brand    = new_item.get("brand")

        price_str    = f"${price:.2f}" if isinstance(price, (int, float)) else "a steal"
        brand_clause = f"It's {brand}, " if brand else ""

        prompt = (
            f"I'm putting together an OOTD post and need a caption.\n\n"
            f"The new thrifted item: '{title}' — {colors} colors, {tags} vibes. "
            f"{brand_clause}found on {platform} for {price_str}.\n\n"
            f"The full outfit: {outfit.strip()}\n\n"
            "Write a 2-4 sentence Instagram/TikTok caption for this fit. "
            "Requirements:\n"
            "- Casual and authentic, like a real person's OOTD post (not an ad)\n"
            "- Mention the item name, price, and platform naturally — each exactly once\n"
            "- Be specific about the vibe this outfit gives off\n"
            "- No hashtags, no emojis, no asterisks — just the caption text"
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.9,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write short, authentic social media captions for thrift "
                        "fashion finds. Your tone is relaxed and genuine — like a "
                        "real person sharing their outfit, not a brand account. "
                        "Never use hashtags, emojis, or markdown formatting."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        text = response.choices[0].message.content or ""
        return text.strip() if text.strip() else "Couldn't generate a caption this time — try again for a fresh take."

    except Exception as e:
        print(f"ERROR: {e}")
        return "Error: caption generation failed. Check your connection and try again."