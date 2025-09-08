
from __future__ import annotations

import math
import json
from dataclasses import dataclass
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from agents.llm_utils import generate_reasoning


# ----------------------- Utility mappings -----------------------

COND_SCORE = {
    "Like New": 1.00,
    "Good": 0.82,
    "Fair": 0.70,
}

CATEGORY_DECAY = {
    "Mobile": 0.035,        # faster depreciation
    "Laptop": 0.030,
    "Electronics": 0.025,
    "Camera": 0.022,
    "Furniture": 0.015,
    "Fashion": 0.040,       # trends change fast
}

BRAND_MULTIPLIER = {
    # premium retention brands
    "Apple": 1.15,
    "Sony": 1.10,
    "Canon": 1.05,
    "Samsung": 1.05,
    "OnePlus": 1.05,
    # value brands
    "Xiaomi": 0.98,
    "Motorola": 0.97,
    # neutral defaults
    "HP": 1.00, "Dell": 1.00, "LG": 1.00, "Ikea": 1.00, "UrbanLadder": 1.00,
    "Adidas": 1.00, "Nike": 1.00,
}

def _cond_score(name: str) -> float:
    return COND_SCORE.get(name, 0.80)

def _decay_for_category(cat: str) -> float:
    return CATEGORY_DECAY.get(cat, 0.025)

def _brand_mult(brand: str) -> float:
    return BRAND_MULTIPLIER.get(brand, 1.00)

# ----------------------- PriceSuggestor -----------------------

@dataclass
class PriceSuggestor:
    df: pd.DataFrame

    @classmethod
    def from_csv(cls, path: str) -> "PriceSuggestor":
        df = pd.read_csv(path)
        # standardize
        for col in ["category", "brand", "condition", "location", "title"]:
            if col in df.columns:
                df[col] = df[col].astype(str)
        return cls(df=df)

    def _nearest_comparables(self, item: Dict[str, Any], k: int = 5) -> pd.DataFrame:
        """Find k nearest comps within the same category."""
        cat = item.get("category")
        pool = self.df.loc[self.df["category"].astype(str).str.lower() == str(cat).lower()].copy()
        if pool.empty:
            return pd.DataFrame()

        def cond_dist(c1, c2):
            return abs(_cond_score(str(c1)) - _cond_score(str(c2)))

        def brand_penalty(b1, b2):
            return 0.0 if str(b1).lower() == str(b2).lower() else 0.30

        def loc_penalty(l1, l2):
            return 0.0 if str(l1).lower() == str(l2).lower() else 0.05

        age = float(item.get("age_months", 0) or 0)
        for idx, row in pool.iterrows():
            d_age = abs(age - float(row["age_months"])) / 60.0  # normalize across 5 years
            d_cond = cond_dist(item.get("condition"), row["condition"])
            d_brand = brand_penalty(item.get("brand"), row["brand"])
            d_loc = loc_penalty(item.get("location"), row["location"])
            pool.loc[idx, "_dist"] = 0.6 * d_age + 0.35 * d_cond + 0.05 * d_brand + d_loc

        pool = pool.sort_values("_dist", ascending=True).head(k).reset_index(drop=True)
        # weights
        pool["_weight"] = 1.0 / (pool["_dist"] + 0.01)
        return pool

    def _baseline_formula(self, item: Dict[str, Any]) -> float:
        """Formula-based baseline using exponential depreciation and brand/condition multipliers."""
        category = str(item.get("category"))
        brand = str(item.get("brand"))
        age = float(item.get("age_months", 0) or 0)
        decay = _decay_for_category(category)
        cond_mult = _cond_score(item.get("condition"))
        brand_mult = _brand_mult(brand)

        # Estimate "new price" level using available comps in this brand+category
        pool = self.df[(self.df["category"].str.lower() == category.lower())]
        if not pool.empty:
            # Back out implied new price from comps
            pool = pool.assign(
                cond_mult=pool["condition"].map(lambda c: _cond_score(c)),
                k=decay,
                implied_new=lambda r: r["asking_price"] * np.exp(r["k"] * r["age_months"]) / (r["cond_mult"] * _brand_mult(brand=str(r["brand"]))),
            )
            # prefer same brand if enough points
            brand_pool = pool[pool["brand"].str.lower() == brand.lower()]
            used = brand_pool if len(brand_pool) >= 2 else pool
            new_price_est = used["implied_new"].median()
        else:
            new_price_est = float(item.get("asking_price", 0) or 0) / max(cond_mult, 0.5)

        # Now forward-price it to today's second-hand value
        baseline = new_price_est * cond_mult * brand_mult * math.exp(-decay * age)
        return float(baseline)

    def suggest(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Return a JSON-able suggestion with range + reasoning."""
        comps = self._nearest_comparables(item, k=5)
        comp_center = None
        comp_spread = None
        comp_used_records: List[Dict[str, Any]] = []

        if not comps.empty:
            # weighted average
            w = comps["_weight"].to_numpy()
            prices = comps["asking_price"].to_numpy(dtype=float)
            comp_center = float(np.average(prices, weights=w))
            # spread as max(8% of center, 0.5*stdev of chosen comps)
            comp_spread = float(max(0.08 * comp_center, 0.5 * np.std(prices)))
            comp_used_records = [
                {
                    "id": int(r["id"]),
                    "title": r["title"],
                    "brand": r["brand"],
                    "condition": r["condition"],
                    "age_months": int(r["age_months"]),
                    "asking_price": float(r["asking_price"]),
                    "distance": float(r["_dist"]),
                    "weight": float(r["_weight"]),
                }
                for _, r in comps.iterrows()
            ]

        baseline_center = self._baseline_formula(item)

        # Combine
        if comp_center is None:
            center = baseline_center
            used = "baseline_only"
            spread = max(0.10 * center, 1500.0)
        else:
            center = 0.55 * comp_center + 0.45 * baseline_center
            used = "ensemble(comps+baseline)"
            spread = max(0.12 * center, comp_spread or 0.0, 1200.0)

        suggested_min = max(0.0, round(center - spread, -2))
        suggested_max = round(center + spread, -2)

        reasoning = generate_reasoning(
            item=item,
            comps=comp_used_records,
            baseline=baseline_center,
            final_price=center,
            min_price=suggested_min,
            max_price=suggested_max
        )


        return {
            "suggested_min": suggested_min,
            "suggested_max": suggested_max,
            "central_price": round(center, 2),
            "method": used,
            "reasoning": reasoning,
            "comps_used": comp_used_records,
        }
