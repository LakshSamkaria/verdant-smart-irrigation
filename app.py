from flask import Flask, render_template, request, jsonify, Response
from algorithms.greedy import run_greedy
from algorithms.dynamic_programming import run_dp
from services.irrigation_service import validate_payload, enrich_fields
import csv
import io
import time

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

SAMPLE_FIELDS = [
    {"id": 1, "name": "North Field", "crop": "Wheat", "area": 1.2, "moisture": 22, "target_moisture": 60, "demand": 120, "priority": 5, "max_allocation": 120},
    {"id": 2, "name": "East Garden", "crop": "Tomato", "area": 0.6, "moisture": 35, "target_moisture": 65, "demand": 70, "priority": 4, "max_allocation": 70},
    {"id": 3, "name": "South Plot", "crop": "Rice", "area": 1.5, "moisture": 48, "target_moisture": 75, "demand": 150, "priority": 5, "max_allocation": 150},
    {"id": 4, "name": "West Field", "crop": "Cotton", "area": 1.0, "moisture": 28, "target_moisture": 60, "demand": 95, "priority": 3, "max_allocation": 95},
]

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/sample")
def sample():
    return jsonify({"available_water": 250, "unit_size": 10, "fields": SAMPLE_FIELDS})

@app.post("/api/simulate")
def simulate():
    payload = request.get_json(silent=True) or {}
    error = validate_payload(payload)
    if error:
        return jsonify({"error": error}), 400
    fields = enrich_fields(payload["fields"])
    water = int(payload["available_water"])
    unit_size = int(payload.get("unit_size", 10))
    # Use the same objective and the same discrete water budget for both strategies.
    t0 = time.perf_counter()
    greedy = run_greedy(fields, water, unit_size)
    greedy_ms = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    dp = run_dp(fields, water, unit_size)
    dp_ms = (time.perf_counter() - t0) * 1000
    return jsonify({
        "available_water": water,
        "unit_size": unit_size,
        "fields": fields,
        "greedy": {**greedy, "execution_ms": round(greedy_ms, 4)},
        "dp": {**dp, "execution_ms": round(dp_ms, 4)},
        "assumptions": [
            "Each field has three options: no irrigation, partial irrigation, or full irrigation.",
            "Partial irrigation uses approximately half the field's requested water and earns a scaled benefit.",
            "Water amounts are rounded up to the selected unit size for DP feasibility.",
            "Benefit scores are educational model scores, not real crop-yield predictions."
        ]
    })

@app.post("/api/export")
def export_csv():
    payload = request.get_json(silent=True) or {}
    result = payload.get("result", {})
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Algorithm", "Field", "Crop", "Priority Score", "Option", "Water Allocated (L)", "Benefit"])
    for alg_name in ("greedy", "dp"):
        for item in result.get(alg_name, {}).get("allocations", []):
            writer.writerow([alg_name.upper(), item["name"], item["crop"], item["priority_score"], item["option"], item["allocated_water"], item["benefit"]])
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=irrigation-report.csv"})

if __name__ == "__main__":
    app.run(debug=True)
