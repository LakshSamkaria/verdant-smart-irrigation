def validate_payload(payload):
    if not isinstance(payload.get("fields"), list):
        return "Fields must be provided as a list."
    if len(payload["fields"]) > 50:
        return "Please use 50 fields or fewer for this demonstration."
    try:
        water = float(payload.get("available_water"))
        unit = int(payload.get("unit_size", 10))
    except (TypeError, ValueError):
        return "Available water and unit size must be numbers."
    if water < 0 or water > 10000000:
        return "Available water must be between 0 and 10,000,000 litres."
    if unit < 1 or unit > 1000:
        return "Unit size must be between 1 and 1000 litres."
    ids = set()
    for i, f in enumerate(payload["fields"]):
        try:
            field_id = int(f.get("id", i + 1))
            area = float(f["area"])
            moisture = float(f["moisture"])
            target = float(f["target_moisture"])
            demand = float(f["demand"])
            priority = float(f.get("priority", 3))
            max_alloc = float(f.get("max_allocation", demand))
        except (KeyError, TypeError, ValueError):
            return f"Field {i + 1}: check all numeric fields."
        if field_id in ids:
            return "Field IDs must be unique."
        ids.add(field_id)
        if not str(f.get("name", "")).strip() or not str(f.get("crop", "")).strip():
            return f"Field {i + 1}: name and crop are required."
        if area <= 0 or demand < 0 or max_alloc < 0:
            return f"Field {i + 1}: area must be positive; demand and maximum allocation cannot be negative."
        if not 0 <= moisture <= 100 or not 0 <= target <= 100:
            return f"Field {i + 1}: moisture values must be 0–100%."
        if not 1 <= priority <= 5:
            return f"Field {i + 1}: priority must be between 1 and 5."
        if demand > max_alloc:
            return f"Field {i + 1}: demand cannot exceed maximum allocation."
    return None

def enrich_fields(fields):
    enriched = []
    for i, f in enumerate(fields):
        moisture = float(f["moisture"])
        target = float(f["target_moisture"])
        priority = float(f.get("priority", 3))
        deficit = max(0.0, target - moisture)
        # Transparent teaching score: moisture deficit × user priority.
        score = round(deficit * priority / 5, 2)
        enriched.append({
            "id": int(f.get("id", i + 1)),
            "name": str(f["name"]).strip(),
            "crop": str(f["crop"]).strip(),
            "area": float(f["area"]),
            "moisture": moisture,
            "target_moisture": target,
            "demand": int(float(f["demand"])),
            "priority": priority,
            "max_allocation": int(float(f.get("max_allocation", f["demand"]))),
            "priority_score": score,
            "moisture_deficit": round(deficit, 2)
        })
    return enriched
