import os
import re
import json
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai

# --------------------------------------------------
# 1. Page Configuration & Meta
# --------------------------------------------------

st.set_page_config(
    page_title="Executive AI Reasoning Console",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# 2. Executive-Grade Monochromatic Slate & Zinc Design System
# --------------------------------------------------

design_system_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-primary: #0B0F17;
    --bg-secondary: #0E131E;
    --bg-surface: #121620;
    --bg-card: #161B26;
    --bg-card-hover: #1A2130;
    --bg-user-bubble: #1A2232;
    
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-card: rgba(255, 255, 255, 0.1);
    --border-hover: rgba(255, 255, 255, 0.18);
    --border-accent: #4F75FF;
    
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --text-user: #FFFFFF;
    
    --accent-steel: #4F75FF;
    --accent-periwinkle: #6366F1;
    --accent-emerald: #10B981;
}

/* Base Viewport & Theme Lockdown */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* Eliminate White Bar at Bottom: Force Dark Canvas */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] footer,
.stChatFloatingInputContainer,
[data-testid="stChatInputContainer"] {
    background-color: var(--bg-primary) !important;
    background: var(--bg-primary) !important;
}

footer {
    display: none !important;
    visibility: hidden !important;
}

/* Fix Material Icons / Ligature Display */
.material-symbols-rounded,
.material-symbols-sharp,
.material-symbols-outlined,
[class*="material-symbols"] {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    font-style: normal !important;
    font-weight: normal !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    display: inline-block !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
}

/* Sidebar: Deep Zinc & Slate */
[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] hr {
    border-color: var(--border-subtle) !important;
    margin: 18px 0;
}

/* Typography Hierarchy */
h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
}

p, li, td {
    font-family: 'Inter', sans-serif !important;
    line-height: 1.65 !important;
    color: #E2E8F0 !important;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9em !important;
}

/* Link Chips (Clean external citation styling) */
a {
    color: #818CF8 !important;
    text-decoration: none !important;
    padding: 2px 8px !important;
    border-radius: 6px !important;
    background: rgba(99, 102, 241, 0.08) !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
    transition: all 0.2s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
}
a:hover {
    background: rgba(99, 102, 241, 0.18) !important;
    border-color: rgba(99, 102, 241, 0.45) !important;
    color: #C7D2FE !important;
}

/* Header Banner */
.console-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 24px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    margin-bottom: 22px;
}

.console-title-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.console-title {
    font-size: 1.18rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 10px;
}

.console-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-subtle);
    color: var(--text-secondary);
}

.status-indicator {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--accent-emerald);
}

.console-meta-chip {
    font-size: 0.8rem;
    color: var(--text-muted);
}

/* Chat Message Containers */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
}

/* User Message: Dark Steel Container */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: var(--bg-user-bubble) !important;
    border: 1px solid rgba(79, 117, 255, 0.25) !important;
}

/* Assistant Message: Deep Slate Edge-to-Edge */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
}

/* Clean Markdown Tables */
table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 16px 0 !important;
    font-size: 0.92rem !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

th {
    background: #1A2130 !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    text-align: left !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid var(--border-card) !important;
}

td {
    padding: 10px 14px !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    color: #CBD5E1 !important;
}

tr:hover td {
    background-color: rgba(255, 255, 255, 0.02) !important;
}

/* Input Area Restyling */
[data-testid="stChatInput"] {
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent-steel) !important;
    box-shadow: 0 0 0 1px var(--accent-steel) !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
}

/* Button & Action Styling */
.stButton > button {
    background-color: #161B26 !important;
    color: #F1F5F9 !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 6px 14px !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    background-color: #202738 !important;
    border-color: var(--border-hover) !important;
    color: #FFFFFF !important;
}

.stDownloadButton > button {
    background-color: #161B26 !important;
    color: #F1F5F9 !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
}

.stDownloadButton > button:hover {
    background-color: #202738 !important;
    color: #FFFFFF !important;
    border-color: var(--border-hover) !important;
}

/* Attachment Pill */
.attachment-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: #161B26;
    border: 1px solid rgba(79, 117, 255, 0.3);
    border-radius: 8px;
    margin-bottom: 12px;
    font-size: 0.82rem;
    color: #C7D2FE;
}
</style>
"""
st.markdown(design_system_css, unsafe_allow_html=True)

# --------------------------------------------------
# 3. Environment & Gemini Client Authentication
# --------------------------------------------------

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Authentication Key Error: GEMINI_API_KEY not found in environment. Please verify your .env file.")
    st.stop()

# Initialize Gemini Client (preserving SDK architecture)
client = genai.Client(api_key=api_key)

# --------------------------------------------------
# 4. Prompt Presets & System Instructions Configuration
# --------------------------------------------------

PRESETS = {
    "Question Answering": {
        "title": "QA Mode (Accurate Q&A)",
        "subtitle": "Precision-focused inquiries with technical depth and direct answers.",
        "default_prompt": "What is cloud computing? Explain its core architectural models and benefits.",
        "task_instruction": (
            "Answer the question accurately, clearly, and concisely. Use simple language when appropriate. "
            "Whenever presenting comparisons or data metrics, structure them into Markdown Tables or JSON ```chart blocks. "
            "Whenever explaining algorithms, workflows, or architectural pipelines, deliver the sequence using valid ```mermaid flowcharts."
        ),
    },
    "Text Summarization": {
        "title": "Document Summarization",
        "subtitle": "Condenses complex texts preserving factual integrity and key takeaways.",
        "default_prompt": (
            "Cloud computing provides on-demand availability of system resources, especially data storage "
            "and computing power, without direct active management by the user. Large clouds often have functions "
            "distributed over multiple locations, each of which is a data center. It relies on sharing of resources "
            "to achieve coherence and typically uses a 'pay as you go' model, which can help in reducing capital expenditure "
            "but may also lead to unexpected operating expenses for users."
        ),
        "task_instruction": (
            "Summarize the supplied text, preserving core ideas and data points without adding unsupported information. "
            "Structure takeaways with clear headings, bullet points, and an executive summary table if appropriate."
        ),
    },
    "Text Classification": {
        "title": "Sentiment & Review Classification",
        "subtitle": "Multi-dimensional sentiment, tonality, and intent classification.",
        "default_prompt": "I love this product. It is easy to use and works perfectly for our engineering team.",
        "task_instruction": (
            "Classify the sentiment into Positive, Negative, or Neutral. "
            "Provide the primary classification label, confidence assessment, and a structured breakdown table "
            "justifying the key emotional or tonal indicators in the text."
        ),
    },
}

TECHNIQUE_INSTRUCTIONS = {
    "Zero-shot Prompting": "Perform the task directly without few-shot exemplars.",
    "Role Prompting": "Act as an executive-level technical consultant and principal systems architect providing clear, professional counsel.",
    "Step-by-step Explanation": "Provide the final output accompanied by a structured breakdown of each logical stage or operational reason. Do not expose unformatted internal scratchpads.",
}

# --------------------------------------------------
# 5. Session State Management
# --------------------------------------------------

if "active_preset" not in st.session_state:
    st.session_state["active_preset"] = "Question Answering"

if "active_technique" not in st.session_state:
    st.session_state["active_technique"] = "Zero-shot Prompting"

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": (
                "Welcome to the **Executive AI Reasoning Console**. "
                "I am equipped to execute Question Answering, Document Summarization, and Sentiment Classification.\n\n"
                "Responses are rendered dynamically with formatted Markdown tables, Chart.js visualizations, "
                "and vector Mermaid.js flowcharts where relevant."
            ),
            "timestamp": time.strftime("%H:%M"),
        }
    ]

# --------------------------------------------------
# 6. Sidebar: Workspace Presets & Session History
# --------------------------------------------------

with st.sidebar:
    st.markdown("### ⚡ Executive AI Console")
    st.caption("Gemini 3.8 Flash • Interactions Engine")
    
    st.markdown("---")
    st.markdown("#### Operational Presets")
    
    for task_key, p_data in PRESETS.items():
        is_selected = (st.session_state["active_preset"] == task_key)
        button_label = f"{'● ' if is_selected else '○ '}{p_data['title']}"
        if st.button(button_label, key=f"btn_preset_{task_key}", use_container_width=True):
            st.session_state["active_preset"] = task_key
            st.rerun()

    st.markdown("---")
    st.markdown("#### Prompting Technique")
    
    selected_technique = st.selectbox(
        "Select Technique",
        options=list(TECHNIQUE_INSTRUCTIONS.keys()),
        index=list(TECHNIQUE_INSTRUCTIONS.keys()).index(st.session_state["active_technique"]),
        label_visibility="collapsed",
    )
    st.session_state["active_technique"] = selected_technique
    st.caption(f"Strategy: *{TECHNIQUE_INSTRUCTIONS[selected_technique]}*")

    st.markdown("---")
    st.markdown("#### Document Attachment 📎")
    uploaded_file = st.file_uploader(
        "Attach context for summarization/analysis",
        type=["txt", "md", "csv"],
        help="Upload text documents to inject directly into your next prompt.",
    )
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.read().decode("utf-8", errors="ignore")
            st.session_state["attached_filename"] = uploaded_file.name
            st.session_state["attached_content"] = file_content
            st.caption(f"Ready: `{uploaded_file.name}` ({len(file_content)} chars)")
        except Exception:
            st.warning("Could not read uploaded text.")

    st.markdown("---")
    if st.button("🗑️ Clear Session History", use_container_width=True):
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Session history cleared. Ready for your instructions.",
                "timestamp": time.strftime("%H:%M"),
            }
        ]
        st.session_state.pop("attached_content", None)
        st.session_state.pop("attached_filename", None)
        st.rerun()

# --------------------------------------------------
# 7. Helper: Rich Dynamic Response Rendering (Markdown, Mermaid, Chart.js)
# --------------------------------------------------

def render_mermaid(diagram_syntax: str, element_id: str):
    """Renders Mermaid.js diagrams inside a contained dark iframe."""
    clean_code = diagram_syntax.strip()
    html_markup = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
      <style>
        body {{
          margin: 0;
          padding: 16px;
          background-color: #121620;
          color: #F8FAFC;
          font-family: 'Inter', sans-serif;
          display: flex;
          justify-content: center;
          align-items: center;
          overflow-x: auto;
          border-radius: 8px;
          border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .mermaid {{
          width: 100%;
          text-align: center;
        }}
      </style>
    </head>
    <body>
      <div class="mermaid" id="{element_id}">
{clean_code}
      </div>
      <script>
        mermaid.initialize({{
          startOnLoad: true,
          theme: 'dark',
          themeVariables: {{
            darkMode: true,
            background: '#121620',
            primaryColor: '#1A2130',
            primaryTextColor: '#F8FAFC',
            primaryBorderColor: 'rgba(255, 255, 255, 0.15)',
            lineColor: '#4F75FF',
            secondaryColor: '#161B26',
            tertiaryColor: '#0B0F17'
          }}
        }});
      </script>
    </body>
    </html>
    """
    st.components.v1.html(html_markup, height=360, scrolling=True)

def render_chart_js(chart_json_str: str, element_id: str):
    """Parses and renders interactive Chart.js visualizations in the monochromatic palette."""
    html_markup = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <style>
        body {{
          margin: 0;
          padding: 18px;
          background-color: #121620;
          border-radius: 8px;
          border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .chart-box {{
          position: relative;
          height: 290px;
          width: 100%;
        }}
      </style>
    </head>
    <body>
      <div class="chart-box">
        <canvas id="{element_id}"></canvas>
      </div>
      <script>
        try {{
          const config = {chart_json_str.strip()};
          if (!config.options) config.options = {{}};
          config.options.responsive = true;
          config.options.maintainAspectRatio = false;
          
          // Apply monochromatic theme colors if missing
          const defaultColors = ['#4F75FF', '#6366F1', '#38BDF8', '#818CF8', '#94A3B8'];
          if (config.data && config.data.datasets) {{
            config.data.datasets.forEach((ds, idx) => {{
              if (!ds.backgroundColor) {{
                ds.backgroundColor = defaultColors[idx % defaultColors.length];
              }}
              if (!ds.borderColor) {{
                ds.borderColor = 'rgba(255, 255, 255, 0.15)';
              }}
            }});
          }}
          
          if (!config.options.plugins) config.options.plugins = {{}};
          if (!config.options.plugins.legend) {{
            config.options.plugins.legend = {{ labels: {{ color: '#94A3B8', font: {{ family: 'Inter' }} }} }};
          }}
          
          new Chart(document.getElementById('{element_id}'), config);
        }} catch(err) {{
          document.body.innerHTML = '<div style="color:#ef4444;font-family:sans-serif;font-size:12px;padding:12px;">Chart parse error: ' + err.message + '</div>';
        }}
      </script>
    </body>
    </html>
    """
    st.components.v1.html(html_markup, height=330, scrolling=False)

def render_rich_content(content: str, message_idx: int):
    """
    Parses content for ```mermaid and ```chart blocks, rendering interactive
    canvases while leaving standard Markdown tables and text formatted.
    """
    pattern = re.compile(r"```(mermaid|chart)\n([\s\S]*?)\n```", re.IGNORECASE)
    last_pos = 0
    sub_id = 0

    for match in pattern.finditer(content):
        text_before = content[last_pos:match.start()].strip()
        if text_before:
            st.markdown(text_before)

        block_type = match.group(1).lower()
        block_body = match.group(2)
        unique_id = f"block_{message_idx}_{sub_id}"

        if block_type == "mermaid":
            render_mermaid(block_body, unique_id)
        elif block_type == "chart":
            render_chart_js(block_body, unique_id)

        sub_id += 1
        last_pos = match.end()

    trailing_text = content[last_pos:].strip()
    if trailing_text:
        st.markdown(trailing_text)

# --------------------------------------------------
# 8. Prompt Construction & Resilient Gemini Request
# --------------------------------------------------

def build_structured_prompt(task_name: str, technique_name: str, user_input: str, attachment: str = None) -> str:
    task_info = PRESETS[task_name]["task_instruction"]
    tech_info = TECHNIQUE_INSTRUCTIONS[technique_name]
    
    attachment_block = f"\n\nATTACHED CONTEXT:\n{attachment}" if attachment else ""

    prompt = f"""
You are an executive-level AI reasoning system.

CORE OPERATIONAL DIRECTIVES:
1. Provide concise, highly structured, and visually scannable responses using bold headers and lists.
2. Whenever presenting comparisons, statistics, or metrics, ALWAYS organize them into Markdown Tables or JSON ```chart blocks (compatible with Chart.js).
3. Whenever explaining workflows, algorithms, or architectural pipelines, ALWAYS provide a valid ```mermaid flowchart.
4. Maintain a professional, objective tone. Strictly avoid generic AI boilerplate.

TASK:
{task_name}

TASK INSTRUCTIONS:
{task_info}

PROMPTING TECHNIQUE:
{technique_name}

TECHNIQUE INSTRUCTIONS:
{tech_info}

USER INQUIRY:
{user_input}{attachment_block}
"""
    return prompt.strip()

def execute_gemini_request(engineered_prompt: str, max_retries: int = 3):
    """
    Calls client.interactions.create with exponential backoff 
    handling 503 (Overload) and 429 (Rate Limit) errors gracefully.
    """
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.interactions.create(
                model="gemini-3.8-flash",
                input=engineered_prompt,
            )
            return response, None
        except Exception as err:
            last_error = err
            err_msg = str(err)
            is_transient = any(code in err_msg for code in [
                "503", "429", "ResourceExhausted", "RESOURCE_EXHAUSTED",
                "UNAVAILABLE", "overloaded", "quota"
            ])
            if is_transient and attempt < max_retries:
                time.sleep(attempt * 2)
                continue
            break
    return None, last_error

# --------------------------------------------------
# 9. Main Console Viewport
# --------------------------------------------------

active_p = PRESETS[st.session_state["active_preset"]]

st.markdown(
    f"""
    <div class="console-header">
        <div class="console-title-group">
            <div class="console-title">
                ⚡ {active_p['title']}
            </div>
            <div class="console-meta-chip">
                {active_p['subtitle']}
            </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <div class="console-badge">
                <span class="status-indicator"></span>
                <span>Interactions API</span>
            </div>
            <div class="console-badge">
                <span>{st.session_state['active_technique']}</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Render Chat History with explicit avatars (preventing broken ligature fonts)
for idx, msg in enumerate(st.session_state["messages"]):
    avatar_icon = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        if msg["role"] == "assistant":
            render_rich_content(msg["content"], idx)
            
            # Action Toolbar: Clean Horizontal Layout (Export, Copy Text, Regenerate)
            act_col1, act_col2, act_col3, act_meta = st.columns([1.1, 1.1, 1.2, 4.0])
            with act_col1:
                st.download_button(
                    label="📄 Export MD",
                    data=msg["content"],
                    file_name=f"gemini_response_{idx}.md",
                    mime="text/markdown",
                    key=f"dl_md_{idx}",
                )
            with act_col2:
                if st.button("📋 Copy Text", key=f"btn_copy_{idx}"):
                    st.session_state[f"show_code_{idx}"] = not st.session_state.get(f"show_code_{idx}", False)
            with act_col3:
                if st.button("🔄 Regenerate", key=f"regen_{idx}"):
                    prior_user = ""
                    for prev_m in reversed(st.session_state["messages"][:idx]):
                        if prev_m["role"] == "user":
                            prior_user = prev_m["content"]
                            break
                    if prior_user:
                        st.session_state["messages"].pop(idx)
                        st.session_state["regenerate_prompt"] = prior_user
                        st.rerun()
            with act_meta:
                if "timestamp" in msg:
                    st.caption(f"🕒 {msg['timestamp']}")

            # Clean raw code block for instant copying without broken expander arrows
            if st.session_state.get(f"show_code_{idx}", False):
                st.caption("Click the copy icon on the top right of this block:")
                st.code(msg["content"], language="markdown")
        else:
            st.markdown(msg["content"])

# --------------------------------------------------
# 10. Attachment Indicator & Sticky Prompt Input
# --------------------------------------------------

# Show attachment pill if context is currently staged
if "attached_content" in st.session_state and st.session_state["attached_content"]:
    fn = st.session_state.get("attached_filename", "Attached document")
    st.markdown(
        f"""
        <div class="attachment-pill">
            <span>📎 Context Ready: <b>{fn}</b> ({len(st.session_state['attached_content'])} characters)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Handle programmatic regeneration trigger
prompt_input = st.session_state.pop("regenerate_prompt", None)

if not prompt_input:
    prompt_input = st.chat_input(
        f"Query {active_p['title']} or test with customized context...",
    )

# Elegant Quick-Load Preset Prompt Chip
if len(st.session_state["messages"]) <= 1 and not prompt_input:
    col_sugg, _ = st.columns([3, 1])
    with col_sugg:
        st.caption("💡 Quick-start demonstration for this preset:")
        if st.button(f"⚡ Insert: \"{active_p['default_prompt'][:75]}...\"", key="btn_quick_sample"):
            prompt_input = active_p["default_prompt"]

if prompt_input:
    # 1. Append User Message
    st.session_state["messages"].append({
        "role": "user",
        "content": prompt_input,
        "timestamp": time.strftime("%H:%M"),
    })
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt_input)

    # 2. Build Engineered Prompt
    attached_data = st.session_state.pop("attached_content", None)
    st.session_state.pop("attached_filename", None)
    
    engineered_prompt = build_structured_prompt(
        st.session_state["active_preset"],
        st.session_state["active_technique"],
        prompt_input,
        attached_data,
    )

    # 3. Stream & Render Assistant Response
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Analyzing and structuring response..."):
            resp, err = execute_gemini_request(engineered_prompt)

        if err:
            err_str = str(err)
            if "429" in err_str or "ResourceExhausted" in err_str:
                st.error("⏳ API Rate Limit Reached (429): Google Gemini is receiving high request volume. Please wait 15 seconds.")
            elif "503" in err_str or "UNAVAILABLE" in err_str:
                st.error("🌩️ Service Unavailable (503): Gemini reasoning clusters are currently overloaded. Retrying advised.")
            else:
                st.error(f"Request failed: {type(err).__name__}")
        elif resp and resp.output_text:
            output_content = resp.output_text
            render_rich_content(output_content, len(st.session_state["messages"]))
            
            # Save to Session History
            st.session_state["messages"].append({
                "role": "assistant",
                "content": output_content,
                "timestamp": time.strftime("%H:%M"),
            })
            st.session_state["last_response"] = output_content
        else:
            st.warning("Model returned an empty response. Please adjust your input.")

# --------------------------------------------------
# 11. Response Quality Score (RQS) Drawer (Collapsible)
# --------------------------------------------------

with st.expander("📊 Response Quality Score (RQS) Evaluation"):
    st.caption("Quantitative evaluation across 4 orthogonal dimensions (1 = Poor, 5 = Flawless).")
    rqs_c1, rqs_c2 = st.columns(2)
    with rqs_c1:
        acc = st.slider("Accuracy (Precision & Truthfulness)", 1, 5, 4, key="rqs_acc")
        cons = st.slider("Consistency (Coherence & Logic)", 1, 5, 4, key="rqs_cons")
    with rqs_c2:
        rel = st.slider("Relevance (Adherence to Prompt)", 1, 5, 4, key="rqs_rel")
        fl = st.slider("Fluency (Typography & Structure)", 1, 5, 5, key="rqs_fl")
    
    score = (acc + cons + rel + fl) / 4.0
    st.metric("Aggregate Response Quality Score", f"{score:.2f} / 5.0")
    st.progress(score / 5.0)

# --------------------------------------------------
# 12. Engineered Prompt Inspection (Collapsible)
# --------------------------------------------------

if "messages" in st.session_state and len(st.session_state["messages"]) > 1:
    with st.expander("🔍 Inspect Last Engineered Prompt Template"):
        last_user_msg = next((m["content"] for m in reversed(st.session_state["messages"]) if m["role"] == "user"), "")
        if last_user_msg:
            st.code(
                build_structured_prompt(
                    st.session_state["active_preset"],
                    st.session_state["active_technique"],
                    last_user_msg,
                ),
                language="text",
            )
