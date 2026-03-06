"""
Streamlit front-end for the Tropical Disease Prediction system.
Reuses fuzzy_app logic directly (no Django required).
"""

import sys
import os

# Make sure fuzzy_app is importable
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from fuzzy_app.tropical_diseases import (
    SYMPTOMS, SYMPTOM_ORDER, SYMPTOM_CATEGORIES, DISEASE_PROFILES
)
from fuzzy_app.consensus import consensus_predict

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tropical Disease Predictor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Quick-fill presets ────────────────────────────────────────────────────────
EXAMPLES = {
    "Malaria": {
        "fever": 103.5, "chills": 8, "headache": 7, "fatigue": 7,
        "muscle_pain": 5, "nausea_vomiting": 4, "loss_of_appetite": 6,
    },
    "Dengue Fever": {
        "fever": 104.0, "headache": 8, "joint_pain": 8, "muscle_pain": 8,
        "rash": 5, "eye_pain": 6, "fatigue": 7, "bleeding": 3,
    },
    "Typhoid Fever": {
        "fever": 103.0, "abdominal_pain": 6, "headache": 5, "fatigue": 7,
        "loss_of_appetite": 8, "nausea_vomiting": 4,
    },
    "Cholera": {
        "diarrhea": 9, "dehydration": 8, "nausea_vomiting": 7,
        "muscle_pain": 5, "fatigue": 7,
    },
    "Chikungunya": {
        "fever": 103.0, "joint_pain": 9, "muscle_pain": 7, "rash": 5,
        "headache": 5, "fatigue": 6,
    },
    "Yellow Fever": {
        "fever": 103.5, "jaundice": 6, "headache": 7, "bleeding": 5,
        "nausea_vomiting": 6, "fatigue": 7, "abdominal_pain": 5,
    },
    "Zika Virus": {
        "fever": 100.5, "rash": 7, "joint_pain": 5, "eye_pain": 6,
        "headache": 4, "fatigue": 4,
    },
    "Leptospirosis": {
        "fever": 103.0, "muscle_pain": 8, "headache": 7, "jaundice": 4,
        "chills": 6, "eye_pain": 5, "fatigue": 7,
    },
    "Common Cold": {
        "runny_nose": 8, "congestion": 7, "sneezing": 7, "sore_throat": 5,
        "cough": 4, "headache": 3, "fatigue": 3,
    },
    "Influenza": {
        "fever": 102.5, "muscle_pain": 8, "fatigue": 8, "headache": 7,
        "cough": 6, "chills": 7, "sore_throat": 4, "loss_of_appetite": 6,
    },
}


def render_sidebar():
    """Sidebar: quick-fill examples + about info."""
    st.sidebar.title("🩺 Disease Predictor")
    st.sidebar.markdown(
        "Uses **Fuzzy Logic** + **Random Forest** with a consensus mechanism "
        f"to predict from **{len(DISEASE_PROFILES)}** conditions."
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Quick Examples")
    st.sidebar.caption("Click to auto-fill typical symptom values:")

    cols = st.sidebar.columns(2)
    names = list(EXAMPLES.keys())
    for i, name in enumerate(names):
        col = cols[i % 2]
        if col.button(name, key=f"ex_{name}", use_container_width=True):
            for key in SYMPTOM_ORDER:
                val = EXAMPLES[name].get(key, None)
                st.session_state[f"input_{key}"] = val

    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Diseases Covered")
    for disease in DISEASE_PROFILES:
        st.sidebar.markdown(f"• {disease}")


def render_input_form():
    """Render grouped symptom input fields. Returns dict of provided values."""
    st.subheader("📋 Enter Symptom Values")
    st.caption(
        "Fill in symptoms you are experiencing. Leave blank if not present. "
        "Provide at least 3–4 symptoms for a meaningful prediction."
    )

    symptom_values = {}

    for cat_name, keys in SYMPTOM_CATEGORIES.items():
        # Category header with icon
        icons = {
            "Systemic": "🌡️", "Pain": "🩹", "Gastrointestinal": "💧",
            "Respiratory": "💨", "Skin & Hemorrhagic": "🎨", "Other": "🔬",
        }
        icon = icons.get(cat_name, "•")
        st.markdown(f"**{icon} {cat_name}**")

        col1, col2 = st.columns(2)
        for idx, key in enumerate(keys):
            info = SYMPTOMS[key]
            col = col1 if idx % 2 == 0 else col2

            if key == "fever":
                val = col.number_input(
                    f"🌡️ {info['name']}",
                    min_value=float(info["min"]),
                    max_value=float(info["max"]),
                    value=None,
                    step=0.1,
                    format="%.1f",
                    placeholder=f"{info['min']}–{info['max']} {info['unit']}",
                    help=info["help"],
                    key=f"input_{key}",
                )
            else:
                val = col.number_input(
                    f"{info['name']}",
                    min_value=float(info["min"]),
                    max_value=float(info["max"]),
                    value=None,
                    step=1.0,
                    format="%.0f",
                    placeholder=f"{info['min']}–{info['max']}",
                    help=info["help"],
                    key=f"input_{key}",
                )

            if val is not None:
                symptom_values[key] = val

        st.markdown("")  # spacer

    return symptom_values


def render_confidence_badge(level):
    colors = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
    return colors.get(level, "⚪") + f" **{level} Confidence**"


def render_results(result):
    """Display prediction results."""
    st.markdown("---")
    st.subheader("🔬 Prediction Results")

    v = result.get("validation", {})

    # ── Status banner ──────────────────────────────────────────────────────────
    status = v.get("status", "unknown")
    reliability = v.get("reliability_score", 0)
    confidence_level = result.get("confidence_level", "Low")
    models_agree = result.get("models_agree", False)

    if status == "reliable":
        st.success(
            f"**Prediction Status: RELIABLE** — Reliability Score: {reliability}%"
        )
    elif status == "moderate":
        st.warning(
            f"**Prediction Status: MODERATE** — Reliability Score: {reliability}%"
        )
    else:
        st.error(
            f"**Prediction Status: LOW RELIABILITY** — Reliability Score: {reliability}%"
        )

    st.progress(int(reliability) / 100)

    # ── Metric row ────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Data Completeness", f"{v.get('data_completeness', 0)}%",
                help=f"{v.get('symptoms_provided', 0)} symptoms provided")
    col2.metric("Prediction Certainty", f"{v.get('prediction_certainty', 0)}%",
                help="Gap between #1 and #2 prediction")
    col3.metric("Fuzzy Logic Top", result.get("fuzzy_top", "—"),
                help="Knowledge-based model result")
    col4.metric("Random Forest Top", result.get("rf_top", "—"),
                help="Data-driven model result")

    # ── Agreement badge ───────────────────────────────────────────────────────
    agree_col, conf_col = st.columns(2)
    if models_agree:
        agree_col.success("✅ Both models agree")
    else:
        agree_col.warning("⚠️ Models disagree — lower confidence")
    conf_col.info(render_confidence_badge(confidence_level))

    # ── Warnings ──────────────────────────────────────────────────────────────
    for w in v.get("warnings", []):
        st.warning(f"⚠️ {w}")

    # ── Top 3 disease predictions ─────────────────────────────────────────────
    st.markdown("### 🏆 Predicted Diseases (Consensus)")
    predictions = result.get("predictions", {})
    for rank, (disease, data) in enumerate(predictions.items(), start=1):
        conf = data["confidence"]
        color = "🥇" if rank == 1 else ("🥈" if rank == 2 else "🥉")

        with st.container():
            st.markdown(f"#### {color} {disease}")

            # Hallmarks
            hallmarks = data.get("hallmarks", [])
            if hallmarks:
                st.markdown(" ".join([f"`⭐ {h}`" for h in hallmarks]))

            # Confidence bar
            bar_col, score_col = st.columns([4, 1])
            bar_col.progress(conf / 100, text=f"Consensus {conf}%")
            score_col.markdown(
                f"<div style='text-align:right;font-size:1.3rem;font-weight:bold;color:#1f77b4'>{conf}%</div>",
                unsafe_allow_html=True,
            )

            # Individual model scores
            mc1, mc2 = st.columns(2)
            mc1.caption(f"🔷 Fuzzy Logic: **{data['fuzzy_score']}%**")
            mc2.caption(f"🌲 Random Forest: **{data['rf_score']}%**")

            st.write(data.get("description", ""))

            # Precautions (top disease only)
            if rank == 1 and data.get("precautions"):
                with st.expander("🛡️ Recommended Actions", expanded=True):
                    for p in data["precautions"]:
                        st.markdown(f"- {p}")

            if rank < len(predictions):
                st.markdown("---")

    # ── Fuzzy Logic Breakdown ─────────────────────────────────────────────────
    fuzzy_details = result.get("fuzzy_details")
    if fuzzy_details and fuzzy_details.get("details"):
        with st.expander(
            f"🔷 Fuzzy Logic Breakdown — {fuzzy_details.get('disease', '')}",
            expanded=False,
        ):
            import pandas as pd

            rows = []
            for d in fuzzy_details["details"]:
                match_pct = d.get("match_pct", 0)
                match_icon = (
                    "✅" if match_pct >= 70 else ("⚠️" if match_pct >= 40 else "❌")
                )
                rows.append(
                    {
                        "Symptom": d.get("symptom_name", d.get("symptom", "")),
                        "Your Value": d.get("value", "—"),
                        "Expected Level": d.get("expected_level", "—"),
                        "Actual Level": d.get("actual_level", "—"),
                        "Match": f"{match_icon} {match_pct}%",
                        "Weight": d.get("weight", "—"),
                        "Score": d.get("score", "—"),
                    }
                )
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Symptoms provided ─────────────────────────────────────────────────────
    symptom_values = result.get("symptom_values", {})
    if symptom_values:
        with st.expander("📊 Symptoms You Provided", expanded=False):
            import pandas as pd

            rows = []
            for key in SYMPTOM_ORDER:
                if key in symptom_values:
                    info = SYMPTOMS[key]
                    rows.append(
                        {
                            "Symptom": info["name"],
                            "Value": symptom_values[key],
                            "Unit": info["unit"],
                        }
                    )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_about():
    """About tab: disease profiles."""
    st.subheader("ℹ️ About This System")
    st.markdown(
        """
        This system combines two prediction models:

        | Model | Type | Strength |
        |---|---|---|
        | 🔷 Fuzzy Logic | Knowledge-based (WHO/CDC rules) | Works well with sparse/partial data |
        | 🌲 Random Forest | Data-driven (ML) | Works well with complete data |

        A **consensus mechanism** dynamically weights both models based on how many symptoms you provided.
        """
    )

    st.markdown("---")
    st.subheader(f"🦠 Diseases Covered ({len(DISEASE_PROFILES)})")
    for disease, profile in DISEASE_PROFILES.items():
        with st.expander(f"📋 {disease}"):
            st.write(profile.get("description", ""))
            hallmarks = profile.get("hallmarks", [])
            if hallmarks:
                st.markdown("**Hallmark symptoms:** " + ", ".join(f"`{h}`" for h in hallmarks))
            precautions = profile.get("precautions", [])
            if precautions:
                st.markdown("**Precautions:**")
                for p in precautions:
                    st.markdown(f"- {p}")
            refs = profile.get("references", [])
            if refs:
                st.caption("References: " + ", ".join(refs))


# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    render_sidebar()

    st.title("🩺 Tropical Disease Symptom Checker")
    st.markdown(
        "Enter your symptoms below. The system uses **Fuzzy Logic** and "
        "**Random Forest** models with a consensus mechanism to predict the "
        f"most likely tropical disease from **{len(DISEASE_PROFILES)}** conditions."
    )

    tab_predict, tab_about = st.tabs(["🔍 Predict", "ℹ️ About"])

    with tab_predict:
        symptom_values = render_input_form()

        st.markdown("")
        predict_col, clear_col = st.columns([3, 1])

        predict_clicked = predict_col.button(
            "🔍 Predict Disease", type="primary", use_container_width=True
        )
        if clear_col.button("🗑️ Clear", use_container_width=True):
            for key in SYMPTOM_ORDER:
                st.session_state[f"input_{key}"] = None
            st.rerun()

        if predict_clicked:
            if not symptom_values:
                st.warning("⚠️ Please enter at least one symptom value before predicting.")
            elif len(symptom_values) < 3:
                st.warning(
                    f"⚠️ Only {len(symptom_values)} symptom(s) provided. "
                    "Provide at least 3–4 for a meaningful prediction."
                )
            else:
                with st.spinner("Running fuzzy logic & random forest analysis..."):
                    result = consensus_predict(symptom_values)
                render_results(result)

    with tab_about:
        render_about()


if __name__ == "__main__":
    main()
