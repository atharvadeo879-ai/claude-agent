"""Streamlit entrypoint for manual and cloud deployment."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

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
        secret_key = ""
        try:
            secret_key = st.secrets.get("GROQ_API_KEY", "")
        except StreamlitSecretNotFoundError:
            # No secrets.toml configured; continue with env/fallback mode.
            secret_key = ""
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
    st.session_state.setdefault("ui_step", "home")
    st.session_state.setdefault("latest_prompt", "")
    st.session_state.setdefault("edit_prompt_value", "")
    st.session_state.setdefault("edit_response_value", "")
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
          .block-container {padding-top: 0.9rem; padding-bottom: 1.2rem; max-width: 860px;}
          [data-testid="stSidebar"] {background: #0f1323;}
          [data-testid="stAppViewContainer"] {background: #06070d;}
          .ag-screen-title {
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-size: 0.72rem;
            color: #7c859f;
            margin-bottom: 0.35rem;
          }
          .ag-card {
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 16px;
            padding: 14px 16px;
            background: linear-gradient(180deg, #11131b 0%, #0c0e14 100%);
            margin-bottom: 12px;
          }
          .ag-title {font-size: 1.02rem; font-weight: 650; margin-bottom: 0.3rem; color: #f1f3ff;}
          .ag-muted {color: #b0b5c9; font-size: 0.93rem; line-height: 1.45;}
          .ag-chip {
            display: inline-block;
            border-radius: 999px;
            padding: 7px 11px;
            font-size: 0.78rem;
            margin: 4px 6px 4px 0;
            background: #2a1a12;
            border: 1px solid #5a3522;
            color: #ffb17f;
          }
          .ag-kpi {
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            background: #10131c;
            padding: 10px 12px;
            text-align: center;
          }
          .ag-kpi-big {font-size: 1.08rem; color: #fff; font-weight: 700;}
          .ag-kpi-label {font-size: 0.72rem; color: #9ca3bd; letter-spacing: .04em; text-transform: uppercase;}
          .ag-divider {height: 1px; background: rgba(255,255,255,.08); margin: 10px 0;}
          .ag-topbar {display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;}
          .ag-token-label {font-size: .82rem; color: #a8adc0;}
          .ag-note {font-size: .78rem; color: #9098b5;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _format_sections_as_architecture(sections: dict[str, str]) -> str:
    chips = ["Overview", "Components", "Data Flow", "Risks", "Next Steps"]
    chips_html = "".join([f"<span class='ag-chip'>{chip}</span>" for chip in chips if chip in sections])
    return chips_html or "<span class='ag-chip'>Architecture</span>"


def _home_step(service: Phase7Service) -> None:
    st.markdown("<div class='ag-screen-title'>01 - Home</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="ag-card">
          <div class="ag-title">Hi there!</div>
          <div class="ag-muted">What can I help you with today? Share your scenario and generate architecture-ready output.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    prompt = st.text_area(
        "Prompt",
        value=st.session_state.get("latest_prompt", ""),
        height=150,
        placeholder="Example: Build a 4-day travel architecture with modules, cost split, and execution plan.",
        label_visibility="collapsed",
    )
    usage = st.session_state["generation_result"]["token_usage"]
    st.caption("Daily tokens")
    st.progress(float(usage.get("usage_ratio", 0.0)))
    st.caption(
        f"{int(usage.get('used_today', 0))} / {service.token_service.daily_limit} used - "
        f"{int(usage.get('remaining_today', 0))} remaining"
    )

    if st.button("Generate Architecture", type="primary", use_container_width=True):
        if not prompt.strip():
            st.warning("Enter a prompt before generating.")
            return
        try:
            result = service.generate_architecture(
                user_id="streamlit-user",
                date_key=str(date.today()),
                prompt=prompt.strip(),
                use_groq=bool(st.session_state.get("groq_enabled", False)),
            )
            st.session_state["latest_prompt"] = prompt.strip()
            st.session_state["edit_prompt_value"] = prompt.strip()
            st.session_state["generation_result"] = result
            st.session_state["last_provider_status"] = result.get("provider_status", {})
            st.session_state["history"].insert(0, prompt.strip())
            st.session_state["edit_response_value"] = "\n\n".join(
                [f"{k}: {v}" for k, v in result.get("sections", {}).items()]
            )
            st.session_state["ui_step"] = "architecture"
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error("Generation failed unexpectedly. " + str(exc))


def _architecture_step(service: Phase7Service) -> None:
    st.markdown("<div class='ag-screen-title'>03 - Architecture</div>", unsafe_allow_html=True)
    result = st.session_state["generation_result"]
    sections = result["sections"]
    prompt_text = st.session_state.get("latest_prompt", "")

    st.markdown(
        f"""
        <div class="ag-card">
          <div class="ag-title">Structured Architecture</div>
          <div class="ag-muted">{prompt_text}</div>
          <div class="ag-divider"></div>
          {_format_sections_as_architecture(sections)}
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    tokens = result["token_usage"]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div class='ag-kpi'><div class='ag-kpi-big'>{len(sections)}</div><div class='ag-kpi-label'>Modules</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            "<div class='ag-kpi'><div class='ag-kpi-big'>Edit</div><div class='ag-kpi-label'>Ready</div></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div class='ag-kpi'><div class='ag-kpi-big'>{int(tokens.get('current_request_tokens', 0))}</div><div class='ag-kpi-label'>Tokens</div></div>",
            unsafe_allow_html=True,
        )

    a, b = st.columns(2)
    with a:
        if st.button("Edit", use_container_width=True):
            st.session_state["ui_step"] = "edit"
            st.rerun()
    with b:
        if st.button("Continue", type="primary", use_container_width=True):
            st.session_state["ui_step"] = "final"
            st.rerun()


def _edit_step(service: Phase7Service) -> None:
    st.markdown("<div class='ag-screen-title'>04 - Edit / Continue</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="ag-card">
          <div class="ag-title">Refine Prompt or Response</div>
          <div class="ag-muted">Update either prompt or generated architecture, then continue to final result.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    edited_prompt = st.text_area(
        "Edit Prompt",
        value=st.session_state.get("edit_prompt_value", ""),
        height=120,
    )
    edited_response = st.text_area(
        "Edit Response",
        value=st.session_state.get("edit_response_value", ""),
        height=180,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Save Prompt Edit", use_container_width=True):
            if edited_prompt.strip():
                rev_id = service.edit_prompt("streamlit-response", edited_prompt.strip())
                st.session_state["edit_prompt_value"] = edited_prompt.strip()
                st.success(f"Prompt edit saved (revision {rev_id}).")
    with c2:
        if st.button("Save Response Edit", use_container_width=True):
            if edited_response.strip():
                rev_id = service.edit_response("streamlit-response", edited_response.strip())
                st.session_state["edit_response_value"] = edited_response.strip()
                st.success(f"Response edit saved (revision {rev_id}).")
    with c3:
        if st.button("Continue to Final", type="primary", use_container_width=True):
            st.session_state["ui_step"] = "final"
            st.rerun()


def _final_step(service: Phase7Service) -> None:
    st.markdown("<div class='ag-screen-title'>05 - Final Result</div>", unsafe_allow_html=True)
    result = st.session_state["generation_result"]
    tokens = result["token_usage"]

    st.markdown(
        """
        <div class="ag-card">
          <div class="ag-title">Final Plan</div>
          <div class="ag-muted">Architecture completed. Continue using this as your implementation blueprint.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for title, body in result["sections"].items():
        st.markdown(
            f"""
            <div class="ag-card">
              <div class="ag-title">{title}</div>
              <div class="ag-muted">{body}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='ag-screen-title'>06 - Token Usage</div>", unsafe_allow_html=True)
    st.progress(float(tokens.get("usage_ratio", 0.0)))
    s1, s2, s3 = st.columns(3)
    s1.metric("Current Request", int(tokens.get("current_request_tokens", 0)))
    s2.metric("Used Today", int(tokens.get("used_today", 0)))
    s3.metric("Remaining", int(tokens.get("remaining_today", 0)))
    st.caption("Daily token usage is updated after every generation.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back to Edit", use_container_width=True):
            st.session_state["ui_step"] = "edit"
            st.rerun()
    with c2:
        if st.button("Start New Session", type="primary", use_container_width=True):
            st.session_state["ui_step"] = "home"
            st.rerun()


def main() -> None:
    st.set_page_config(page_title="Claude Agent Architecture", layout="wide")
    _render_styles()
    st.title("Claude Agent - Architecture Experience")
    st.caption("Generate detailed architecture, edit it, then continue to final result and token insights.")

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
        st.markdown("---")
        st.caption("Flow")
        st.write("1. Home")
        st.write("2. Architecture")
        st.write("3. Edit or Continue")
        st.write("4. Final + Tokens")

    provider_status = st.session_state.get("last_provider_status", {})
    if provider_status.get("status") == "error":
        st.warning("Provider issue detected. Fallback mode is active and generation continues smoothly.")
        st.session_state["groq_enabled"] = False
    elif provider_status.get("status") == "disabled":
        st.caption("Fallback provider mode active.")
    elif provider_status.get("status") == "success":
        st.caption("Groq provider active.")

    step = st.session_state.get("ui_step", "home")
    if step == "home":
        _home_step(service)
    elif step == "architecture":
        _architecture_step(service)
    elif step == "edit":
        _edit_step(service)
    else:
        _final_step(service)

    st.markdown("---")
    st.caption("Recent prompts")
    history = st.session_state.get("history", [])
    if history:
        for idx, item in enumerate(history[:5], start=1):
            st.write(f"{idx}. {item}")
    else:
        st.caption("No architecture sessions yet.")


if __name__ == "__main__":
    main()

