import pyhtml

DB = "database/immunisation.db"

def _options(db, sql):
    """Helper: Get distinct values for dropdowns."""
    return [r[0] for r in pyhtml.get_results_from_query(db, sql)]

def _get_single(form_data, key, default=None):
    """Helper: Get single value from form input."""
    vals = form_data.get(key, [])
    return vals[0] if vals else default

def get_page_html(form_data):
    # Dropdown options
    antigens = _options(DB, "SELECT DISTINCT antigen FROM Vaccination ORDER BY antigen;")
    years = _options(DB, "SELECT DISTINCT year FROM Vaccination ORDER BY year;")

    # Selected values
    sel_antigen = _get_single(form_data, "antigen", antigens[0] if antigens else "")
    sel_year = _get_single(form_data, "year", years[0] if years else "")
    run = _get_single(form_data, "run", "0")

    # Query results
    rows = []
    if run == "1":
        print(f"Running query for antigen={sel_antigen}, year={sel_year}")  # Debug info
        sql = f"""
        SELECT country, antigen, year, coverage
        FROM Vaccination
        WHERE antigen = '{sel_antigen}'
          AND year = CAST('{sel_year}' AS INTEGER)
        ORDER BY coverage DESC;
        """
        rows = pyhtml.get_results_from_query(DB, sql)
        print("DEBUG rows returned:", len(rows))

    # Build HTML
    h = []
    h.append("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Vaccination Coverage by Country (Level 2)</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 24px;
                background-color: #fdfdfd;
            }
            h1 {
                color: #222;
            }
            .card {
                border: 1px solid #ccc;
                padding: 16px;
                border-radius: 8px;
                background: #fafafa;
                margin-bottom: 20px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 16px;
            }
            th, td {
                border: 1px solid #bbb;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #e8e8e8;
            }
            tr:nth-child(odd) { background-color: #f9f9f9; }
            tr:nth-child(1) td { background-color: #dff0d8; font-weight: bold; } /* highlight top row */
            nav a {
                margin-right: 12px;
                text-decoration: none;
                color: #0055aa;
            }
            nav a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <nav>
            <a href="/">A: Level 1</a>
            <a href="/page2">A: Level 2</a>
            <a href="/page3">A: Level 3</a>
            <a href="/b1">B: Level 1</a>
            <a href="/b2">B: Level 2</a>
        </nav>

        <h1>Vaccination Coverage by Country</h1>
        <p>Select an <b>Antigen</b> and <b>Year</b> to view coverage by country.</p>

        <div class="card">
            <form method="get">
                Antigen:
                <select name="antigen">
    """)

    # Antigen dropdown
    for a in antigens:
        selected = "selected" if a == sel_antigen else ""
        h.append(f"<option {selected}>{a}</option>")

    # Year dropdown
    h.append("</select> Year: <select name='year'>")
    for y in years:
        selected = "selected" if y == sel_year else ""
        h.append(f"<option {selected}>{y}</option>")

    h.append("</select> <button name='run' value='1'>Run</button></form></div>")

    # Display table results
    if rows:
        h.append("<table><tr><th>Country</th><th>Antigen</th><th>Year</th><th>Coverage (%)</th></tr>")
        for r in rows:
            country, antigen, year, coverage = r
            try:
                coverage_display = f"{float(coverage):.2f}"
            except (ValueError, TypeError):
                coverage_display = "N/A"
            h.append(f"<tr><td>{country}</td><td>{antigen}</td><td>{year}</td><td>{coverage_display}</td></tr>")
        h.append("</table>")
    elif run == "1":
        h.append("<p><em>No data found for the selected antigen and year.</em></p>")

    # Navigation links
    h.append("""
        <p><a href="/">← Back to Level 1</a> | <a href="/page3">Next → Level 3</a></p>
    </body>
    </html>
    """)

    return "".join(h)

