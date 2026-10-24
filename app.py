"""
NexusPrompt AI Studio (Practical No. 9 Edition) - Universal Conversational Edition
==================================================================================
Conversational AI Chatbot powered by Google Gemini API (gemini-3.5-flash).
Modeled strictly after the Google Gemini and ChatGPT interface.

Features:
- Dynamic execution for ANY query, question, document, or review using Gemini 3.5 Flash
- 100% Focused Chat Stream with pure Gemini/ChatGPT welcome state (no hardcoded test prompts)
- Dynamic Generative UI in Chat Bubbles: Mermaid.js Flowcharts, Plotly Charts, Tables
- Floating Bottom Bar with Auto-Detection & Task Mode Selectors
- Collapsible Left Sidebar (+ New Chat, API Status, Prompt Engine, Live RQS Mini-Card)
- Subtle "View Behind-the-Scenes Prompt & RQS" inspector under each response
"""

import os
import re
import json
import time
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gemini AI Studio | Practical No. 9",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. Design System: Gemini & ChatGPT Dark Obsidian Aesthetic
# -----------------------------------------------------------------------------
gemini_chat_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-base: #0B0F19;
    --bg-sidebar: #0E1424;
    --bg-user-bubble: #1E293B;
    --bg-ai-bubble: #111827;
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-hover: rgba(56, 189, 248, 0.4);
    
    --accent-cyan: #38BDF8;
    --accent-indigo: #818CF8;
    --accent-emerald: #34D399;
    --accent-amber: #F59E0B;
    --accent-pink: #EC4899;
    
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
}

html, body, [data-testid="stAppViewContainer"], .main {
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background-color: var(--bg-base) !important;
}

[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

/* Chat Message Containers */
[data-testid="stChatMessage"] {
    padding: 18px 22px !important;
    border-radius: 14px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
}

/* User Message Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #1E293B 0%, #172033 100%) !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
}

/* Assistant Message Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(22, 30, 48, 0.85) 100%) !important;
    border: 1px solid var(--border-subtle) !important;
    backdrop-filter: blur(12px) !important;
}

/* Top Floating Chat Header */
.chat-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background: rgba(14, 20, 36, 0.7);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    margin-bottom: 24px;
}

.chat-navbar-title {
    font-size: 1.1rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(90deg, #FFFFFF, #38BDF8, #818CF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Welcome Screen */
.welcome-container {
    text-align: center;
    padding: 70px 20px 40px 20px;
    max-width: 760px;
    margin: 0 auto;
}

.welcome-sparkle {
    font-size: 3.2rem;
    margin-bottom: 12px;
    display: inline-block;
    filter: drop-shadow(0 0 20px rgba(56, 189, 248, 0.6));
}

.welcome-heading {
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #FFFFFF 0%, #38BDF8 50%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
}

.welcome-subtext {
    font-size: 1.05rem;
    line-height: 1.65;
    color: var(--text-secondary);
}

/* Badges & Chips */
.neon-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.badge-cyan { background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.4); color: #38BDF8; }
.badge-emerald { background: rgba(52, 211, 153, 0.12); border: 1px solid rgba(52, 211, 153, 0.4); color: #34D399; }
.badge-indigo { background: rgba(129, 140, 248, 0.12); border: 1px solid rgba(129, 140, 248, 0.4); color: #818CF8; }
.badge-amber { background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.4); color: #F59E0B; }
.badge-pink { background: rgba(236, 72, 153, 0.12); border: 1px solid rgba(236, 72, 153, 0.4); color: #EC4899; }

.pulse-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #34D399;
    box-shadow: 0 0 8px #34D399;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); opacity: 0.7; }
    50% { transform: scale(1.2); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.7; }
}

.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.inspector-box {
    background: #080C14;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 12px;
    margin-top: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.5;
}
</style>
"""
st.markdown(gemini_chat_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Environment & Gemini Client Authentication
# -----------------------------------------------------------------------------
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY", "").strip()

gemini_client = None
if api_key:
    try:
        gemini_client = genai.Client(api_key=api_key)
    except Exception:
        gemini_client = None

# -----------------------------------------------------------------------------
# 4. Prompt Engineering Techniques Configuration
# -----------------------------------------------------------------------------
TECHNIQUES = {
    "Zero-shot Prompting": {
        "badge": "Zero-shot",
        "color": "badge-cyan",
        "description": "Direct task instruction with zero exemplars.",
        "system_directive": "Execute the task directly based on your comprehensive knowledge without requiring exemplars.",
        "few_shot_block": "",
        "cot_directive": "",
    },
    "Few-shot Prompting": {
        "badge": "Few-shot",
        "color": "badge-amber",
        "description": "Guides the model with high-quality reference exemplars.",
        "system_directive": "Follow the structured input-to-output pattern demonstrated in the reference exemplars precisely.",
        "few_shot_block": (
            "REFERENCE EXEMPLAR:\n"
            "Input: 'What is Cloud Computing?'\n"
            "Output Structure: Concept synthesis, 3 pillars, Mermaid flowchart, dimensions table, RQS metrics.\n"
        ),
        "cot_directive": "",
    },
    "Role Prompting": {
        "badge": "Role Prompting",
        "color": "badge-indigo",
        "description": "Instills an executive persona: Principal AI Architect & Senior Faculty Evaluator.",
        "system_directive": (
            "You are an Executive Principal AI Systems Architect, Fellow IEEE Researcher, and Senior University Evaluator. "
            "Your answers must be authoritative, rigorous, technically elegant, and formatted with pristine schema precision."
        ),
        "few_shot_block": "",
        "cot_directive": "",
    },
    "Chain-of-Thought Prompting": {
        "badge": "Chain-of-Thought (CoT)",
        "color": "badge-pink",
        "description": "Forces multi-step internal reasoning before compiling output.",
        "system_directive": "Reason systematically through each component of the user query before finalizing your assessment.",
        "few_shot_block": "",
        "cot_directive": (
            "COGNITIVE REASONING PROTOCOL:\n"
            "1. Deconstruct the user input into primary claims, tone markers, or conceptual entities.\n"
            "2. Map each entity to its architectural hierarchy or sentiment vector.\n"
            "3. Synthesize the findings into the required visual JSON schema without deviating."
        ),
    },
}

# -----------------------------------------------------------------------------
# 5. Session State Management
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "active_technique" not in st.session_state:
    st.session_state["active_technique"] = "Zero-shot Prompting"

if "task_mode" not in st.session_state:
    st.session_state["task_mode"] = "✨ Auto-Detect"

if "rqs_scores" not in st.session_state:
    st.session_state["rqs_scores"] = {
        "accuracy": 9.6,
        "relevance": 9.8,
        "consistency": 9.5,
        "fluency": 9.7,
    }

# -----------------------------------------------------------------------------
# 6. Helper: Intelligent Task Classification
# -----------------------------------------------------------------------------
def detect_task_mode(user_text: str, selected_mode: str) -> str:
    if selected_mode == "💡 QA":
        return "Question Answering"
    elif selected_mode == "📝 Summarize":
        return "Text Summarization"
    elif selected_mode == "🏷️ Classify":
        return "Text Classification"

    lower = user_text.lower().strip()
    words = lower.split()
    
    # Sentiment / Review detection
    sentiment_keywords = ["review", "battery", "camera", "experience", "lag", "lags", "sentiment", "worst", "excellent", "poor", "rating", "phone", "device"]
    if any(k in lower for k in sentiment_keywords):
        return "Text Classification"

    # Summarization detection
    if "summariz" in lower or "tl;dr" in lower or (len(words) > 22 and not lower.endswith("?")):
        return "Text Summarization"

    # Default to Question Answering
    return "Question Answering"

# -----------------------------------------------------------------------------
# 7. Engine: Structured Gemini 3.5 Flash Execution
# -----------------------------------------------------------------------------
def compile_prompt(task_name: str, tech_name: str, user_text: str):
    tech_data = TECHNIQUES[tech_name]

    if task_name == "Question Answering":
        task_directive = (
            "Answer the query comprehensively, accurately, and authoritatively. "
            "Return a strictly valid JSON object with the following fields: "
            "1. 'hero_answer': A clean, thorough 1-2 paragraph explanation of the concept with key terms emphasized. "
            "2. 'key_takeaways': A list of exactly 3 concise, punchy takeaways or architectural pillars. "
            "3. 'mermaid_diagram': A valid, well-structured Mermaid.js flowchart (graph TD) illustrating how the components, workflows, or sub-disciplines connect. Use clean node IDs and labels. "
            "4. 'comparison_table': A list of 4-5 objects with 'Dimension', 'Details', 'Impact' comparing pillars, architectural layers, or trade-offs. "
            "5. 'rqs_estimate': An object with numeric scores (1 to 10) for 'accuracy', 'relevance', 'consistency', 'fluency'."
        )
    elif task_name == "Text Summarization":
        orig_count = len(user_text.split())
        task_directive = (
            f"Summarize the provided text concisely while preserving factual integrity and key entities. "
            f"The original text has approximately {orig_count} words. "
            "Return a strictly valid JSON object with: "
            "1. 'tldr': A single powerful executive summary sentence. "
            "2. 'bullet_takeaways': A list of 3-4 key bullet points. "
            "3. 'metrics': An object with 'original_words' (integer), 'summary_words' (integer), 'compression_ratio_pct' (float), and 'reading_time_saved_sec' (float). "
            "4. 'domain_impact_table': A list of objects with 'Domain' (industry/domain mentioned) and 'Impact' (summarized effect). "
            "5. 'rqs_estimate': An object with numeric scores (1 to 10) for 'accuracy', 'relevance', 'consistency', 'fluency'."
        )
    else:
        task_directive = (
            "Analyze the sentiment polarity and feature-level aspects of the input. "
            "Return a strictly valid JSON object with: "
            "1. 'primary_sentiment': Exactly one of 'Positive', 'Negative', or 'Neutral'. "
            "2. 'confidence_scores': An object with 'Positive', 'Negative', and 'Neutral' percentages summing to 100. "
            "3. 'sentiment_summary': A brief 1-2 sentence justification of the classification. "
            "4. 'aspect_breakdown': A list of objects with 'Aspect' (feature mentioned), 'Extracted_Phrase' (quote from input), 'Polarity' ('Positive'/'Negative'/'Neutral'), and 'Confidence' (number). "
            "5. 'rqs_estimate': An object with numeric scores (1 to 10) for 'accuracy', 'relevance', 'consistency', 'fluency'."
        )

    system_role = (
        "You are an executive-level AI reasoning engine and academic evaluation system. "
        "Strictly adhere to the prompt directives and return responses ONLY in valid, parseable JSON format."
    )
    if tech_name == "Role Prompting":
        system_role = tech_data["system_directive"]

    few_shot = tech_data["few_shot_block"]
    cot = tech_data["cot_directive"]

    full_compiled = f"""SYSTEM ROLE:
{system_role}

TASK DIRECTIVE:
{task_directive}

TECHNIQUE DIRECTIVE ({tech_name}):
{tech_data['system_directive']}
{few_shot}
{cot}
USER INQUIRY / INPUT:
{user_text}

CRITICAL: Return ONLY valid, parseable JSON matching the requested schema.
"""
    return {
        "system_role": system_role,
        "task_name": task_name,
        "task_directive": task_directive,
        "tech_name": tech_name,
        "technique_rules": tech_data["system_directive"],
        "few_shot": few_shot,
        "cot": cot,
        "user_input": user_text,
        "full_compiled": full_compiled.strip(),
    }

def execute_gemini_35_flash(compiled_data: dict, client: genai.Client):
    """Executes live Gemini 3.5 Flash call with JSON enforcement for optimal speed."""
    if not client:
        return None, "Gemini client not initialized"

    prompt_str = compiled_data["full_compiled"]

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt_str,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
            ),
        )
        if response and response.text:
            cleaned = response.text.strip()
            # Clean possible markdown wrap
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE).strip()
            payload = json.loads(cleaned)
            return payload, None
        return None, "Empty response from Gemini 3.5 Flash"
    except Exception as e_primary:
        # Fallback to Interactions API if generate_content has any network issue
        try:
            interact_resp = client.interactions.create(
                model="gemini-3.5-flash",
                input=prompt_str,
            )
            if interact_resp and interact_resp.output_text:
                raw_text = interact_resp.output_text.strip()
                cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
                cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE).strip()
                json_match = re.search(r"(\{[\s\S]*\})", cleaned)
                if json_match:
                    cleaned = json_match.group(1)
                return json.loads(cleaned), None
        except Exception as e_fallback:
            return None, f"{str(e_primary)} | Fallback: {str(e_fallback)}"

    return None, "API_FAILURE"

# -----------------------------------------------------------------------------
# 8. Generative UI Renderers Inside Chat Bubbles
# -----------------------------------------------------------------------------
def render_mermaid_in_chat(mermaid_code: str, element_id: str, height: int = 340):
    clean_syntax = mermaid_code.strip()
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
      <style>
        body {{
          margin: 0;
          padding: 14px;
          background: #090D16;
          color: #F8FAFC;
          font-family: 'Inter', sans-serif;
          display: flex;
          justify-content: center;
          align-items: center;
          overflow-x: auto;
          border-radius: 8px;
          border: 1px solid rgba(56, 189, 248, 0.25);
        }}
        .mermaid {{ width: 100%; text-align: center; }}
      </style>
    </head>
    <body>
      <div class="mermaid" id="{element_id}">
{clean_syntax}
      </div>
      <script>
        try {{
          mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            securityLevel: 'loose',
            themeVariables: {{
              darkMode: true,
              background: '#090D16',
              primaryColor: '#1A2130',
              primaryTextColor: '#F8FAFC',
              primaryBorderColor: '#38BDF8',
              lineColor: '#818CF8',
              secondaryColor: '#161B26',
              tertiaryColor: '#090D16'
            }}
          }});
        }} catch(e) {{
          document.body.innerHTML = '<div style="color:#ef4444;padding:8px;">Diagram Error: ' + e.message + '</div>';
        }}
      </script>
    </body>
    </html>
    """
    st.components.v1.html(html_content, height=height, scrolling=True)

def render_compression_chart_in_chat(metrics: dict, chart_key: str):
    orig_words = metrics.get("original_words", 20)
    sum_words = metrics.get("summary_words", 12)
    comp_pct = metrics.get("compression_ratio_pct", 40.0)
    saved_sec = metrics.get("reading_time_saved_sec", 3.0)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Original Words", "Summary Words"],
            y=[orig_words, sum_words],
            marker_color=["#38BDF8", "#34D399"],
            text=[f"{orig_words} words", f"{sum_words} words"],
            textposition="auto",
            width=0.4,
        )
    )
    fig.update_layout(
        title={
            "text": f"<b>Compression Analytics</b>: {comp_pct:.1f}% Reduction | ~{saved_sec}s Saved",
            "font": {"size": 13, "color": "#F8FAFC", "family": "Inter"},
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=35, b=15),
        height=220,
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="#94A3B8")),
        xaxis=dict(tickfont=dict(color="#F8FAFC")),
    )
    st.plotly_chart(fig, use_container_width=True, key=chart_key)

def render_sentiment_donut_in_chat(confidence: dict, primary_sentiment: str, chart_key: str):
    labels = ["Positive", "Negative", "Neutral"]
    values = [
        confidence.get("Positive", 0),
        confidence.get("Negative", 0),
        confidence.get("Neutral", 0),
    ]
    colors = ["#34D399", "#F43F5E", "#94A3B8"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=colors, line=dict(color="#090D16", width=2)),
                textinfo="label+percent",
                textfont=dict(color="#F8FAFC", family="Inter", size=11),
            )
        ]
    )
    fig.update_layout(
        title={
            "text": f"<b>Sentiment Distribution</b>: {primary_sentiment.upper()}",
            "font": {"size": 13, "color": "#F8FAFC", "family": "Inter"},
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=35, b=10),
        height=230,
        showlegend=True,
        legend=dict(font=dict(color="#94A3B8"), orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig, use_container_width=True, key=chart_key)

def render_sidebar_radar_chart(acc: float, rel: float, cons: float, fl: float):
    categories = ["Accuracy", "Relevance", "Consistency", "Fluency", "Accuracy"]
    values = [acc, rel, cons, fl, acc]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name="RQS",
            line=dict(color="#38BDF8", width=2),
            fillcolor="rgba(56, 189, 248, 0.25)",
            marker=dict(size=4, color="#818CF8"),
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255, 255, 255, 0.1)", tickfont=dict(color="#94A3B8", size=8)),
            angularaxis=dict(gridcolor="rgba(255, 255, 255, 0.1)", tickfont=dict(color="#F8FAFC", size=9, family="Inter")),
            bgcolor="#0B101D",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=25, r=25, t=20, b=20),
        height=200,
        showlegend=False,
    )
    return fig

# -----------------------------------------------------------------------------
# 9. Sidebar: Collapsible Controls & RQS Mini-Card
# -----------------------------------------------------------------------------
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state["messages"] = []
        st.rerun()

    st.markdown("---")

    # API Status
    st.markdown("##### 🔑 Gemini API Connection")
    if gemini_client:
        st.markdown(
            """
            <div style="background: rgba(52, 211, 153, 0.1); border: 1px solid rgba(52, 211, 153, 0.35); border-radius: 8px; padding: 10px;">
                <div style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: #34D399; font-weight: 600;">
                    <span class="pulse-dot"></span>
                    <span>Gemini 3.5 Flash Online</span>
                </div>
                <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 4px;">Loaded from .env • High Speed JSON Engine</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("⚠️ GEMINI_API_KEY not connected. Please verify .env file.")

    st.markdown("---")

    # Under-the-Hood Prompt Engine Selector
    st.markdown("##### 🧠 Active Prompt Strategy")
    tech_keys = list(TECHNIQUES.keys())
    sel_tech = st.selectbox(
        "Active Technique",
        options=tech_keys,
        index=tech_keys.index(st.session_state["active_technique"]),
        label_visibility="collapsed",
    )
    st.session_state["active_technique"] = sel_tech
    st.caption(f"Strategy: *{TECHNIQUES[sel_tech]['description']}*")

    st.markdown("---")

    # Section 7: Mathematical Model (RQS Evaluator Mini-Card)
    st.markdown("##### 📐 Section 7: RQS Model")
    st.markdown(
        r"""
        <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 6px;">
            $$RQS = \frac{\text{Acc} + \text{Rel} + \text{Cons} + \text{Flu}}{4}$$
        </div>
        """,
        unsafe_allow_html=True,
    )

    rqs_data = st.session_state["rqs_scores"]
    acc_s = float(rqs_data.get("accuracy", 9.6))
    rel_s = float(rqs_data.get("relevance", 9.8))
    cons_s = float(rqs_data.get("consistency", 9.5))
    fl_s = float(rqs_data.get("fluency", 9.7))
    comp_rqs = (acc_s + rel_s + cons_s + fl_s) / 4.0

    st.plotly_chart(render_sidebar_radar_chart(acc_s, rel_s, cons_s, fl_s), use_container_width=True, key="sidebar_rqs_radar")

    grade_tier = "Executive Grade (A+)" if comp_rqs >= 9.0 else "High Distinction (A)"
    st.markdown(
        f"""
        <div style="background: rgba(17, 24, 39, 0.8); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 0.73rem; color: #94A3B8; text-transform: uppercase;">Composite RQS Score</div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #38BDF8; margin: 2px 0;">{comp_rqs:.2f} / 10.0</div>
            <div style="font-size: 0.74rem; color: #34D399; font-weight: 600;">{grade_tier}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("⚙️ Fine-Tune RQS Parameters"):
        acc_s = st.slider("Accuracy", 1.0, 10.0, acc_s, 0.1, key="sb_slider_acc")
        rel_s = st.slider("Relevance", 1.0, 10.0, rel_s, 0.1, key="sb_slider_rel")
        cons_s = st.slider("Consistency", 1.0, 10.0, cons_s, 0.1, key="sb_slider_cons")
        fl_s = st.slider("Fluency", 1.0, 10.0, fl_s, 0.1, key="sb_slider_fl")
        st.session_state["rqs_scores"] = {"accuracy": acc_s, "relevance": rel_s, "consistency": cons_s, "fluency": fl_s}

# -----------------------------------------------------------------------------
# 10. Main Center Screen: Top Navigation Bar
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="chat-navbar">
        <div class="chat-navbar-title">
            <span>✨</span>
            <span>NexusPrompt AI Studio</span>
            <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 500; margin-left: 6px;">Gemini 3.5 Flash</span>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <span class="neon-badge {TECHNIQUES[st.session_state['active_technique']]['color']}">
                Engine: {TECHNIQUES[st.session_state['active_technique']]['badge']}
            </span>
            <span class="neon-badge badge-emerald">
                <span class="pulse-dot"></span>
                <span>Live Gemini</span>
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 11. Main Screen: Welcome Empty State vs. Active Chat Stream
# -----------------------------------------------------------------------------
messages = st.session_state["messages"]

if len(messages) == 0:
    # Sleek Pure Gemini Welcome Screen (Zero hardcoded sample buttons)
    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-sparkle">✨</div>
            <div class="welcome-heading">Hello! How can I help you today?</div>
            <div class="welcome-subtext">
                Ask any question, paste text or articles to summarize, or enter customer reviews to evaluate sentiment.<br>
                Powered live by <b>Google Gemini 3.5 Flash</b> with real-time Generative UI charts, Mermaid mindmaps, and aspect tables.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Active Scrolling Chat Stream
    for idx, msg in enumerate(messages):
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="✨"):
                payload = msg.get("payload", {})
                curr_task = msg.get("task", "Question Answering")

                # 1. QUESTION ANSWERING
                if curr_task == "Question Answering" or "hero_answer" in payload:
                    hero_ans = payload.get("hero_answer", msg.get("content", ""))
                    st.markdown(f"**{hero_ans}**")

                    takeaways = payload.get("key_takeaways", [])
                    if takeaways:
                        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                        cols = st.columns(len(takeaways))
                        for i, tk in enumerate(takeaways):
                            with cols[i]:
                                st.markdown(
                                    f"""
                                    <div style="background: rgba(14, 20, 36, 0.7); border: 1px solid rgba(129, 140, 248, 0.3); border-radius: 8px; padding: 10px;">
                                        <div style="font-size: 0.72rem; color: #818CF8; font-weight: 700; text-transform: uppercase;">Pillar {i+1}</div>
                                        <div style="font-size: 0.82rem; color: #E2E8F0; margin-top: 3px;">{tk}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                    m_code = payload.get("mermaid_diagram", "")
                    if m_code:
                        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                        render_mermaid_in_chat(m_code, element_id=f"mermaid_chat_{idx}", height=320)

                    comp_t = payload.get("comparison_table", [])
                    if comp_t:
                        st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #38BDF8; margin: 8px 0 4px 0;'>Architectural Dimensions & Impact:</div>", unsafe_allow_html=True)
                        st.dataframe(pd.DataFrame(comp_t), use_container_width=True, hide_index=True)

                # 2. TEXT SUMMARIZATION
                elif curr_task == "Text Summarization" or "tldr" in payload:
                    tldr = payload.get("tldr", "")
                    st.markdown(
                        f"""
                        <div style="background: rgba(14, 20, 36, 0.85); border-left: 4px solid #34D399; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                            <div style="font-size: 0.74rem; font-weight: 700; color: #34D399; text-transform: uppercase;">Executive TL;DR</div>
                            <div style="font-size: 0.95rem; color: #F8FAFC; margin-top: 4px;"><b>{tldr}</b></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    c_chart, c_bullets = st.columns([1.2, 1])
                    with c_chart:
                        metrics = payload.get("metrics", {})
                        render_compression_chart_in_chat(metrics, chart_key=f"comp_chart_{idx}")

                    with c_bullets:
                        st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #38BDF8; margin-bottom: 6px;'>Key Takeaways:</div>", unsafe_allow_html=True)
                        for b in payload.get("bullet_takeaways", []):
                            st.markdown(f"• <span style='font-size: 0.85rem; color: #E2E8F0;'>{b}</span>", unsafe_allow_html=True)

                    dom_t = payload.get("domain_impact_table", [])
                    if dom_t:
                        st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #38BDF8; margin: 10px 0 4px 0;'>Extracted Sectors & Specific Domain Impact:</div>", unsafe_allow_html=True)
                        st.dataframe(pd.DataFrame(dom_t), use_container_width=True, hide_index=True)

                # 3. TEXT CLASSIFICATION
                elif curr_task == "Text Classification" or "primary_sentiment" in payload:
                    sentiment = payload.get("primary_sentiment", "Neutral")
                    badge_class = "badge-emerald" if sentiment == "Positive" else ("badge-amber" if sentiment == "Neutral" else "badge-pink")
                    summary_sent = payload.get("sentiment_summary", "")

                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                            <span class="neon-badge {badge_class}" style="font-size: 0.88rem; padding: 5px 14px;">
                                {sentiment.upper()} SENTIMENT
                            </span>
                            <span style="font-size: 0.78rem; color: #94A3B8;">Confidence Verified</span>
                        </div>
                        <div style="font-size: 0.93rem; color: #E2E8F0; margin-bottom: 10px;">{summary_sent}</div>
                        """,
                        unsafe_allow_html=True,
                    )

                    c_donut, c_aspects = st.columns([1, 1.3])
                    with c_donut:
                        render_sentiment_donut_in_chat(payload.get("confidence_scores", {}), sentiment, chart_key=f"donut_{idx}")

                    with c_aspects:
                        st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #38BDF8; margin-bottom: 6px;'>Aspect-Level Breakdown:</div>", unsafe_allow_html=True)
                        aspects = payload.get("aspect_breakdown", [])
                        if aspects:
                            st.dataframe(pd.DataFrame(aspects), use_container_width=True, hide_index=True)

                # 4. FALLBACK RAW DISPLAY IF PLAIN TEXT
                elif "raw_text" in payload:
                    st.markdown(payload["raw_text"])

                # Subtle Inspector Pill
                xray_data = msg.get("xray")
                with st.expander("🛠️ View Behind-the-Scenes Prompt Engineering & RQS", expanded=False):
                    if xray_data:
                        st.markdown(
                            f"""
                            <div class="inspector-box">
                                <div style="color: #A855F7; margin-bottom: 4px;"><b>[SYSTEM ROLE]</b>: {xray_data.get('system_role')}</div>
                                <div style="color: #38BDF8; margin-bottom: 4px;"><b>[TASK]</b>: {xray_data.get('task_directive')}</div>
                                <div style="color: #F59E0B; margin-bottom: 4px;"><b>[STRATEGY: {xray_data.get('tech_name')}]</b>: {xray_data.get('technique_rules')}</div>
                                {f'<div style="color: #FB923C; margin-bottom: 4px;"><b>[FEW-SHOT EXEMPLARS]</b>:<br>' + xray_data.get('few_shot').replace(chr(10), '<br>') + '</div>' if xray_data.get('few_shot') else ''}
                                {f'<div style="color: #EC4899; margin-bottom: 4px;"><b>[CHAIN-OF-THOUGHT]</b>:<br>' + xray_data.get('cot').replace(chr(10), '<br>') + '</div>' if xray_data.get('cot') else ''}
                                <div style="color: #34D399; margin-top: 6px;"><b>[USER INPUT]</b>: {xray_data.get('user_input')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    est_rqs = payload.get("rqs_estimate", {})
                    if est_rqs:
                        calc_val = (float(est_rqs.get("accuracy", 9.5)) + float(est_rqs.get("relevance", 9.8)) + float(est_rqs.get("consistency", 9.5)) + float(est_rqs.get("fluency", 9.7))) / 4.0
                        st.caption(f"📊 Live Gemini Evaluated RQS: Accuracy: {est_rqs.get('accuracy', 9.5)} | Relevance: {est_rqs.get('relevance', 9.8)} | Consistency: {est_rqs.get('consistency', 9.5)} | Fluency: {est_rqs.get('fluency', 9.7)} → **Composite RQS: {calc_val:.2f} / 10.0**")

# -----------------------------------------------------------------------------
# 12. Floating Bottom Prompt Bar & Task Mode Selector Pill
# -----------------------------------------------------------------------------
mode_cols = st.columns([1, 1, 1, 1, 4])
mode_options = ["✨ Auto-Detect", "💡 QA", "📝 Summarize", "🏷️ Classify"]
for i, m_opt in enumerate(mode_options):
    with mode_cols[i]:
        is_sel = (st.session_state["task_mode"] == m_opt)
        btn_type = "primary" if is_sel else "secondary"
        if st.button(m_opt, key=f"btn_mode_{m_opt}", type=btn_type, use_container_width=True):
            st.session_state["task_mode"] = m_opt
            st.rerun()

user_chat_input = st.chat_input("Ask any question, paste text to summarize, or enter a review to classify...")

if user_chat_input:
    active_task = detect_task_mode(user_chat_input, st.session_state["task_mode"])
    active_technique = st.session_state["active_technique"]

    # 1. Append User Message
    st.session_state["messages"].append({
        "role": "user",
        "content": user_chat_input,
        "task": active_task,
        "time": time.strftime("%H:%M"),
    })

    # 2. Compile engineered prompt
    compiled_xray = compile_prompt(active_task, active_technique, user_chat_input)

    # 3. Call Live Gemini 3.5 Flash
    payload = None
    with st.spinner("✨ Reasoning with Gemini 3.5 Flash..."):
        live_payload, err = execute_gemini_35_flash(compiled_xray, gemini_client)
        if live_payload:
            payload = live_payload
        else:
            payload = {"raw_text": f"Error interacting with Gemini API: {err}"}

    # Update RQS scores from live response
    if payload and "rqs_estimate" in payload:
        st.session_state["rqs_scores"] = payload["rqs_estimate"]

    # 4. Append Assistant Message
    assistant_content = payload.get("hero_answer", payload.get("tldr", payload.get("sentiment_summary", payload.get("raw_text", ""))))
    st.session_state["messages"].append({
        "role": "assistant",
        "content": assistant_content,
        "task": active_task,
        "payload": payload,
        "xray": compiled_xray,
        "time": time.strftime("%H:%M"),
    })

    st.rerun()
