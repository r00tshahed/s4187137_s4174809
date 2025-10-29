import pyhtml
from navigation import build_nav, nav_styles

DB = "database/immunisation.db"

# --- tiny helpers ---
def _opts(db, sql):
    return [r[0] for r in pyhtml.get_results_from_query(db, sql)]

def _get(form_data, key, default=None):
    vals = form_data.get(key, [])
    return vals[0] if vals else default

def _fmt_int(x):
    try:
        return f"{int(x):,}"
    except Exception:
        return "—"

def _fmt_float(x, dp=2):
    try:
        return f"{float(x):.{dp}f}"
    except Exception:
        return "—"

def _severity_class(per100k):
    """Return a soft heat class name based on numeric rate."""
    try:
        v = float(per100k)
    except Exception:
        return "sev-null"
    if v >= 50:  return "sev-4"
    if v >= 20:  return "sev-3"
    if v >= 5:   return "sev-2"
    if v >= 0:   return "sev-1"
    return "sev-null"


def get_page_html(form_data):
    # -------- Dropdown data --------
    phases   = _opts(DB, "SELECT DISTINCT phase FROM Economy ORDER BY phase;")
    diseases = _opts(DB, "SELECT DISTINCT description FROM Infection_Type ORDER BY description;")
    years    = _opts(DB, "SELECT DISTINCT year FROM InfectionData ORDER BY year;")

    # Selected values (default to first available)
    sel_phase   = _get(form_data, "var_phase",   phases[0] if phases else "")
    sel_disease = _get(form_data, "var_disease", diseases[0] if diseases else "")
    sel_year    = _get(form_data, "var_year",    str(years[0]) if years else "")

    rows = []
    summary_rows = []
    if sel_phase and sel_disease and sel_year:
        sql = f"""
        SELECT it.description AS disease,
               c.name        AS country,
               e.phase       AS economic_phase,
               i.year,
               ROUND( (CAST(i.cases AS FLOAT) / NULLIF(cp.population,0)) * 100000, 2 ) AS cases_per_100k
        FROM InfectionData i
        JOIN Country        c  ON c.CountryID = i.country
        JOIN Economy        e  ON e.economyID = c.economy
        JOIN Infection_Type it ON it.id       = i.inf_type
        LEFT JOIN CountryPopulation cp ON cp.country = i.country AND cp.year = i.year
        WHERE e.phase = '{sel_phase}'
          AND it.description = '{sel_disease}'
          AND i.year = {sel_year}
        ORDER BY cases_per_100k DESC, country ASC;
        """
        rows = pyhtml.get_results_from_query(DB, sql)

        summary_sql = f"""
        SELECT e.phase AS economic_phase,
               it.description AS disease,
               i.year,
               SUM(COALESCE(i.cases,0)) AS total_cases
        FROM InfectionData i
        JOIN Country c         ON c.CountryID = i.country
        JOIN Economy e         ON e.economyID = c.economy
        JOIN Infection_Type it ON it.id       = i.inf_type
        WHERE e.phase = '{sel_phase}'
          AND it.description = '{sel_disease}'
          AND i.year = {sel_year}
        GROUP BY e.phase, it.description, i.year
        ORDER BY total_cases DESC;
        """
        summary_rows = pyhtml.get_results_from_query(DB, summary_sql)

    def _render_options(options, selected):
        if not options:
            return '<option disabled>None</option>'
        return "".join(
            f'<option value="{v}"{" selected" if str(v)==str(selected) else ""}>{v}</option>'
            for v in options
        )

    # -------- HTML --------
    h = []
    h.append("""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><title>Sub-Task B — Level 2</title>
<style>
  :root{
    --ink:#0b1220; --muted:#5b6476; --line:#e6e9f2;
    --card:#ffffff; --bg:#f7f9ff;
    --accent:#6c5ce7; --accent-2:#22c55e; --accent-3:#ef4444; --accent-4:#06b6d4;
    --chip:#eef2ff; --chip-b:#c7d2fe;
  }
  html,body{height:100%}
  body{
    margin:0; font-family:Segoe UI,system-ui,Arial,sans-serif; color:var(--ink); line-height:1.6;
    background: radial-gradient(1200px 800px at 0% -10%, #eef2ff 0%, #f7f9ff 55%, #ffffff 100%);
  }
  main{max-width:1100px;margin:28px auto;padding:0 20px}

  .card{
    background:var(--card); border:1px solid var(--line); border-radius:16px;
    padding:18px; margin:14px 0; box-shadow:0 8px 24px rgba(16,24,40,.04);
  }

  .filters{
    display:flex; flex-wrap:wrap; gap:12px; align-items:end;
    background:linear-gradient(180deg,#ffffff 0%, #f6f7ff 100%);
    border:1px solid #e8eaff; padding:14px; border-radius:14px;
  }
  label{font-size:.92rem; color:#1f2937; display:flex; flex-direction:column; gap:6px}
  select{padding:10px 12px; border:1px solid #cfd5ff; border-radius:10px; min-width:200px; background:#fff}
  .btn{
    padding:11px 16px; border-radius:10px; border:1px solid #cdd4ff;
    background:#fff; font-weight:700; cursor:pointer;
    transition:transform .06s, box-shadow .18s, border-color .18s;
  }
  .btn:hover{box-shadow:0 10px 20px rgba(17,24,39,.08); border-color:#a9b6ff}
  .btn:active{transform:translateY(1px)}

  .title{display:flex; flex-wrap:wrap; gap:8px; align-items:center}
  .chip{display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px;
        background:var(--chip); border:1px solid var(--chip-b); font-weight:600; font-size:.9rem}
  .chip b{font-weight:800}

  table{border-collapse:separate; border-spacing:0; width:100%; overflow:hidden; border-radius:14px}
  thead th{background:#f3f5ff; border-bottom:1px solid var(--line); padding:11px 10px; text-align:left}
  tbody td{border-bottom:1px solid var(--line); padding:10px}
  tbody tr:nth-child(odd){background:#fcfdff}
  tbody tr:hover{background:#f6f8ff}

  /* soft heat coloring for per-100k cell */
  .sev-null{background:#f9fafb}
  .sev-1{background:#e9fbf3}
  .sev-2{background:#fff7e6}
  .sev-3{background:#ffe8e6}
  .sev-4{background:#ffd9d6}
  td.rate{font-weight:800; border-left:1px solid #eef0fa}

  .subtle{color:var(--muted); font-size:.95rem}
  .h3{font-size:1.15rem; font-weight:800; margin:16px 0 8px}
</style>
</head><body>""")

    # Navigation bar
    h.append(nav_styles())
    h.append(build_nav("b2", "B"))

    h.append("<main>")

    # Header / chips
    h.append(f"""
      <div class="title">
        <h1 style="margin:0">Focused view — Infection by Economic Status</h1>
        <span class="chip">Phase: <b>{sel_phase or '—'}</b></span>
        <span class="chip">Disease: <b>{sel_disease or '—'}</b></span>
        <span class="chip">Year: <b>{sel_year or '—'}</b></span>
      </div>
      <p class="subtle">Choose a phase, infection type and year, then press <b>Show results</b>. Data are calculated as cases per 100,000 people using the matching country population for that year.</p>
    """)

    # Filters
    h.append("""
    <div class="card">
      <form method="get" class="filters">
        <label>Economic phase
          <select name="var_phase">""")
    h.append(_render_options(phases, sel_phase))
    h.append("""</select></label>
        <label>Infection type
          <select name="var_disease">""")
    h.append(_render_options(diseases, sel_disease))
    h.append("""</select></label>
        <label>Year
          <select name="var_year">""")
    h.append(_render_options(years, sel_year))
    h.append("""</select></label>
        <button class="btn" type="submit">Show results</button>
      </form>
    </div>
    """)

    # Main results table
    if rows:
        h.append('<div class="card">')
        h.append('<table aria-label="Per-country infection rates"><thead><tr>')
        h.append('<th>Country</th><th>Phase</th><th>Disease</th><th>Year</th><th>Cases per 100,000</th>')
        h.append('</tr></thead><tbody>')
        for disease, country, phase, year, per100k in rows:
            rate_txt = "N/A" if per100k is None else _fmt_float(per100k, 2)
            rate_class = _severity_class(per100k)
            h.append(
                f"<tr>"
                f"<td>{country}</td>"
                f"<td>{phase}</td>"
                f"<td>{disease}</td>"
                f"<td>{year}</td>"
                f'<td class="rate {rate_class}">{rate_txt}</td>'
                f"</tr>"
            )
        h.append("</tbody></table></div>")
    else:
        h.append('<div class="card"><em>No results yet (check filters or data).</em></div>')

    # Summary by economic phase
    if summary_rows:
        h.append('<div class="h3">Summary by economic phase</div>')
        h.append('<div class="card">')
        h.append('<table aria-label="Summary by phase"><thead><tr>')
        h.append('<th>Economic phase</th><th>Disease</th><th>Year</th><th>Total cases</th>')
        h.append('</tr></thead><tbody>')
        for phase, disease, year, total in summary_rows:
            h.append(f"<tr><td>{phase}</td><td>{disease}</td><td>{year}</td><td>{_fmt_int(total)}</td></tr>")
        h.append('</tbody></table></div>')

    h.append('<p class="subtle"><a href="/b1">← Back to B: Level 1</a></p>')
    h.append("</main></body></html>")
    return "".join(h)
