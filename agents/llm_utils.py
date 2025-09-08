"""
LLM utility functions for generating natural language reasoning.
Currently uses a dummy fallback, but you can plug in OpenAI/HuggingFace/etc.
"""

def generate_reasoning(item, comps, baseline, final_price, min_price, max_price):
    """
    Stub function to generate human-like explanations for price suggestions.
    
    Parameters
    ----------
    item : dict
        The product details
    comps : list
        List of comparable items used in calculation
    baseline : float
        Baseline (formula-based) estimate
    final_price : float
        Central blended price
    min_price : float
        Suggested minimum price
    max_price : float
        Suggested maximum price
    
    Returns
    -------
    str
        Natural language reasoning string
    """
    # ---- Fallback version (no real LLM) ----
    title = item.get("title", "item")
    brand = item.get("brand", "")
    cond = item.get("condition", "")
    age = item.get("age_months", "?")

