# Disease Prediction Using Fuzzy Logic

An interpretable fuzzy inference system (FIS) for disease risk stratification leveraging linguistic membership functions, configurable rule bases, and an optional calibration layer for probabilistic mapping.

> Aim: Balance transparency and adaptability—enabling domain experts to audit and evolve risk reasoning without retraining opaque models.

---

## 🌟 Highlights

- Config-driven fuzzy membership definitions (triangular / trapezoidal / Gaussian)
- Modular rule base: easily add/remove disease-specific or risk-factor modules
- Multiple t-norm / s-norm strategies (min, product, max, probabilistic OR)
- Explanation trace: which rules fired, their degrees, and contribution weights
- Optional calibration: map defuzzified score → probability (logistic / isotonic)
- CLI & (planned) lightweight API for integration
- Extensible: add new variables, linguistic sets, or inference strategies

---

## 🧠 Why Fuzzy Logic?

| Challenge | Fuzzy Advantage |
|-----------|-----------------|
| Opaque ML risk scores | Human-auditable IF–THEN rules |
| Hard thresholds | Gradual membership (e.g. “moderately high”) |
| Mixed qualitative + quantitative input | Unified linguistic abstraction |
| Domain expert iteration | Rules editable without retraining |

---

## 🏗️ Architecture

```
Inputs → Preprocess → Fuzzify → Rule Evaluation → Aggregate → Defuzzify → (Calibrate) → Output
                              ↘ Explanation Trace (rules fired, degrees)
```

Core Components:
- membership/: Functions & parameterization
- rules/: Config definitions (YAML / JSON)
- engine/: Core inference logic
- inference/: Execution orchestration + explanation
- calibration/: Optional probability mapping
- api/: (Planned) service layer
- cli/: User-facing entrypoint

---

## 📂 Suggested Structure

```
.
├─ configs/
│  ├─ membership.yaml
│  └─ rules.yaml
├─ fuzzy/
│  ├─ membership/
│  ├─ rules/
│  ├─ engine/
│  ├─ inference/
│  └─ calibration/
├─ cli/
│  └─ run.py
├─ api/
│  ├─ server.py
│  └─ routers/
├─ notebooks/
│  ├─ exploratory.ipynb
│  └─ calibration.ipynb
├─ data/
│  ├─ samples/
│  └─ schemas/
├─ tests/
└─ README.md
```

---

## 🧩 Membership Definition (Example)

`configs/membership.yaml`:
```yaml
variables:
  temperature:
    unit: celsius
    sets:
      low:
        type: triangular
        params: [34, 35.5, 37]
      high:
        type: triangular
        params: [37, 39, 42]
  glucose:
    unit: mg/dL
    sets:
      elevated:
        type: trapezoidal
        params: [100, 110, 160, 180]
  heart_rate:
    unit: bpm
    sets:
      tachycardic:
        type: trapezoidal
        params: [90, 100, 140, 180]
```

---

## 🧮 Rule Base (Example)

`configs/rules.yaml`:
```yaml
rules:
  - id: r1
    if:
      - variable: temperature
        is: high
      - variable: glucose
        is: elevated
    then:
      risk: very_high
      weight: 1.0
  - id: r2
    if:
      - variable: temperature
        is: high
    then:
      risk: high
      weight: 0.7
  - id: r3
    if:
      - variable: heart_rate
        is: tachycardic
    then:
      risk: moderate
      weight: 0.5
```

---

## 🔄 Inference Flow

1. Load membership + rule configs  
2. Normalize inputs (unit conversions / clamping)  
3. Compute membership degrees  
4. Evaluate rule antecedents (t-norm)  
5. Aggregate consequents (s-norm + weighting)  
6. Defuzzify (centroid / weighted average) → raw risk score  
7. (Optional) Calibrate → probability  
8. Emit explanation trace

---

## ⚙️ Installation

```bash
git clone https://github.com/tharunkumarvk/Disease-Prediction-using-fuzzy-logic.git
cd Disease-Prediction-using-fuzzy-logic
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Suggested `requirements.txt` (if not yet created):
```
numpy
scipy
pydantic
pyyaml
fastapi
uvicorn
scikit-learn
```

---

## ▶️ CLI Usage

```bash
python -m cli.run \
  --temperature 38.2 \
  --glucose 145 \
  --heart_rate 102 \
  --output json
```

Sample JSON:
```json
{
  "inputs": {"temperature": 38.2, "glucose": 145, "heart_rate": 102},
  "risk_score": 0.81,
  "risk_label": "high",
  "rules_fired": [
    {
      "id": "r1",
      "antecedent_degree": 0.72,
      "contribution": 0.51,
      "description": "temperature is high AND glucose is elevated"
    }
  ]
}
```

---

## 🌐 API (Planned)

Start server:
```bash
uvicorn api.server:app --reload
```

Example request:
```bash
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"temperature": 38.2, "glucose": 145, "heart_rate": 102}'
```

---

## 🧪 Testing

```bash
pytest -q
```

Test categories:
- Membership functions (edge + nominal)
- Rule combination logic
- Defuzzification correctness
- Calibration mapping stability
- Explanation fidelity

---

## 📊 Evaluation & Calibration

If labeled data available:
- Split dataset (train/calibrate/test)
- Reliability curve (fuzzy score vs observed prevalence)
- Fit logistic or isotonic calibrator
- Metrics: AUC, Brier score, rule coverage %, explanation density

---

## 🔍 Explainability

Includes:
- Active rules with degrees
- Per-rule weighted contribution
- Normalized risk label mapping
- (Planned) Visual membership activation diagrams

---

## 🛠️ Extending

Add a variable:
1. Define sets in `membership.yaml`
2. Reference in new rules
3. Update preprocessing (if needed)

Add new disease module:
- Add rule group with `context: <disease>`
- Aggregate per-context and/or composite risk

Switch t-norm / s-norm:
- Configure in engine settings (e.g. `t_norm: product`, `s_norm: probabilistic_sum`)

---

## 🧱 Roadmap

| Milestone | Status |
|-----------|--------|
| Base fuzzy engine | ✅ |
| Config-driven rules | ✅ |
| Explanation trace | ✅ |
| Calibration layer | ⏳ |
| API service | ⏳ |
| Multi-disease modularization | Planned |
| Visualization dashboard | Planned |
| Rule suggestion assistant | Planned |

---

## ⚖️ Disclaimer

For research / educational purposes only. Not a certified medical device. Do not use for clinical decision-making.

---

## 🤝 Contributing

1. Branch: `feat/<name>`  
2. Add / adjust tests  
3. Run lint + test suite  
4. Open PR with rationale & calibration impact (if applicable)

Principles:
- Pure functions for fuzzy math
- Config-first extensibility
- Clear docstrings for new membership types

---

## 📄 License

MIT License (see LICENSE file).

---

## 💬 Contact

See profile contact links.

> “Explainability accelerates trust more than opaque marginal gains.”

---
