"""
VALENTI AI — Model Comparison Test Bench
=========================================
Tests both `meta/llama-3.1-70b-instruct` and `moonshotai/kimi-k2.6` on NVIDIA NIM
with 5 fashion-related inputs. Measures tool usage, response quality, and latency.

Usage:
    uv run python test_model_comparison.py
"""

import os
import sys
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load env
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)
os.environ["NVIDIA_API_KEY"] = os.getenv("NVIDIA_NIM_API_KEY", "")

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

# ── Load product catalog ──
PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "products.json")
with open(PRODUCTS_FILE, "r") as f:
    PRODUCTS_CATALOG = json.load(f)

# ── Shared state ──
_active_cart: Dict[str, int] = {}
_action_log: List[str] = []
_tool_calls: List[str] = []

def get_product_by_id(product_id: str) -> Dict[str, Any]:
    for p in PRODUCTS_CATALOG:
        if p["id"].lower() == product_id.lower() or p["name"].lower() == product_id.lower():
            return p
    return {}

# ── Tools (instrumented with call tracking) ──

@tool("Search Fashion Catalog")
def search_fashion_catalog(query: str = "", category: str = "", max_price: float = 10000.0) -> str:
    """
    Search the fashion store's product database.
    Inputs:
    - query: Optional keywords to search in product names or descriptions.
    - category: Optional category filter. Available: shirt, watch, pant, shoes, jacket, bag, hat, sunglasses, belt, socks.
    - max_price: Optional maximum price filter.
    Returns a formatted string listing matching products.
    """
    _tool_calls.append(f"search_fashion_catalog(query='{query}', category='{category}', max_price={max_price})")
    results = []
    q = query.lower()
    cat = category.lower().strip()
    for p in PRODUCTS_CATALOG:
        match_cat = not cat or p["category"].lower() == cat
        match_price = p["price"] <= max_price
        match_query = True
        if q:
            match_query = (q in p["name"].lower() or q in p["description"].lower() or q in p["category"].lower())
        if match_cat and match_price and match_query:
            results.append(p)
    if not results:
        return "No products found matching those filters."
    output = "Available Products:\n"
    for r in results:
        output += f"- [{r['id']}] {r['name']} - ${r['price']:.2f} (Stock: {r['stock']})\n"
        output += f"  {r['description']}\n\n"
    return output


@tool("Modify User Shopping Cart")
def modify_user_shopping_cart(action: str, product_id: str, quantity: int = 1) -> str:
    """
    Manipulates the user's active shopping cart.
    Inputs:
    - action: 'add', 'remove', 'clear', or 'checkout'.
    - product_id: Product ID (e.g. 'shirt_1').
    - quantity: Number of items (default 1).
    """
    global _active_cart, _action_log
    _tool_calls.append(f"modify_cart(action='{action}', product_id='{product_id}', qty={quantity})")
    action = action.lower().strip()
    pid = product_id.strip()
    if action == "add":
        prod = get_product_by_id(pid)
        if not prod:
            return f"Error: Product '{pid}' not found."
        current = _active_cart.get(pid, 0)
        _active_cart[pid] = current + quantity
        _action_log.append(f"added {pid}")
        return f"Added {quantity}x '{prod['name']}' to cart."
    elif action == "remove":
        if pid in _active_cart:
            del _active_cart[pid]
            _action_log.append(f"removed {pid}")
            return f"Removed '{pid}' from cart."
        return f"'{pid}' not in cart."
    elif action == "clear":
        _active_cart.clear()
        return "Cart cleared."
    elif action == "checkout":
        if not _active_cart:
            return "Cart is empty."
        total = sum(get_product_by_id(k).get("price", 0) * v for k, v in _active_cart.items())
        _active_cart.clear()
        return f"Order placed! Total: ${total:.2f}"
    return f"Unknown action '{action}'."


# ── 5 Test Inputs ──
TEST_INPUTS = [
    {
        "id": 1,
        "input": "What are the fashion products available in your store?",
        "expected_tool": "search_fashion_catalog",
        "description": "Browse entire catalog",
    },
    {
        "id": 2,
        "input": "Show me some premium watches under $300",
        "expected_tool": "search_fashion_catalog",
        "description": "Category + price filter",
    },
    {
        "id": 3,
        "input": "I'm looking for a nice leather jacket, do you have any?",
        "expected_tool": "search_fashion_catalog",
        "description": "Keyword search (leather jacket)",
    },
    {
        "id": 4,
        "input": "Add the Classic Linen shirt to my cart please",
        "expected_tool": "modify_user_shopping_cart",
        "description": "Cart add action",
    },
    {
        "id": 5,
        "input": "Can you recommend a complete outfit — shirt, pants, and shoes — for a formal dinner?",
        "expected_tool": "search_fashion_catalog",
        "description": "Complex multi-category recommendation",
    },
]


# ── Model Definitions ──
MODELS = [
    {
        "name": "Meta Llama 3.1 70B Instruct",
        "model_id": "nvidia_nim/meta/llama-3.1-70b-instruct",
    },
    {
        "name": "Meta Llama 3.3 70B Instruct",
        "model_id": "nvidia_nim/meta/llama-3.3-70b-instruct",
    },
]


def create_test_crew(model_id: str) -> Crew:
    """Build a fresh Crew with the given model."""
    llm = LLM(model=model_id, temperature=0.2, max_tokens=1024)

    stylist = Agent(
        role="Elite Personal Fashion Consultant",
        goal="Browse the catalog to recommend premium clothes and accessories matching the user's inquiry.",
        backstory="A sophisticated stylist with deep expertise in fashion, fabrics, and coordination.",
        tools=[search_fashion_catalog],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    order_mgr = Agent(
        role="Meticulous Order Operations Manager",
        goal="Execute shopping cart actions (add, remove, clear, checkout) precisely.",
        backstory="A reliable shopping assistant who executes cart requests accurately.",
        tools=[modify_user_shopping_cart],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    style_task = Task(
        description=(
            "Review the user's input: '{user_input}'.\n"
            "If asking about products/styling/recommendations, search the catalog and respond.\n"
            "If purely a cart action, output 'CART_ACTION_ONLY'."
        ),
        expected_output="A 1-2 sentence fashion recommendation, or 'CART_ACTION_ONLY'.",
        agent=stylist,
    )

    order_task = Task(
        description=(
            "Review the user's input: '{user_input}' and the stylist's output.\n"
            "If the user wants to add/remove/clear/checkout, execute it.\n"
            "Produce a concise spoken reply (max 3 sentences)."
        ),
        expected_output="A concise, natural, spoken response. Max 3 sentences.",
        agent=order_mgr,
    )

    return Crew(
        agents=[stylist, order_mgr],
        tasks=[style_task, order_task],
        process=Process.sequential,
        verbose=False,
    )


def run_single_test(model_info: dict, test_case: dict) -> dict:
    """Run a single test case against a model and collect metrics."""
    global _active_cart, _action_log, _tool_calls
    _active_cart = {}
    _action_log = []
    _tool_calls = []

    print(f"    Test {test_case['id']}: {test_case['description']}...", end=" ", flush=True)

    start = time.time()
    try:
        crew = create_test_crew(model_info["model_id"])
        result = crew.kickoff(inputs={"user_input": test_case["input"]})
        elapsed = time.time() - start
        response = str(result).strip()
        status = "SUCCESS"
        error = None
    except Exception as e:
        elapsed = time.time() - start
        response = ""
        status = "ERROR"
        error = str(e)

    # Check tool usage
    used_expected = any(test_case["expected_tool"].replace("_", "") in tc.replace("_", "") for tc in _tool_calls) if _tool_calls else False

    result_data = {
        "test_id": test_case["id"],
        "description": test_case["description"],
        "input": test_case["input"],
        "expected_tool": test_case["expected_tool"],
        "tool_calls": _tool_calls.copy(),
        "used_expected_tool": used_expected,
        "response": response[:500],
        "status": status,
        "error": error,
        "latency_s": round(elapsed, 2),
    }

    icon = "✓" if status == "SUCCESS" else "✗"
    tool_icon = "🔧" if used_expected else "⚠"
    print(f"{icon} {elapsed:.1f}s {tool_icon} tools={_tool_calls}")

    return result_data


def main():
    print("=" * 70)
    print("  VALENTI AI — Model Comparison Test Bench")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"  Test cases: {len(TEST_INPUTS)}")
    print(f"  Models:     {', '.join(m['name'] for m in MODELS)}")
    print(f"  Products:   {len(PRODUCTS_CATALOG)} items loaded")
    print("=" * 70)

    all_results = {}

    for model in MODELS:
        print(f"\n{'─' * 60}")
        print(f"  Testing: {model['name']}")
        print(f"  Model:   {model['model_id']}")
        print(f"{'─' * 60}")

        model_results = []
        for test_case in TEST_INPUTS:
            result = run_single_test(model, test_case)
            model_results.append(result)

        all_results[model["name"]] = model_results

    # ── Summary Report ──
    print("\n" + "=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)

    summary = {}
    for model_name, results in all_results.items():
        successes = sum(1 for r in results if r["status"] == "SUCCESS")
        tool_hits = sum(1 for r in results if r["used_expected_tool"])
        avg_latency = sum(r["latency_s"] for r in results) / len(results)
        errors = sum(1 for r in results if r["status"] == "ERROR")

        summary[model_name] = {
            "success_rate": f"{successes}/{len(results)}",
            "tool_accuracy": f"{tool_hits}/{len(results)}",
            "avg_latency": f"{avg_latency:.1f}s",
            "errors": errors,
        }

        print(f"\n  {model_name}:")
        print(f"    Success Rate:   {successes}/{len(results)}")
        print(f"    Tool Accuracy:  {tool_hits}/{len(results)} (called correct tool)")
        print(f"    Avg Latency:    {avg_latency:.1f}s")
        print(f"    Errors:         {errors}")

    # Determine winner
    print("\n" + "─" * 70)
    best_model = None
    best_score = -1
    for model_name, s in summary.items():
        successes = int(s["success_rate"].split("/")[0])
        tool_hits = int(s["tool_accuracy"].split("/")[0])
        avg_lat = float(s["avg_latency"].replace("s", ""))
        # Score: successes * 10 + tool_hits * 5 - avg_latency
        score = successes * 10 + tool_hits * 5 - avg_lat
        if score > best_score:
            best_score = score
            best_model = model_name

    print(f"  🏆 RECOMMENDED MODEL: {best_model}")
    print("─" * 70)

    # ── Save detailed results as JSON ──
    output_file = os.path.join(os.path.dirname(__file__), "model_comparison_results.json")
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "test_cases": len(TEST_INPUTS),
        "products_count": len(PRODUCTS_CATALOG),
        "summary": summary,
        "recommended_model": best_model,
        "detailed_results": all_results,
    }
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"\n  Detailed results saved to: {output_file}")

    # ── Print per-test detail table ──
    print("\n" + "=" * 70)
    print("  DETAILED TEST RESULTS")
    print("=" * 70)

    for test in TEST_INPUTS:
        print(f"\n  Test {test['id']}: {test['description']}")
        print(f"  Input: \"{test['input']}\"")
        print(f"  Expected tool: {test['expected_tool']}")
        for model_name, results in all_results.items():
            r = results[test["id"] - 1]
            status_icon = "✓" if r["status"] == "SUCCESS" else "✗"
            tool_icon = "✓" if r["used_expected_tool"] else "✗"
            print(f"    [{model_name}]")
            print(f"      Status: {status_icon} {r['status']} | Latency: {r['latency_s']}s | Tool: {tool_icon}")
            if r["response"]:
                # Truncate for readability
                resp = r["response"][:200].replace("\n", " ")
                print(f"      Response: {resp}...")
            if r["error"]:
                print(f"      Error: {r['error'][:150]}")

    print("\n" + "=" * 70)
    print("  Test bench complete.")
    print("=" * 70)

    return output_data


if __name__ == "__main__":
    main()
