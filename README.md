# FitFindr — Starter Kit

A thrift shopping agent that searches through available listings, suggests outfits, and generates a short and shareable fit card, from a single query. 

## What It Does

The user types a query describing the type of clothing they're looking for, their max price, size and their current wardrobe. 
The agent then: 
1. Parses the query for certain keywords, size, and price
2. Searches the listings for most relevant matches
3. Suggests 1-2 outfits using the most relevant match and the description of the user's wardrobe
4. Generates a fit card, that can shared through social media as a caption, for the outfit 

## Tool Inventory

### search_listings(description: str, size: str | None, max_price: float | None) -> list[dict]
This tool searches through the listings dataset by comparing the description with the title, description, category, style_tags, colors and brand. This tool also filters by size and max_price, if they are provided by the user in their query. Lastly, it returns results sorted by relevance to the user's query or an empty list if the user's description, size, or price did not match with the dataset. 

### suggest_outfit(new_item: dict, wardrobe: dict) -> str
This tool calls the Groq LLM to suggest around 1-2 outfits based on the most relevant item returned from the search_listings tool and the user's wardrobe. If the user's wardrobe is not provided in the query, this tool returns general styling advice instead of being very specific. 

### create_fit_card(outfit: str, new_item: dict) -> str
This tool calls the Groq LLM at temperature=0.9 to generate a caption, that can be used in social media posts, about the item thrifted, such as its name, price, and platform. If the outfit is empty, an error is returned from this tool instead. 

## Planning Loop 

The agent runs a linear planning loop with one branch: 
1. Parse the query to extract description, size, and max_price from the user's query
2. Call search_listings(), if result is empty, return early with an error message and stop the session
3. Select the most relevant match as the item to work with
4. Call suggest_outfit() with the item from step 3 and user's wardrobe
5. Call create_fit_card() with the suggested outfit and thrifted item
6. Return completed session dict

After search_listings is called, if no results are found, suggest_outfit and create_fit_card are never called. 

## State Management 

At the start of each run, all values are stored in a session dict in the following way: 

1. session["parsed"] = extracted description, size, and max_price
2. session["search_results"] = list of matching listings 
3. session["selected_item"] = most relevant match, passed into suggest_outfit
4. session["outfit_suggestion"] = output from the LLM, passed into create_fit_card
5. session["fit_card"] = final caption to be shared
6. session["error"] = early end of session if something fails, no effect if everything is successful 

## Error Handling 

|      Tool       |    Failure Mode   |        Response
| search_listings |    no matches     | returns [] and agent gets session["error"] and ends early
| suggest_outfit  |    empty wardrobe | returns general styling advice 
| create_fit_card |    empty outfit string | return descriptive error string instead of caption

## Spec Reflection 

A few things that I implemented differently from planning.md include how I handled the empty wardrobe case in the suggest_outfit tool. I mentioned that suggest_outfit would be skipped entirely if the user's wardrobe was not provided but the actual implementation included returning general styling advice from the LLM instead. My planning.md spec also included the step of check whether suggest_outfit returned empty before calling the next tool, create_fit_card. However, in the actual implementation the actual check wasn't needed. 

## AI Usage 

### Tool implementation (tools.py)
To implement each tool, I gave Claude the function stub, a spec block with the required inputs, return value, and failure mode. I made sure that Claude implemented one tool at a time so I could test that each tool was working individually before testing all 3 at once. The generated code for search_listings was correct but I had to ask the AI to generate the code for _get_groq_client() because the helper function was dropped, so I ran into a "name not defined" error in suggest_outfit and create_fit_card. I was able to figure out this error by adding debugging statements in the tools and examine what exactly was causing the tools not to function properly. 

### Planning loop (agent.py)
To implement agent.py, I gave Claude the session dict structure, the 7 TODO steps from agent.py and the architecture diagram from planning.md. The generated code was correct, but I was missing 'import re' at the top of agent.py, which gave me an error when trying to run the tests. But after fixing that error, all of the tests ran properly and I was able to test a few prompts in the FitFindr after running app.py.

