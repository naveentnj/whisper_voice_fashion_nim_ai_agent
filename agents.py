import os
import json
import sys
import uuid
import asyncio
from typing import Dict, List, Any
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

# Load environment
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

# Set NVIDIA API key for LiteLLM
os.environ["NVIDIA_API_KEY"] = os.getenv("NVIDIA_NIM_API_KEY", "")

# Load product data once
PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "products.json")
try:
    with open(PRODUCTS_FILE, "r") as f:
        PRODUCTS_CATALOG = json.load(f)
except Exception as e:
    print(f"Error loading products catalog in agents.py: {e}")
    PRODUCTS_CATALOG = []

# Shared state during a single run
_active_cart: Dict[str, int] = {}
_action_log: List[str] = []

def get_product_by_id(product_id: str) -> Dict[str, Any]:
    for p in PRODUCTS_CATALOG:
        if p["id"].lower() == product_id.lower() or p["name"].lower() == product_id.lower():
            return p
    return {}

# -------------------------------------------------------------
# CrewAI Custom Tools
# -------------------------------------------------------------

@tool("Search Fashion Catalog")
def search_fashion_catalog(query: str = "", category: str = "", max_price: float = 10000.0) -> str:
    """
    Search the fashion store's product database.
    Inputs:
    - query: Optional keywords to search in product names or descriptions (e.g. 'linen', 'leather', 'chronograph').
    - category: Optional category filter. Available: shirt, watch, pant, shoes, jacket, bag, hat, sunglasses, belt, socks.
    - max_price: Optional maximum price filter.
    Returns a formatted string listing matching products, their pricing, ID, description, and stock level.
    """
    results = []
    
    # Query MongoDB database first
    try:
        from database import get_products_from_mongo, ping_db
        if ping_db()["status"] == "connected":
            results = get_products_from_mongo(category=category, query=query, max_price=max_price)
            print(f"[Agent Tool] Successfully queried {len(results)} products from MongoDB")
    except Exception as db_err:
        print(f"[Agent Tool] MongoDB search skipped or failed, using JSON fallback: {db_err}")

    # Fallback to local products.json if MongoDB query yielded no results
    if not results:
        q = query.lower()
        cat = category.lower().strip()
        for p in PRODUCTS_CATALOG:
            match_cat = not cat or p["category"].lower() == cat
            match_price = p["price"] <= max_price
            match_query = True
            if q:
                match_query = (q in p["name"].lower() or 
                               q in p["description"].lower() or 
                               q in p["category"].lower())
            if match_cat and match_price and match_query:
                results.append(p)
            
    if not results:
        return "No products found matching those filters. Try adjusting your search keywords or category."
        
    output = "Available Products in Catalog:\n"
    for r in results:
        output += f"- [{r['id']}] {r['name']} - ${r['price']:.2f} (Stock: {r['stock']} left)\n"
        output += f"  Description: {r['description']}\n\n"
    return output

@tool("Modify User Shopping Cart")
def modify_user_shopping_cart(action: str, product_id: str, quantity: int = 1) -> str:
    """
    Manipulates the user's active shopping cart and checkout state.
    Inputs:
    - action: The action to perform. MUST be one of: 'add', 'remove', 'clear', 'checkout'.
    - product_id: The unique ID of the product (e.g., 'shirt_1', 'watch_3') to add/remove. Pass empty string for 'clear' or 'checkout'.
    - quantity: Number of items to add or remove (default is 1).
    Returns a confirmation string of the action taken.
    """
    global _active_cart, _action_log
    action = action.lower().strip()
    pid = product_id.strip()
    
    if action == "add":
        prod = get_product_by_id(pid)
        if not prod:
            return f"Error: Product with ID '{pid}' does not exist in the catalog."
            
        # Check stock limits
        current_in_cart = _active_cart.get(pid, 0)
        target_qty = current_in_cart + quantity
        if target_qty > prod["stock"]:
            target_qty = prod["stock"]
            added = prod["stock"] - current_in_cart
            _active_cart[pid] = prod["stock"]
            _action_log.append(f"added {pid} up to stock limit")
            if added <= 0:
                return f"Cannot add more of '{prod['name']}'. We are already at the maximum stock limit of {prod['stock']} units."
            return f"Added {added} of '{prod['name']}' to the cart. Reached local stock limit of {prod['stock']} units."
            
        _active_cart[pid] = target_qty
        _action_log.append(f"added {pid} (qty: {quantity})")
        return f"Successfully added {quantity} of '{prod['name']}' (ID: {pid}) to the cart. Cart now has {target_qty} units."
        
    elif action == "remove":
        prod = get_product_by_id(pid)
        name = prod.get("name", pid)
        if pid not in _active_cart:
            return f"Product '{name}' is not in the shopping cart."
            
        current = _active_cart[pid]
        if quantity >= current:
            del _active_cart[pid]
            _action_log.append(f"removed {pid}")
            return f"Removed all units of '{name}' from the cart."
        else:
            _active_cart[pid] = current - quantity
            _action_log.append(f"reduced {pid} by {quantity}")
            return f"Reduced '{name}' by {quantity}. {current - quantity} units remain in the cart."
            
    elif action == "clear":
        _active_cart.clear()
        _action_log.append("clear")
        return "The shopping cart has been cleared."
        
    elif action == "checkout":
        if not _active_cart:
            return "Cannot checkout. The shopping cart is currently empty."
            
        # Compile total price and checkout
        total_price = 0.0
        items_ordered = []
        for item_id, qty in _active_cart.items():
            p = get_product_by_id(item_id)
            total_price += p.get("price", 0.0) * qty
            items_ordered.append(f"{qty}x {p.get('name', item_id)}")
            
        _active_cart.clear() # Clear cart on successful order
        _action_log.append("checkout")
        return f"Order PLACED successfully! Total cost: ${total_price:.2f}. Items purchased: {', '.join(items_ordered)}."
        
    else:
        return f"Unknown action '{action}'. Valid actions are: add, remove, clear, checkout."

# -------------------------------------------------------------
# CrewAI Agent Setup
# -------------------------------------------------------------

def create_crew_system() -> Crew:
    """
    Creates and returns the CrewAI agent setup.
    Model: meta/llama-3.3-70b-instruct — highly reliable, excellent at tool use, and 3x faster than 3.1.
    """
    llm = LLM(
        model="nvidia_nim/meta/llama-3.3-70b-instruct",
        temperature=0.2,
        max_tokens=1024,
    )
    
    # 1. Stylist / Fashion Consultant Agent
    stylist_agent = Agent(
        role="Elite Personal Fashion Consultant",
        goal="Browse the catalog to recommend premium clothes, accessories, and styling tips that perfectly match the user's inquiry.",
        backstory="An elegant, sophisticated personal stylist with a deep eye for design, fit, and premium styles. You talk elegantly about fabrics, tailoring, coordination, and help the user find the perfect item.",
        tools=[search_fashion_catalog],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # 2. Order Processor Agent
    order_agent = Agent(
        role="Meticulous Order Operations Manager",
        goal="Perfectly manage the shopping cart actions (adding, removing, clearing) and process final checkouts.",
        backstory="An extremely precise, reliable shopping assistant who is fast and strictly executes cart modification requests and order placement. You always double-check product availability and confirm actions in the cart.",
        tools=[modify_user_shopping_cart],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Define tasks — one per agent (CrewAI sequential)
    style_task = Task(
        description=(
            "Review the user's voice input: '{user_input}'.\n"
            "If the user is asking about products, styling, or recommendations, search the "
            "fashion catalog and craft a warm, elegant response.\n"
            "If the request is purely a cart action (add/remove/checkout), just output: "
            "'CART_ACTION_ONLY' so the next agent handles it."
        ),
        expected_output="A warm, elegant 1-2 sentence fashion recommendation, or the literal string 'CART_ACTION_ONLY'.",
        agent=stylist_agent,
    )

    order_task = Task(
        description=(
            "Review the user's voice input: '{user_input}' and the stylist's output.\n"
            "If the user's request is purely informational (e.g. asking how many items are in store, price of items, what is available) "
            "and does NOT specify any cart modification (add/remove/checkout), you MUST NOT say you lack information to execute a cart action. "
            "Instead, simply repeat the stylist's elegant recommendation/answer verbatim as the final response.\n"
            "If the user wants to add, remove, clear cart items, or place an order, use "
            "the 'Modify User Shopping Cart' tool to execute that action, and produce the final spoken reply confirming the cart action."
        ),
        expected_output="A concise, natural, spoken response answering the user's question or confirming their cart actions.",
        agent=order_agent,
    )

    # Assemble Crew
    crew = Crew(
        agents=[stylist_agent, order_agent],
        tasks=[style_task, order_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew

# -------------------------------------------------------------
# Main Entrypoint
# -------------------------------------------------------------

def _build_result(user_input, session_id, result_obj, current_cart, asr_mode, tts_mode):
    """Shared logic to build the response dict and persist to MongoDB."""
    global _active_cart, _action_log
    response_text = str(result_obj).strip()
    print(f"[Agent] flow done | response='{response_text[:80]}...' | cart={_active_cart}")

    # ── Persist session to MongoDB (best-effort) ──
    try:
        from database import log_voice_session
        log_voice_session(
            session_id=session_id,
            transcription=user_input,
            response=response_text,
            asr_mode=asr_mode,
            tts_mode=tts_mode,
            cart_snapshot=_active_cart.copy(),
        )
    except Exception as db_err:
        print(f"[Agent] MongoDB session log skipped: {db_err}")

    return {
        "response": response_text,
        "cart":     _active_cart.copy(),
        "actions":  _action_log.copy(),
    }


def _prepare_flow(user_input, current_cart, session_id):
    """Shared setup for both sync and async flows."""
    global _active_cart, _action_log
    _active_cart = current_cart.copy()
    _action_log = []
    if not session_id:
        session_id = str(uuid.uuid4())
    print(f"[Agent] flow start | session={session_id} | input='{user_input}' | cart={current_cart}")
    return session_id


def run_agent_flow(user_input: str, current_cart: Dict[str, int],
                   session_id: str = "", asr_mode: str = "online",
                   tts_mode: str = "online") -> Dict[str, Any]:
    """
    Synchronous version – use from scripts and CLI.
    Do NOT call from an async FastAPI endpoint (use run_agent_flow_async instead).
    """
    session_id = _prepare_flow(user_input, current_cart, session_id)
    try:
        crew = create_crew_system()
        result = crew.kickoff(inputs={"user_input": user_input})
        return _build_result(user_input, session_id, result, current_cart, asr_mode, tts_mode)
    except Exception as e:
        import traceback
        print(f"[Agent] ERROR in multi-agent flow: {e}")
        traceback.print_exc()
        return {"response": f"Agent error: {e}", "cart": current_cart, "actions": []}


async def run_agent_flow_async(user_input: str, current_cart: Dict[str, int],
                               session_id: str = "", asr_mode: str = "online",
                               tts_mode: str = "online") -> Dict[str, Any]:
    """
    Async version – safe to call from FastAPI async endpoints.
    Uses crew.kickoff_async() which cooperates with the running event loop.
    """
    session_id = _prepare_flow(user_input, current_cart, session_id)
    try:
        crew = create_crew_system()
        result = await crew.kickoff_async(inputs={"user_input": user_input})
        return _build_result(user_input, session_id, result, current_cart, asr_mode, tts_mode)
    except Exception as e:
        import traceback
        print(f"[Agent] ERROR in multi-agent flow (async): {e}")
        traceback.print_exc()
        return {"response": f"Agent error: {e}", "cart": current_cart, "actions": []}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing Multi-Agent Coordinator using NVIDIA NIM...")
        test_cart = {}
        result = run_agent_flow("Hey, can you search for a good linen shirt and add one to my cart?", test_cart)
        print("Agent Result:")
        print(json.dumps(result, indent=2))
    else:
        print("Agents module imported. Run with '--test' to execute a sample tool flow.")
