"""Streamlit entrypoint for manual and cloud deployment."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import streamlit as st

from phases.phase7 import GroqClient, Phase7Service


def _load_local_env_if_present() -> None:
    env_path = Path(__file__).parent / "phases" / "phase6" / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key and value and key not in os.environ:
            os.environ[key] = value


def _service() -> Phase7Service:
    if "phase7_service" not in st.session_state:
        _load_local_env_if_present()
        secret_key = st.secrets.get("GROQ_API_KEY", "")
        if secret_key and "GROQ_API_KEY" not in os.environ:
            os.environ["GROQ_API_KEY"] = secret_key
        st.session_state["phase7_service"] = Phase7Service(
            groq_client=GroqClient(),
            vector_provider="chromadb",
            daily_limit=100000,
        )
    return st.session_state["phase7_service"]


def _bootstrap_session() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("groq_enabled", False)
    st.session_state.setdefault("last_provider_status", {})
    st.session_state.setdefault(
        "generation_result",
        {
            "sections": {"Overview": "Submit a prompt to generate architecture output."},
            "token_usage": {
                "current_request_tokens": 0,
                "used_today": 0,
                "remaining_today": 100000,
                "usage_ratio": 0.0,
            },
        },
    )


def _render_styles() -> None:
    st.markdown(
        """
        <style>
          .block-container {padding-top: 1.2rem; padding-bottom: 1.2rem; max-width: 1100px;}
          .ag-card {
            border: 1px solid rgba(120, 120, 200, 0.25);
            border-radius: 12px;
            padding: 14px 16px;
            background: rgba(20, 28, 52, 0.45);
            margin-bottom: 10px;
          }
          .ag-title {font-size: 1.05rem; font-weight: 650; margin-bottom: 0.25rem;}
          .ag-muted {color: #8ea0c9; font-size: 0.92rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Claude Agent Architecture", layout="wide")
    _render_styles()
    st.title("Claude Agent - Architecture Generator")
    st.caption("Smooth architecture generation with automatic fallback when Groq is unavailable.")

    _bootstrap_session()
    service = _service()

    with st.sidebar:
        st.subheader("Provider Settings")
        has_key = bool(os.getenv("GROQ_API_KEY", "").strip())
        st.session_state["groq_enabled"] = st.toggle(
            "Use Groq provider",
            value=bool(st.session_state.get("groq_enabled", False) and has_key),
            disabled=not has_key,
            help="Optional. If disabled, app uses stable fallback mode.",
        )
        if not has_key:
            st.info("No GROQ_API_KEY found. Running in fallback mode.")
        st.caption("Recommended: keep fallback mode for stable behavior.")

    prompt = st.text_area(
        "Prompt",
        value="",
        height=170,
        placeholder="Describe the architecture you want to generate...",
    )

    usage = st.session_state["generation_result"]["token_usage"]
    st.markdown("### Daily Token Usage")
    st.progress(float(usage.get("usage_ratio", 0.0)))
    st.write(
        f"Used today: {int(usage.get('used_today', 0))} / {service.token_service.daily_limit} "
        f"- Remaining: {int(usage.get('remaining_today', 0))}"
    )

    if st.button("Generate Architecture", type="primary"):
        if not prompt.strip():
            st.warning("Enter a prompt before generating.")
        else:
            try:
                result = service.generate_architecture(
                    user_id="streamlit-user",
                    date_key=str(date.today()),
                    prompt=prompt.strip(),
                    use_groq=bool(st.session_state.get("groq_enabled", False)),
                )
                st.session_state["generation_result"] = result
                st.session_state["last_provider_status"] = result.get("provider_status", {})
                st.session_state["history"].insert(0, prompt.strip())
            except Exception as exc:  # noqa: BLE001
                st.error(
                    "Generation hit an unexpected error. "
                    "Please retry. Details: " + str(exc)
                )

    result = st.session_state["generation_result"]
    sections = result["sections"]
    tokens = result["token_usage"]
    provider_status = result.get("provider_status", {})

    if provider_status:
        status_label = provider_status.get("status", "unknown")
        if status_label == "error":
            st.warning("Provider issue detected. App is using fallback mode for smooth generation.")
            st.session_state["groq_enabled"] = False
        elif status_label == "disabled":
            st.caption("Fallback provider mode active.")
        else:
            st.caption("Groq provider active.")

    st.markdown("### Generated Architecture")
    for title, body in sections.items():
        st.markdown(
            f"""
            <div class="ag-card">
              <div class="ag-title">{title}</div>
              <div class="ag-muted">{body}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Edit Actions")
    col1, col2 = st.columns(2)
    with col1:
        edited_prompt = st.text_area("Edit Prompt", value="", height=80, key="edited_prompt")
        if st.button("Save Prompt Edit"):
            if edited_prompt.strip():
                rev_id = service.edit_prompt("streamlit-response", edited_prompt.strip())
                st.success(f"Prompt edit saved as revision {rev_id}.")
    with col2:
        edited_response = st.text_area("Edit Response", value="", height=80, key="edited_response")
        if st.button("Save Response Edit"):
            if edited_response.strip():
                rev_id = service.edit_response("streamlit-response", edited_response.strip())
                st.success(f"Response edit saved as revision {rev_id}.")

    st.markdown("### Final Token Summary")
    s1, s2, s3 = st.columns(3)
    s1.metric("Current Request Tokens", int(tokens.get("current_request_tokens", 0)))
    s2.metric("Used Today", int(tokens.get("used_today", 0)))
    s3.metric("Daily Tokens Remaining", int(tokens.get("remaining_today", 0)))

    st.markdown("### Session History")
    history = st.session_state["history"]
    if history:
        for idx, item in enumerate(history[:10], start=1):
            st.write(f"{idx}. {item}")
    else:
        st.info("No architecture sessions yet.")


if __name__ == "__main__":
    main()

