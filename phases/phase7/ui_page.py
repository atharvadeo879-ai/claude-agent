"""Phase 7: UI page rendering for architecture sessions."""

from __future__ import annotations


def render_architecture_page(
    sections: dict[str, str],
    token_usage: dict[str, float | int],
    daily_limit: int,
    history_items: list[str],
    prompt_value: str = "",
) -> str:
    used_today = int(token_usage.get("used_today", 0))
    remaining = int(token_usage.get("remaining_today", max(daily_limit - used_today, 0)))
    ratio = float(token_usage.get("usage_ratio", 0.0))
    width_pct = max(0, min(int(ratio * 100), 100))

    sections_html = "".join(
        f'<section class="card"><h3>{title}</h3><p>{body}</p></section>'
        for title, body in sections.items()
    )
    history_html = "".join(f"<li>{item}</li>" for item in history_items) or "<li>No sessions yet</li>"

    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Claude Agent Architecture UI</title>
    <style>
      :root {{
        --bg: #0b1020;
        --panel: #121a31;
        --panel-soft: #182241;
        --text: #eaf0ff;
        --muted: #a8b3d1;
        --primary: #4e79ff;
        --success: #3fd08f;
        --border: #2a3763;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Segoe UI, Arial, sans-serif;
        color: var(--text);
        background: radial-gradient(circle at top, #15244e 0%, var(--bg) 45%);
      }}
      .container {{
        max-width: 1080px;
        margin: 24px auto 36px;
        padding: 0 16px;
      }}
      .card {{
        background: linear-gradient(180deg, var(--panel) 0%, var(--panel-soft) 100%);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
      }}
      h1, h2, h3 {{ margin: 0 0 10px; }}
      p {{ margin: 0; color: var(--muted); line-height: 1.5; }}
      .prompt-label {{
        display: block;
        margin-bottom: 8px;
        font-weight: 600;
      }}
      textarea {{
        width: 100%;
        min-height: 130px;
        resize: vertical;
        border-radius: 10px;
        border: 1px solid var(--border);
        background: #0e162f;
        color: var(--text);
        padding: 12px;
        font-size: 14px;
      }}
      .actions {{
        margin-top: 10px;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
      }}
      button {{
        border: 1px solid transparent;
        border-radius: 10px;
        padding: 10px 14px;
        font-weight: 600;
        cursor: pointer;
      }}
      .btn-primary {{
        background: var(--primary);
        color: white;
      }}
      .btn-secondary {{
        background: #26335f;
        color: var(--text);
        border-color: var(--border);
      }}
      .token-shell {{
        width: 100%;
        height: 16px;
        background: #0e162f;
        border: 1px solid var(--border);
        border-radius: 999px;
        overflow: hidden;
        margin: 10px 0 8px;
      }}
      .token-fill {{
        height: 100%;
        width: {width_pct}%;
        background: linear-gradient(90deg, var(--primary), var(--success));
      }}
      .usage-meta {{
        display: flex;
        justify-content: space-between;
        gap: 10px;
        flex-wrap: wrap;
        color: var(--muted);
        font-size: 14px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 12px;
      }}
      ul {{ margin: 0; padding-left: 18px; color: var(--muted); }}
      li {{ margin-bottom: 6px; }}
    </style>
  </head>
  <body>
    <main class="container">
      <section class="card">
        <h1>Architecture Session</h1>
        <p>Generate a structured architecture response with Groq-backed suggestions.</p>
      </section>

      <section class="card">
        <form method="post">
          <label class="prompt-label" for="prompt">Manual Prompt</label>
          <textarea id="prompt" name="prompt">{prompt_value}</textarea>
          <div class="actions">
            <button class="btn-primary" type="submit">Generate Architecture</button>
          </div>
        </form>
      </section>

      <section class="card" id="daily-usage">
        <strong>Daily Token Usage</strong>
        <div aria-label="daily-token-usage-bar" class="token-shell">
          <div class="token-fill"></div>
        </div>
        <div class="usage-meta">
          <span>Used today: {used_today} / {daily_limit}</span>
          <span>{width_pct}% consumed</span>
        </div>
      </section>

      <section id="architecture-output">{sections_html}</section>

      <section class="card" id="edit-actions">
        <h2>Edit Actions</h2>
        <div class="actions">
          <button class="btn-secondary" id="edit-prompt" type="button">Edit Prompt</button>
          <button class="btn-secondary" id="edit-response" type="button">Edit Response</button>
        </div>
      </section>

      <section class="card" id="final-token-summary">
        <h2>Final Token Summary</h2>
        <div class="grid">
          <div class="card"><h3>Current Request</h3><p>{int(token_usage.get("current_request_tokens", 0))} tokens</p></div>
          <div class="card"><h3>Used Today</h3><p>{used_today} tokens</p></div>
          <div class="card"><h3>Daily Tokens Remaining</h3><p>{remaining} tokens</p></div>
        </div>
      </section>

      <section class="card" id="history">
        <h2>Session History</h2>
        <ul>{history_html}</ul>
      </section>
    </main>
  </body>
</html>"""

