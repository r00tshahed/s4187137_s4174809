import pyhtml
from navigation import build_nav, nav_styles   # ⬅️ add this

DB = "database/immunisation.db"

def _opts(db, sql):
    return [r[0] for r in pyhtml.get_results_from_query(db, sql)]

def _get(form_data, key, default=None):
    vals = form_data.get(key, [])
    return vals[0] if vals else default

def get_page_html(form_data):
    # dropdown data
    phases   = _opts(DB, "SELECT DISTINCT phase FROM Economy ORDER BY phase;")
    diseases = _opts(DB, "SELECT DISTINCT description FROM Infection_Type ORDER BY description;")
    years    = _opts(DB, "SELECT DISTINCT year FROM InfectionData ORDER BY year;")

    # selected values (default to first available so first load shows results)
    sel_phase   = _get(form_data, "var_phase",   phases[0] if phases else "")
    sel_disease = _get(form_data, "var_disease", diseases[0] if diseases else "")
    sel_year    = _get(form_data, "var_year",    str(years[0]) if years else "")

    # run the query (no JS, no run flag — we always compute with current selections)
    rows = []
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

    def _render_options(options, selected):
        if not options:
            return '<option disabled>None</option>'
        return "".join(
            f'<option value="{v}"{" selected" if str(v)==str(selected) else ""}>{v}</option>'
            for v in options
        )

    # -------- HTML (no <script>, just HTML+CSS) --------
    h = []
    h.append("""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><title>Sub-Task B – Level 2 (No JS)</title>
<style>
  body{font-family:Segoe UI,Arial,sans-serif;margin:24px;line-height:1.5}
  .card{border:1px solid #ddd;border-radius:10px;padding:16px;margin:12px 0;background:#fff}
  table{border-collapse:collapse;width:100%}
  th,td{border-bottom:1px solid #eee;text-align:left;padding:8px}
  select,button{padding:6px 10px;margin-right:8px}
  button{border:1px solid #bbb;border-radius:8px;background:#f5f5f5;cursor:pointer}
</style>
</head><body>""")

    # ✅ Shared nav (Home + B1 + B2 + B3) — current page highlighted
    h.append(nav_styles())
    h.append(build_nav("b2", "B"))

    # Page heading + instructions
    h.append("""
<h1>Focused view — Infection by Economic Status</h1>
<p>Choose an <b>economic phase</b>, <b>infection type</b>, and <b>year</b>, then press <b>Show results</b>.</p>

<div class="card">
  <form method="get">
    <label>Economic phase
      <select name="var_phase">""")
    h.append(_render_options(phases, sel_phase))
    h.append("""</select>
    </label>
    <label>Infection type
      <select name="var_disease">""")
    h.append(_render_options(diseases, sel_disease))
    h.append("""</select>
    </label>
    <label>Year
      <select name="var_year">""")
    h.append(_render_options(years, sel_year))
    h.append("""</select>
    </label>
    <button type="submit">Show results</button>
  </form>
</div>
""")

    if rows:
        h.append('<div class="card"><table><thead><tr>')
        h.append('<th>Country</th><th>Phase</th><th>Disease</th><th>Year</th><th>Cases per 100k</th>')
        h.append('</tr></thead><tbody>')
        for disease, country, phase, year, per100k in rows:
            h.append(f"<tr><td>{country}</td><td>{phase}</td><td>{disease}</td><td>{year}</td><td>{'N/A' if per100k is None else per100k}</td></tr>")
        h.append("</tbody></table></div>")
    else:
        h.append('<div class="card"><em>No results yet (check filters or data).</em></div>')

    h.append('<p><a href="/b1">Back to B: Level 1</a></p></body></html>')
    return "".join(h)
