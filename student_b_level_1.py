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

    h = []
    h.append("""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><title>Sub-Task B — Level 1 (Mission)</title>
<style>
  :root { --line:#d7d7d7; --text:#111; --muted:#555; --boxbg:#fafafa; }
  body{font-family:Segoe UI,Arial,sans-serif;margin:24px;line-height:1.5;color:var(--text)}
  h1,h2{margin:0 0 12px 0}
  .muted{color:var(--muted)}
  .card{border:1px solid var(--line);border-radius:10px;padding:16px;margin:12px 0;background:#fff}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}

  /* persona tiles */
  .persona-box{
     border:10px solid var(--text); background:var(--boxbg);
     height:150px; display:flex; align-items:center; justify-content:center;
     font-weight:700; font-size:18px; letter-spacing:.3px; border-radius:6px;
     transition:background .15s, border-color .15s, transform .05s;
  }
  .persona-box, .persona-box:link, .persona-box:visited { color:inherit; text-decoration:none; }
  .persona-box:hover { background:#f0f0f0; border-color:#555; }
  .persona-box:active { transform:scale(0.99); }

  /* team table */
  table{border-collapse:collapse;width:100%;background:#fff}
  th,td{border-bottom:1px solid var(--line);text-align:left;padding:10px}
  th{background:#f4f4f4}

  /* --- Hero Mission Section --- */
  .card.hero{
    position:relative;
    text-align:center;
    border-radius:18px;
    padding:50px 40px;
    border:1px solid #e6e6e6;
    background:linear-gradient(180deg,#ffffff 0%, #f8f9ff 100%);
    box-shadow:0 8px 25px rgba(0,0,0,0.05);
  }
  .card.hero::before{
    content:"";
    position:absolute; inset:0 0 auto 0; height:6px;
    border-top-left-radius:18px; border-top-right-radius:18px;
    background:linear-gradient(90deg,#2563eb,#7c3aed 60%,#e11d48);
  }

  .section-label{
    display:inline-block;
    font-size:36px; font-weight:700; letter-spacing:.4px;
    color:#334155; background:#f1f5f9;
    padding:6px 12px; border-radius:999px; border:1px solid #e2e8f0;
    margin-bottom:14px;
  }

  .hero h1{
    font-size:36px;
    line-height:1.3;
    color:#0f172a;
    margin:0 auto 14px;
    max-width:900px;
  }
  .hero p.lead{
    color:#1e293b;
    font-size:18px;
    max-width:850px;
    margin:0 auto 24px;
    line-height:1.6;
  }

  .hero .actions{ margin-top:10px; display:flex; justify-content:center; gap:12px; flex-wrap:wrap }
  .hero .btn{
    display:inline-block; padding:12px 18px; border-radius:12px;
    border:1px solid #cbd5e1; text-decoration:none; font-weight:600;
    background:#fff; color:#0f172a;
    transition:transform .05s, box-shadow .15s, border-color .15s;
  }
  .hero .btn:hover{ box-shadow:0 6px 14px rgba(0,0,0,0.06); border-color:#94a3b8 }
  .hero .btn:active{ transform:scale(.98) }

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
          <em>economic phase</em>, <em>infection type</em>, and <em>year</em>, then view
          per-country <b>cases per 100,000 people</b>.</li>
      <li>Open <a href="/b3">B3 — Above-average view</a>. See the <b>global infection rate</b>
          for your chosen disease/year, then compare countries that exceed that benchmark (global
          row shown first).</li>
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
            is_policymaker = (title or "").strip().lower() == "policymaker" \
                             or (name or "").strip().lower() == "policymaker" \
                             or (role or "").strip().lower() == "policymaker"
            if is_policymaker:
                h.append(f'<a href="/b2" class="persona-box" aria-label="Open B2 for Policymaker">{title_txt}</a>')
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
