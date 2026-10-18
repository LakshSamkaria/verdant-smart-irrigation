# Verdant — Smart Irrigation System

A local academic web application demonstrating Greedy Algorithm and Dynamic Programming for constrained irrigation-water allocation.

## Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python + Flask
- Charts: Chart.js (loaded from CDN)
- Algorithms: Greedy heuristic and multiple-choice Knapsack-style Dynamic Programming

## Run on Windows / VS Code
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. In Terminal, create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and then `.\.venv\Scripts\python.exe app.py`.

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

## Features
- Responsive dashboard and field-management table
- Editable field data and water budget
- Greedy and DP allocation using the same input dataset and benefit model
- Algorithm comparison with execution timing and complexity
- Charts and CSV export
- Sample data and viva notes

## Model and limitations
Each field has three mutually exclusive choices: no irrigation, partial irrigation, or full irrigation. The objective is to maximize the modeled benefit score while staying within the discretized water budget. Dynamic Programming is optimal only for this finite model and unit resolution; it does not guarantee an optimum for every real-world irrigation problem. The benefit score and demand values are for educational simulation, not agricultural advice. The app does not control physical pumps or sensors.

Water is discretized by the selected unit size. Each partial/full option's water cost is rounded up to a whole unit to ensure the total allocation never exceeds the capacity. DP complexity is O(n × W × k) time and O(n × W) space, where n is fields, W is the number of discrete water units, and k=3 options.

## Tests
Run:

```powershell
python -m unittest discover -s tests -v
```
