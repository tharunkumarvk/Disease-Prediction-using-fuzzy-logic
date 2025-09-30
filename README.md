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
- rules/: Config definitions (JSON)
- engine/: Core inference logic
- inference/: Execution orchestration + explanation
- calibration/: Optional probability mapping
- api/: (Planned) service layer
- cli/: User-facing entrypoint

---

## 📂 Structure

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


## ⚙️ Installation

```bash
git clone https://github.com/tharunkumarvk/Disease-Prediction-using-fuzzy-logic.git
cd Disease-Prediction-using-fuzzy-logic
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt`:
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


## 📄 License

MIT License (see LICENSE file).

---

