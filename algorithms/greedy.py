def run_greedy(fields, available_water, unit_size=10):
    """Greedy heuristic: rank fields by benefit per rounded-up water unit.
    For each field, choose the best feasible option at the current remaining budget.
    """
    budget_units = available_water // unit_size
    ranked = []
    for field in fields:
        options = _options(field, unit_size)
        best = max(options[1:], key=lambda o: o["benefit"] / max(1, o["units"]))
        ranked.append((best["benefit"] / max(1, best["units"]), field, options))
    ranked.sort(key=lambda row: (-row[0], -row[1]["priority_score"], row[1]["id"]))

    remaining = budget_units
    allocations = []
    steps = []
    total_benefit = 0
    for rank, (_, field, options) in enumerate(ranked, start=1):
        feasible = [o for o in options if o["units"] <= remaining]
        chosen = max(feasible, key=lambda o: (o["benefit"], -o["units"])) if feasible else options[0]
        remaining -= chosen["units"]
        total_benefit += chosen["benefit"]
        allocations.append(_allocation(field, chosen, rank))
        steps.append({
            "title": f"Decision {rank}: {field['name']}",
            "detail": f"Ranked by benefit per water unit. Choose {chosen['label']} using {chosen['units'] * unit_size} L; {remaining * unit_size} L remains."
        })
    allocations.sort(key=lambda x: x["id"])
    used = sum(a["allocated_water"] for a in allocations)
    return {
        "algorithm": "Greedy",
        "allocations": allocations,
        "total_water_used": used,
        "remaining_water": available_water - used,
        "unmet_demand": sum(max(0, f["demand"] - a["allocated_water"]) for f, a in zip(
            sorted(fields, key=lambda f: f["id"]), allocations)),
        "total_benefit": total_benefit,
        "fields_served": sum(1 for a in allocations if a["allocated_water"] > 0),
        "steps": steps,
        "complexity": {"time": "O(n log n + n)", "space": "O(n)", "explanation": "Sorting fields dominates the linear allocation pass."},
        "limitation": "Greedy makes locally attractive choices first. It is a heuristic and is not guaranteed to find the global optimum."
    }

def _options(field, unit_size):
    demand = int(field["demand"])
    full_units = (demand + unit_size - 1) // unit_size
    partial_water = (demand + 1) // 2
    partial_units = (partial_water + unit_size - 1) // unit_size
    base = int(field["priority_score"] * field["area"])
    # Keep a field's benefit positive when it has a meaningful moisture deficit.
    full_benefit = max(0, base)
    partial_benefit = int(full_benefit * (partial_water / max(1, demand)) * 0.9)
    return [
        {"label": "No irrigation", "option": "none", "units": 0, "water": 0, "benefit": 0},
        {"label": "Partial", "option": "partial", "units": partial_units, "water": partial_units * unit_size, "benefit": partial_benefit},
        {"label": "Full", "option": "full", "units": full_units, "water": full_units * unit_size, "benefit": full_benefit},
    ]

def _allocation(field, option, rank):
    return {
        "id": field["id"], "name": field["name"], "crop": field["crop"],
        "priority_score": field["priority_score"], "option": option["option"],
        "option_label": option["label"], "allocated_water": option["water"],
        "benefit": option["benefit"], "greedy_rank": rank,
        "demand": field["demand"]
    }
