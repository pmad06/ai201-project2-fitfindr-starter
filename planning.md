# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool searches through the listings.json database for items that match the user's description of items they are looking for, the size, and price range. It also sorts the matching listings by relevance to make sure they match the query accurately. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): This parameter describes what the user is looking for in the listings. 
- `size` (str): This parameter describes the specific size the user is looking for. If this parameter is not specified, then it is assigned to 'None' which skips size filtering. 
- `max_price` (float): This parameter describes the maximum price the user wants their listing to be. If the max price is not specified, it is assigned to 'None' to skip price filerting. 

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
This tool results a list of matching listings based on the description, size, and max price. The fields that the result contains include id, title, description, category, style_tags, size, condition, price, colors, brand, and platform. An empty list is returned if the user query did not match with any available listings. 

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
If the tool returns nothing, FitFindr should respond to the user by letting them know which field did not match and ask them to try different options and stops the session. 

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool takes the output from search_listings, which is going to be a thrifted clothing item from the listings database, and the user's wardrobe to suggest 1-2 complete outfits. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): This parameter is the item that the user selected from possible listings and want to buy because it fits their description of clothing, size, and max price. 
- `wardrobe` (dict): This parameter represents the user's wardrobe and their style to be able to come with the right suggestion for an outfit. This parameter could also be empty. 

**What it returns:**
<!-- Describe the return value -->
This tool returns a non-empty string with outfit suggestions based on the parameters. 

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If the wardrobe parameter is empty, it offers suggestions for the outfit based on the new_item parameter instead of making assumptions or return an empty string.  

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool generates a caption about the thrifted item the user found from the various listings and allows the caption to be shared. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (string): This parameter represents the string returned from the suggest_outfit() function.
- `new_item` (dict): This parameter represents the listing dict for the thrifted item selected from the search_listings() function.


**What it returns:**
<!-- Describe the return value -->
This tool returns a 2-4 sentence that can be used as a caption for social media. 


**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If the output is empty or missing, then an error message is returned instead. 
---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
With given the user query, the agent identifies the item the user is searching for, the size they're looking for, and user's wardrobe, so what they currently wear. Then, the agent calls search_listings with those inputs from the query to return the available listings with those categories. After getting the result from search_listings, the agent checks to make sure that the results list is not empty. But if it is, then the agent sends an error message in the session telling the user to change their inputs and returns early without calling the other tools. But if the results list is not empty, the agent selects the most relevant match and calls the suggest_outfit tool with that input and the user's wardrobe context. After getting the result from suggest_outfit, the agents checks whether the result is empty or not and if it empty, then the agent displays the listing information with generic styling advice. But if a result is returned, then the agent sets outfit_suggestion to the result of that tool and calls the next tool, which is create_fit_card with the suggestion and selected item and runs that tool. Once create_fit_card finishes running, the agent displays the output to the user and the loop ends. That is the last loop called. 
---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
The session that the agent maintains is updated after each tool is called and passed into the next one. So the data that is tracked is the following three values: the item selected from search_listings, with the highest relevance, the suggested outfit from the tool suggest_outfit, and the fit_card from the tool create_fit_card. 

After search_listings is ran, the agent updates the session by adding the item with the highest relevance. This listing consists of the item's title, description, condition, price, etc. Then, after suggest_outfit is ran, the agent updates the session by adding the suggested outfit, which is a string returned by the tool. Lastly, after create_fit_card is ran, the agent updates the session by adding the shareable caption returned from the tool. So, the agent ensures that the tools return something before moving on to the next tool since they depend on the results from the prior tools. 
---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | An empty list, and asks the user to change their preferences in order to find a better match. |
| suggest_outfit | Wardrobe is empty | The agent offers general styling advice for the item thrifted, rather than user. |
| create_fit_card | Outfit input is missing or incomplete | The agent responds with an error message string. |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

User query
    │
    V
Planning Loop
    │
    ├─> search_listings(query, size, max_price)
    │       │
    │       ├── results=[] ──> "No listings found. Try adjusting your
    │       │                   price limit or rewording your search." ──► STOP
    │       │
    │       └── results=[item, ...] ──> Session: selected_item = results[0]
    │                                                       │
    ├─> suggest_outfit(selected_item, wardrobe) <───────────┘
    │       │
    │       ├── failed/empty ──> skip to create_fit_card with no styling advice
    │       │
    │       └── success ──> Session: outfit_suggestion = "..."
    │                                           │
    └─> create_fit_card(outfit_suggestion, selected_item) ◄─┘
            │
            └── Session: fit_card = "..."
                            │
                            V
                    Display to user -> End
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**
To implement the tools in Milestone 3, I will use Claude and instead of finishing all tools at once, I will give the AI the tool specs one at a time from planning.md, which includes the parameters, return value, and what to do in the case of an error/failure, and ask it to implement that single function and then move on to the next function after I verify that there no errors with its implementations. 

For search_listings, I will verify that there are no errors by running it against multiple queries, one of them being where I expect a result and a few where I expect there to be no result returned, so changing my parameters so that they do not exist in the listings.json() file. For suggest_outfit, I would need to ask Claude to implement the LLM with the right model and verify that it works with an empty wardrobe to make its returning the right result. For create_fit_card, I will give Claude the specs and ask it to implement the tool. To verify that the tool works, I will have to run the tool a few times to make sure I'm getting various different captions for different items. 

**Milestone 4 — Planning loop and state management:**
To complete this milestone, I will give claude the architecture diagram from planning.md along with the planning loop sections. I will ask the AI to implement the functions in agent.py by giving it the right conditional logic and ensure that it knows other tools depend on the results on the tool before it in order to run successfully. To verify, I would need to check if the right results are stored in the session and passed in later after the tool is done running. 
---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The agent first searches through the listing to find whether the types of clothes mentioned by the user are available. To do this, the tool: "search_listings" is called with the input, "vintage graphic tee", the size variable, which is None since size isn't specified in the user query, and max_price, which is equal to 30.0.  FitFindr is going to find vintage graphic tees under $30 and display all of the possible results that match the inputs. 

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
From step 1, a variety of vintage graphic tees under $30 are returned, which are then passed into the tool: "suggest_outfit". The inputs for this tool include the items returned from step 1 and the user's wardrobe mentioned from the user query, which are baggy jeans and chunky sneakers. 

**Step 3:**
<!-- Continue until the full interaction is complete -->
The interaction is completed when the tool: "create_fit_card" is called. The inputs for this tool include the output returned from step 2, the suggested output, and the new item returned from step 1 that matched the user query. 


**Final output to user:**
<!-- What does the user actually see at the end? -->
At the end of the session, the user sees the output from step 3. The output includes the new item from the listings, how the user can integrate that item with their wardrobe, and the fit card consisting of where the items were bought from and how much. 