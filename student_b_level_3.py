import pyhtml
from navigation import build_nav, nav_styles

DB = "database/immunisation.db"

# ---------- helpers ----------
def _safe(s): 
    return str(s).replace("'", "''") if s is not None else ""

def _qs(form_data, key, default=None):
    v = form_data.get(key, default)
    if isinstance(v, list):
        v = v[0] if v else default
    return default if v in (None, "") else v

def _opts(sql):
    return [r[0] for r in pyhtml.get_results_from_query(DB, sql)]

def _opt_html(options, selected, placeholder=None):
    out = []
    if placeholder is not None:
        sel = " selected" if selected in (None, "", placeholder) else ""
        out.append(f'<option value=""{sel}>{placeholder}</option>')
    for v in options:
        sel = " selected" if str(v) == str(selected) else ""
        out.append(f'<option value="{v}"{sel}>{v}</option>')
    return "".join(out)

def _fmt_num(x, digits=2):
    return "—" if x is None else f"{float(x):.{digits}f}"

# ---------- page ----------
def get_page_html(form_data):
    # dropdown data
    diseases = _opts("SELECT DISTINCT description FROM Infection_Type ORDER BY description;")
    years    = _opts("SELECT DISTINCT year FROM InfectionData ORDER BY year;")
    phases   = _opts("SELECT DISTINCT phase FROM Economy ORDER BY phase;")

    # sensible defaults
    default_disease = diseases[0] if diseases else "Measles"
    default_year    = years[-1] if years else 2020

    # GET params
    sel_disease = _qs(form_data, "disease", default_disease)
    sel_year    = _qs(form_data, "year",    default_year)
    sel_phase   = _qs(form_data, "phase",   "")      # optional
    sel_sort    = _qs(form_data, "sort",    "per100k_desc")
    compare     = _qs(form_data, "cmp",     "above") # above | below | all
    topn        = _qs(form_data, "topn",    "50")    # string; cast later

    # Clear -> blank selections (prevents query run)
    if _qs(form_data, "clear", "0") == "1":
        sel_disease, sel_year, sel_phase = "", "", ""

    # sanitize / cast
    disease_q = _safe(sel_disease)
    phase_q   = _safe(sel_phase) if sel_phase else ""
    try:
        year_q = int(sel_year) if sel_year != "" else None
    except ValueError:
        year_q = None
    try:
        topn_q = max(1, min(500, int(topn)))
    except ValueError:
        topn_q = 50

    # order by
    if sel_sort == "country_asc":
        order_by = "ORDER BY sort_key ASC, country ASC, per_100k DESC"
    elif sel_sort == "phase_asc":
        order_by = "ORDER BY sort_key ASC, economic_phase ASC, country ASC"
    else:
        order_by = "ORDER BY sort_key ASC, per_100k DESC, country ASC"

    # compare relation
    if compare == "below":
        rel = "<"
    elif compare == "all":
        rel = "IS NOT NULL"  # will be handled specially
    else:
        rel = ">"

    # build SQL only when required inputs exist
    rows = []
    summary = {"global_rate": None, "matched": 0, "compare": compare}
    if sel_disease and year_q is not None:
        phase_clause = f" AND e.phase = '{phase_q}'" if phase_q else ""
        sql = f"""
WITH base AS (
  SELECT
    c.CountryID,
    c.name AS country,
    COALESCE(e.phase,'') AS economic_phase,
    it.description AS infection_type,
    id.year,
    id.cases,
    cp.population
  FROM InfectionData id
  JOIN Country c         ON c.CountryID = id.country
  JOIN Infection_Type it ON it.id       = id.inf_type
  LEFT JOIN CountryPopulation cp
                         ON cp.country = c.CountryID AND cp.year = id.year
  LEFT JOIN Economy e    ON e.economyID = c.economy
  WHERE it.description = '{disease_q}' AND id.year = {year_q} {phase_clause}
),
rates AS (
  SELECT
    country, economic_phase, infection_type, year, cases, population,
    CASE WHEN population IS NOT NULL AND population > 0 AND cases IS NOT NULL
      THEN (cases * 100000.0) / population
      ELSE NULL
    END AS per_100k
  FROM base
),
global_rate AS (
  SELECT 
    (SUM(COALESCE(cases,0)) * 100000.0) / NULLIF(SUM(NULLIF(population,0)),0) AS g
  FROM rates
)
SELECT 'Global' AS country, NULL AS economic_phase, '{disease_q}' AS infection_type,
       {year_q} AS year, ROUND(g.g,2) AS per_100k, 0 AS sort_key
FROM global_rate g
UNION ALL
SELECT r.country, r.economic_phase, r.infection_type, r.year,
       ROUND(r.per_100k,2) AS per_100k, 1 AS sort_key
FROM rates r
CROSS JOIN global_rate g
WHERE r.per_100k IS NOT NULL
""" + (
    "" if compare == "all" else f"  AND r.per_100k {rel} g.g\n"
) + f"""{order_by}
LIMIT {topn_q + 1}; -- +1 because we include the Global row
"""
        rows = pyhtml.get_results_from_query(DB, sql)

        # compute summary
        if rows:
            # first row is global
            try:
                summary["global_rate"] = rows[0][4]
            except Exception:
                summary["global_rate"] = None
            summary["matched"] = max(0, len(rows) - 1)

    # -------------- HTML --------------
    h = []
    h.append("""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><title>Sub-Task B — Level 3 (Above / Below Global)</title>
<style>
  :root { --line:#d7d7d7; --ink:#0f172a; --muted:#6b7280; --pill:#eef2ff; }
  html,body{background:#f8fafc; color:var(--ink); font-family:Segoe UI,Arial,sans-serif}
  main{max-width:1100px; margin:24px auto; padding:0 16px}
  .card{background:#fff; border:1px solid var(--line); border-radius:14px; padding:16px; margin:12px 0}
  .muted{color:var(--muted)}
  form{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:8px 0 8px}
  label{font-size:.95rem}
  select,input,button{padding:8px 10px; border-radius:10px; border:1px solid #cbd5e1}
  button{cursor:pointer; background:#fff}
  .actions{display:flex; gap:8px; flex-wrap:wrap}
  table{width:100%;border-collapse:collapse}
  th,td{border-bottom:1px solid #eef2f7; padding:10px; text-align:left}
  thead th{background:#f1f5f9}
  tr.global{background:#fff7cc; font-weight:600}
  tr:nth-child(even):not(.global){background:#fcfcff}
  .pill{display:inline-block; padding:4px 10px; border-radius:999px; background:var(--pill); border:1px solid #e2e8f0; font-weight:600}
  .grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:12px}
</style>
</head><body>
<main>
""")

    # Top shared nav
    h.append(nav_styles())
    h.append(build_nav("b3", "B"))

    # Header + form
    h.append("""
<div class="card">
  <h1>Global benchmark comparison</h1>
  <p class="muted">See countries whose infection rate is <b>above</b> or <b>below</b> the global average for a selected disease and year. Optionally filter by economic phase.</p>
  <form method="get" action="/b3">
    <label>Infection type
      <select name="disease">""")
    h.append(_opt_html(diseases, sel_disease))
    h.append("""</select></label>

    <label>Year
      <select name="year">""")
    h.append(_opt_html(years, sel_year))
    h.append("""</select></label>

    <label>Economic phase
      <select name="phase">""")
    h.append(_opt_html(phases, sel_phase, placeholder="All phases"))
    h.append("""</select></label>

    <label>Compare
      <select name="cmp">
        <option value="above"{0}>Above global</option>
        <option value="below"{1}>Below global</option>
        <option value="all"{2}>All (show global + all countries)</option>
      </select>
    </label>

    <label>Sort
      <select name="sort">
        <option value="per100k_desc"{3}>Per-100k (high→low)</option>
        <option value="country_asc"{4}>Country (A–Z)</option>
        <option value="phase_asc"{5}>Economic phase (A–Z)</option>
      </select>
    </label>

    <label>Top-N
      <input type="number" min="1" max="500" name="topn" value="{6}" />
    </label>

    <div class="actions">
      <button type="submit">Update</button>
      <button type="submit" name="clear" value="1">Clear</button>
    </div>
  </form>
</div>
""".format(
        " selected" if compare == "above" else "",
        " selected" if compare == "below" else "",
        " selected" if compare == "all"   else "",
        " selected" if sel_sort == "per100k_desc" else "",
        " selected" if sel_sort == "country_asc"  else "",
        " selected" if sel_sort == "phase_asc"    else "",
        topn_q
    ))

    # Summary panel
    h.append('<div class="card"><div class="grid">')
    h.append(f'<div><div class="pill">Global rate</div><p style="margin:.4rem 0 0">{_fmt_num(summary["global_rate"])}</p></div>')
    label = {"above":"Countries above", "below":"Countries below", "all":"Countries listed"}[compare]
    h.append(f'<div><div class="pill">{label}</div><p style="margin:.4rem 0 0">{summary["matched"]}</p></div>')
    phase_text = sel_phase if sel_phase else "All phases"
    h.append(f'<div><div class="pill">Phase filter</div><p style="margin:.4rem 0 0">{phase_text}</p></div>')
    h.append('</div></div>')

    # Results table
    h.append('<div class="card" role="region" aria-labelledby="results-heading">')
    h.append('<h2 id="results-heading">Results</h2>')
    h.append('<div class="table-wrap"><table aria-label="Global comparison results"><thead><tr>')
    h.append('<th>Country</th><th>Economic phase</th><th>Infection</th><th>Year</th><th>Per 100,000</th>')
    h.append('</tr></thead><tbody>')

    if rows:
        for country, phase, disease, year, per100k, _ in rows:
            tr_class = ' class="global"' if country == "Global" else ""
            phase_txt = phase if phase not in (None, "") else "—"
            h.append(f"<tr{tr_class}><td>{country}</td><td>{phase_txt}</td><td>{disease}</td><td>{year}</td><td>{_fmt_num(per100k)}</td></tr>")
    else:
        h.append('<tr><td colspan="5" class="muted">No data for this selection.</td></tr>')

    h.append("</tbody></table></div></div>")

    # Bottom nav
    h.append(build_nav("b3", "B"))
    h.append("</main></body></html>")
    return "".join(h)
