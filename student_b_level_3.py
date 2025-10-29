import pyhtml
from navigation import build_nav, nav_styles  # keep

DB = "database/immunisation.db"

def _safe(s: str) -> str:
    return str(s).replace("'", "''") if s is not None else ""

def _qs(form_data, key, default=None):
    """Return single value from parse_qs dict; fall back to default."""
    v = form_data.get(key, default)
    if isinstance(v, list):
        v = v[0] if v else default
    return v if v is not None and v != "" else default

def get_page_html(form_data):
    # --- Load dropdown options ---
    diseases = [row[0] for row in pyhtml.get_results_from_query(
        DB, "SELECT DISTINCT description FROM Infection_Type ORDER BY description;"
    )]
    years = [row[0] for row in pyhtml.get_results_from_query(
        DB, "SELECT DISTINCT year FROM InfectionData ORDER BY year;"
    )]

    # sensible defaults
    default_disease = diseases[0] if diseases else "Measles"
    default_year    = years[-1] if years else 2020
    default_sort    = "per100k_desc"

    # unwrap parse_qs lists into single values
    sel_disease = _qs(form_data, "disease", default_disease)
    sel_year    = _qs(form_data, "year",    default_year)
    sel_sort    = _qs(form_data, "sort",    default_sort)

    # --- NEW: Clear button handling (same idea as Level 2) ---
    if _qs(form_data, "clear", "0") == "1":
        sel_disease = ""
        sel_year = ""     # blanking these prevents the query from running

    # sanitize/cast for SQL
    sel_disease_q = _safe(sel_disease)
    try:
        sel_year_q = int(sel_year)   # keep year numeric in SQL
    except (TypeError, ValueError):
        sel_year_q = int(default_year) if sel_year != "" else None
    sel_sort_q = _safe(sel_sort)

    # --- ORDER BY builder (use only output column names; valid for UNION) ---
    if sel_sort_q == "country_asc":
        order_by = "ORDER BY sort_key ASC, country ASC, per_100k DESC"
    elif sel_sort_q == "phase_asc":
        order_by = "ORDER BY sort_key ASC, economic_phase ASC, country ASC"
    else:  # default: per100k_desc
        order_by = "ORDER BY sort_key ASC, per_100k DESC, country ASC"

    # --- Single SQL (CTEs) ---
    rows = []
    if sel_disease and sel_year:  # only run when both present (mirrors Level 2 behaviour)
        year_clause = f"AND id.year = {sel_year_q}"
        sql = f"""
WITH base AS (
  SELECT
    c.CountryID,
    c.name AS country,
    e.phase AS economic_phase,
    it.description AS infection_type,
    id.year,
    id.cases,
    cp.population
  FROM InfectionData id
  JOIN Country c            ON c.CountryID = id.country
  JOIN Infection_Type it    ON it.id = id.inf_type
  LEFT JOIN CountryPopulation cp
                            ON cp.country = c.CountryID AND cp.year = id.year
  LEFT JOIN Economy e       ON e.economyID = c.economy
  WHERE it.description = '{sel_disease_q}' {year_clause}
),
rates AS (
  SELECT
    country, economic_phase, infection_type, year, cases, population,
    CASE
      WHEN cases IS NOT NULL AND population IS NOT NULL AND population > 0
        THEN (cases * 100000.0) / population
      ELSE NULL
    END AS per_100k
  FROM base
),
global_rate AS (
  SELECT
    MAX(infection_type) AS infection_type,
    MAX(year) AS year,
    (SUM(COALESCE(cases,0)) * 100000.0) / NULLIF(SUM(NULLIF(population,0)),0) AS global_per_100k
  FROM rates
)
SELECT
  'Global' AS country,
  NULL     AS economic_phase,
  g.infection_type,
  g.year,
  ROUND(g.global_per_100k, 2) AS per_100k,
  0 AS sort_key
FROM global_rate g

UNION ALL

SELECT
  r.country,
  r.economic_phase,
  r.infection_type,
  r.year,
  ROUND(r.per_100k, 2) AS per_100k,
  1 AS sort_key
FROM rates r
CROSS JOIN global_rate g
WHERE r.per_100k IS NOT NULL
  AND g.global_per_100k IS NOT NULL
  AND r.per_100k > g.global_per_100k
{order_by};
"""
        rows = pyhtml.get_results_from_query(DB, sql)

    # --- HTML ---
    h = []
    h.append("""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><title>Sub-Task B — Level 3 (Above Global)</title>
<style>
  :root { --line:#d7d7d7; --text:#111; --muted:#555; --box:#fafafa; }
  body{font-family:Segoe UI,Arial,sans-serif;margin:24px;line-height:1.5;color:var(--text)}
  .card{border:1px solid var(--line);border-radius:10px;padding:16px;margin:12px 0;background:#fff}
  form{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:8px 0 16px}
  label{font-size:.95rem}
  .muted{color:var(--muted)}
  input,select,button{padding:6px 10px}
  table{width:100%;border-collapse:collapse}
  th,td{border-bottom:1px solid var(--line);padding:8px;text-align:left}
  tr.global{background:#fff7cc;font-weight:600}

  /* --- Navigation card styling (same as Level 1) --- */
  .nav-card h2{ margin-bottom:8px }
  .nav-card nav{ display:flex; flex-wrap:wrap; gap:10px }
  .nav-card nav a{
    display:inline-block; padding:8px 12px; border-radius:12px;
    border:1px solid var(--line); background:#fff; text-decoration:none; color:inherit;
    transition:background .12s, border-color .12s, transform .05s;
  }
  .nav-card nav a:hover{ background:#f8fafc; border-color:#94a3b8 }
  .nav-card nav a[aria-current="page"], .nav-card nav a.active{
    background:#0f172a; color:#fff; border-color:#0f172a;
  }
</style>
</head><body>""")

    # Shared nav CSS
    h.append(nav_styles())

    # --- Top Navigation (same component as Level 1) ---
    h.append("""
<main>
  <div class="card nav-card" role="region" aria-labelledby="nav-heading">
    <h2 id="nav-heading">Navigation</h2>
""")
    h.append(build_nav("b3", "B"))
    h.append("</div>")  # close top nav

    # --- Page content ---
    h.append("""
  <div class="card">
    <h1>Above-average infection rate</h1>
    <p class="muted">Select a year and infection type. The global infection rate (per 100,000 people) is shown as the first row, followed by countries above that global average.</p>
    <form method="get" action="/b3">
      <label>Infection type
        <select name="disease">""")

    for d in diseases:
        sel = " selected" if str(d) == str(sel_disease) else ""
        h.append(f'<option value="{d}"{sel}>{d}</option>')

    h.append("""</select></label>
      <label>Year
        <select name="year">""")

    for y in years:
        sel = " selected" if str(y) == str(sel_year) else ""
        h.append(f'<option value="{y}"{sel}>{y}</option>')

    h.append("""</select></label>
      <label>Sort
        <select name="sort">
          <option value="per100k_desc"{0}>Per-100k (high→low)</option>
          <option value="country_asc"{1}>Country (A–Z)</option>
          <option value="phase_asc"{2}>Economic phase (A–Z)</option>
        </select>
      </label>
      <button type="submit">Update</button>
      <!-- NEW: Clear button to mirror Level 2 -->
      <button type="submit" name="clear" value="1">Clear</button>
    </form>
  </div>
""".format(
        " selected" if sel_sort == "per100k_desc" else "",
        " selected" if sel_sort == "country_asc" else "",
        " selected" if sel_sort == "phase_asc" else "",
    ))

    # Table
    h.append('<div class="card" role="region" aria-labelledby="results-heading">')
    h.append('<h2 id="results-heading">Results</h2>')
    h.append('<div class="table-wrap"><table aria-label="Countries above global infection rate"><thead><tr>')
    h.append('<th>Country</th><th>Economic phase</th><th>Infection</th><th>Year</th><th>Per 100,000</th>')
    h.append('</tr></thead><tbody>')

    if rows:
        for country, phase, disease, year, per100k, _ in rows:
            tr_class = ' class="global"' if country == "Global" else ""
            phase_txt = phase if phase is not None else "—"
            per_txt = "—" if per100k is None else f"{per100k:.2f}"
            h.append(f"<tr{tr_class}><td>{country}</td><td>{phase_txt}</td><td>{disease}</td><td>{year}</td><td>{per_txt}</td></tr>")
    else:
        h.append('<tr><td colspan="5" class="muted">No data for this selection.</td></tr>')

    h.append("</tbody></table></div></div>")

    # --- Bottom Navigation (same component as Level 1) ---
    h.append("""
  <div class="card nav-card" role="region" aria-labelledby="bottom-nav-heading" style="margin-top:24px;">
    <h2 id="bottom-nav-heading">Navigation</h2>
""")
    h.append(build_nav("b3", "B"))
    h.append("""
  </div>

</main>
</body></html>""")

    return "".join(h)
