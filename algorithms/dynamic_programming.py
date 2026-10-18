def run_dp(fields, available_water, unit_size=10):
    """Multiple-choice knapsack DP: one option per field (none/partial/full).
    Capacity is discretized in unit_size litre units. Returns a globally optimal
    benefit for this finite, explicitly defined option model.
    """
    capacity = available_water // unit_size
    options_by_field = []
    for field in fields:
        demand = int(field["demand"])
        full_units = (demand + unit_size - 1) // unit_size
        partial_water = (demand + 1) // 2
        partial_units = (partial_water + unit_size - 1) // unit_size
        full_benefit = max(0, int(field["priority_score"] * field["area"]))
        partial_benefit = int(full_benefit * (partial_water / max(1, demand)) * 0.9)
        options_by_field.append([
            {"option": "none", "label": "No irrigation", "units": 0, "water": 0, "benefit": 0},
            {"option": "partial", "label": "Partial", "units": partial_units, "water": partial_units * unit_size, "benefit": partial_benefit},
            {"option": "full", "label": "Full", "units": full_units, "water": full_units * unit_size, "benefit": full_benefit},
        ])

    n = len(fields)
    # dp[i][w] = maximum benefit using first i fields with capacity w.
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    choice = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            best_benefit, best_idx = dp[i - 1][w], 0
            for oi, option in enumerate(options_by_field[i - 1]):
                if option["units"] <= w:
                    candidate = dp[i - 1][w - option["units"]] + option["benefit"]
                    if candidate > best_benefit:
                        best_benefit, best_idx = candidate, oi
            dp[i][w] = best_benefit
            choice[i][w] = best_idx

    allocations = []
    w = capacity
    selected_options = [0] * n
    for i in range(n, 0, -1):
        oi = choice[i][w]
        selected_options[i - 1] = oi
        w -= options_by_field[i - 1][oi]["units"]

    steps = []
    for i, field in enumerate(fields):
        option = options_by_field[i][selected_options[i]]
        allocations.append({
            "id": field["id"], "name": field["name"], "crop": field["crop"],
            "priority_score": field["priority_score"], "option": option["option"],
            "option_label": option["label"], "allocated_water": option["water"],
            "benefit": option["benefit"], "greedy_rank": None,
            "demand": field["demand"]
        })
        steps.append({
            "title": f"Field {i + 1}: {field['name']}",
            "detail": f"DP compares no irrigation, partial ({option['units'] * unit_size} L cost), and full irrigation options. Selected: {option['label']}."
        })

    used = sum(a["allocated_water"] for a in allocations)
    return {
        "algorithm": "Dynamic Programming",
        "allocations": allocations,
        "total_water_used": used,
        "remaining_water": available_water - used,
        "unmet_demand": sum(max(0, f["demand"] - a["allocated_water"]) for f, a in zip(fields, allocations)),
        "total_benefit": dp[n][capacity],
        "fields_served": sum(1 for a in allocations if a["allocated_water"] > 0),
        "steps": steps,
        "dp_table": dp if capacity <= 150 else [],
        "complexity": {"time": "O(n × W × k)", "space": "O(n × W)", "explanation": "n fields, W discrete water units, and k=3 irrigation options per field. The full table is retained for explanation and reconstruction."},
        "limitation": f"Optimal only for this defined model and {unit_size} L discretization; it is not a universal optimum for real farms."
    }
