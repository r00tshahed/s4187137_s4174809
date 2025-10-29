import pyhtml
from navigation import build_nav, nav_styles

DB = "database/immunisation.db"

def get_page_html(form_data):
    personas = pyhtml.get_results_from_query(
        DB, "SELECT name, role, goals FROM Persona ORDER BY id;"
    )
    team = pyhtml.get_results_from_query(
        DB, "SELECT name, student_number FROM TeamMember ORDER BY name;"
    )

    # Map persona roles (or names) → destination page
    role_links = {
        "policymaker": "/b2",   # compare by economic status
        "journalist":  "/b3",   # global vs above-average comparison
        "researcher":  "/b3",
        "epidemiologist": "/b3",
        "student": "/b2",
    }

    def _link_for(role_or_name: str):
        if not role_or_name:
            return None
        key = role_or_name.strip().lower()
        # try exact, then contains match (e.g., "Health Journalist")
        for k, href in role_links.items():
            if k == key or k in key:
                return href
        return None

    h = []
    h.append("""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><title>Sub-Task B — Level 1 (Mission)</title>
<style>
  /* ===== Vibrant look & feel ===== */
  :root {
    --ink:#0b1220; --muted:#5b6476; --line:#e6e9f2;
    --card:#ffffff; --bg:#f7f9ff;
    --accent:#6c5ce7; --accent-2:#22c55e; --accent-3:#ef4444; --accent-4:#06b6d4;
  }
  html,body{height:100%}
  body{
    font-family:Segoe UI,system-ui,Arial,sans-serif; margin:0;
    color:var(--ink); line-height:1.6;
    background: radial-gradient(1200px 800px at 0% -10%, #eef2ff 0%, #f7f9ff 55%, #ffffff 100%);
  }
  main{max-width:1060px;margin:28px auto;padding:0 20px}

  h1,h2{margin:0 0 12px 0}
  .muted{color:var(--muted)}

  .card{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:16px; padding:18px; margin:14px 0;
    box-shadow:0 8px 24px rgba(16,24,40,.04);
  }

  /* --- Hero --- */
  .hero{
    position:relative; overflow:hidden;
    padding:46px 36px 38px; text-align:center;
    background:
      radial-gradient(1200px 400px at 50% -10%, rgba(108,92,231,.18), transparent 60%),
      linear-gradient(180deg, #ffffff 0%, #f7f7ff 100%);
    border:1px solid #eae9ff;
  }
  .hero::before{
    content:""; position:absolute; inset:0 0 auto 0; height:6px;
    background:linear-gradient(90deg, var(--accent), #8b5cf6 35%, #22c55e 65%, #06b6d4 100%);
  }
  .section-label{
    display:inline-block; font-size:14px; font-weight:700; letter-spacing:.4px;
    color:#334155; background:#eef2ff; padding:6px 12px; border-radius:999px;
    border:1px solid #dbe1ff; margin-bottom:14px; text-transform:uppercase;
  }
  .hero h1{font-size:34px; line-height:1.25; margin:0 auto 12px; max-width:900px}
  .hero p.lead{font-size:18px; max-width:880px; margin:0 auto 20px; color:#1f2937}

  .actions{margin-top:10px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap}
  .btn{
    display:inline-block; padding:12px 16px; border-radius:12px; font-weight:700;
    text-decoration:none; border:1px solid #cdd4ff; background:#fff; color:#0f172a;
    transition:transform .06s, box-shadow .18s, border-color .18s, background .18s;
  }
  .btn:hover{box-shadow:0 10px 20px rgba(17,24,39,.08); border-color:#a9b6ff}
  .btn:active{transform:translateY(1px)}

  /* --- Persona grid --- */
  .grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px}
  .persona-box{
    border:2px solid #cfd5ff; background:linear-gradient(180deg, #ffffff 0%, #fbfbff 100%);
    min-height:120px; display:flex; align-items:center; justify-content:center; text-align:center;
    font-weight:800; font-size:18px; letter-spacing:.2px; border-radius:14px;
    transition:transform .06s, box-shadow .18s, border-color .18s, background .18s, color .18s;
    color:#1c2434; text-decoration:none;
  }
  .persona-box:hover{
    transform:translateY(-1px);
    box-shadow:0 10px 22px rgba(17,24,39,.08);
    border-color:#a9b6ff; background:linear-gradient(180deg, #ffffff 0%, #eef2ff 100%);
  }
  .persona-box.linked{
    border-color:#86efac;
  }
  .persona-box.linked:hover{
    border-color:#22c55e; color:#064e3b;
    background:linear-gradient(180deg,#ffffff 0%, #eafff3 100%);
  }

  /* Team table */
  table{border-collapse:collapse;width:100%}
  thead th{background:#f3f5ff}
  th,td{border-bottom:1px solid var(--line);text-align:left;padding:10px}
</style>
</head>
<body>""")

    h.append(nav_styles())
    h.append(build_nav("b1", "B"))

    h.append("""
<main>
  <!-- Mission -->
  <div class="card hero" role="region" aria-labelledby="mission-heading">
    <span class="section-label" id="mission-heading">Mission Statement</span>
    <h1>Help diverse users explore unbiased vaccination &amp; infection data.</h1>
    <p class="lead">
      We present respectful, neutral information and let users examine patterns by economic status, region, and time —
      offering both quick summaries and deeper analysis so anyone can become well-informed about global immunisation efforts and their impacts.
    </p>
    <div class="actions" aria-label="Quick links">
      <a class="btn" href="/b2" aria-label="Open B2 focused view">Open B2 — Focused view</a>
      <a class="btn" href="/b3" aria-label="Open B3 above average view">Open B3 — Above-average view</a>
    </div>
  </div>

  <!-- How to use -->
  <div class="card" role="region" aria-labelledby="howto-heading">
    <h2 id="howto-heading">How to use this site</h2>
    <ol>
      <li>Open <a href="/b2">B2 — Focused view by economic status</a>. Choose an
          <em>economic phase</em>, <em>infection type</em>, and <em>year</em>, then view per-country
          <b>cases per 100,000 people</b>.</li>
      <li>Open <a href="/b3">B3 — Above-average view</a>. See the <b>global infection rate</b> for your chosen disease/year,
          then compare countries that exceed that benchmark (global row shown first).</li>
      <li>Return here any time to review the Personas we target and your team details stored in the database.</li>
    </ol>
  </div>

  <!-- Personas -->
  <div class="card" role="region" aria-labelledby="personas-heading">
    <h2 id="personas-heading">Personas</h2>
    <div class="grid">
""")

    if personas:
        for (name, role, goals) in personas:
            title = (role or name or "User")
            title_txt = (title or "").replace('"', '&quot;')
            # pick link by role or by name
            link = _link_for(role) or _link_for(name)
            if link:
                h.append(f'<a href="{link}" class="persona-box linked" aria-label="Open {link} for {title_txt}">{title_txt}</a>')
            else:
                h.append(f'<div class="persona-box">{title_txt}</div>')
    else:
        h.append('<p class="muted">No personas found. Add rows to <code>Persona</code>.</p>')

    h.append("""
    </div>
  </div>

  <!-- Team -->
  <div class="card" role="region" aria-labelledby="team-heading">
    <h2 id="team-heading">Developers</h2>
    <table aria-describedby="team-heading">
      <thead><tr><th scope="col">Name</th><th scope="col">Student #</th></tr></thead>
      <tbody>
""")

    if team:
        for (name, sn) in team:
            name_txt = (name or "").replace("<","&lt;").replace(">","&gt;")
            sn_txt = (sn or "")
            h.append(f"<tr><td>{name_txt}</td><td>{sn_txt}</td></tr>")
    else:
        h.append('<tr><td colspan="2" class="muted">No team members found.</td></tr>')

    h.append("""
      </tbody>
    </table>
  </div>

  <p><a href="/">Back to Home</a></p>
</main>
</body></html>""")

    return "".join(h)
