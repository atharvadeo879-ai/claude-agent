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
        st.session_state["phase7_service"] = Phase7Service(
            groq_client=GroqClient(),
            vector_provider="chromadb",
            daily_limit=100000,
        )
    return st.session_state["phase7_service"]


def _bootstrap_session() -> None:
    st.session_state.setdefault("history", [])
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


def main() -> None:
    st.set_page_config(page_title="Claude Agent Architecture", layout="wide")
    st.title("Claude Agent - Architecture Generator")
    st.caption("Phase 7 Streamlit UI with Groq integration and token usage insights.")

    _bootstrap_session()
    service = _service()

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
                )
                st.session_state["generation_result"] = result
                st.session_state["history"].insert(0, prompt.strip())
            except Exception as exc:  # noqa: BLE001
                st.error(f"Generation failed: {exc}")

    result = st.session_state["generation_result"]
    sections = result["sections"]
    tokens = result["token_usage"]

    st.markdown("### Generated Architecture")
    for title, body in sections.items():
        with st.container(border=True):
            st.subheader(title)
            st.write(body)

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

