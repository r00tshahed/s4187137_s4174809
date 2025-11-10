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
        ORDER BY
            CASE
                WHEN coverage IS NULL OR CAST(coverage AS REAL) = 0 THEN 1  -- push N/A/0 to bottom
                ELSE 0
            END,
            CAST(coverage AS REAL) DESC,
            country ASC;  
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaccination Coverage by Country (Level 2)</title>
    <style>
        body {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            background-color: #ffffff;
            padding: 40px 20px;
            color: #1f2937;
            max-width: 1000px;
            margin: 0 auto;
        }
        
        h1 {
            color: #007bff;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 12px;
            margin-bottom: 25px;
            font-size: 2.5em;
            font-weight: 600;
        }

        nav {
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e5e7eb;
        }
        nav a {
            margin-right: 12px;
            text-decoration: none;
            color: #4b5563;
            font-size: 0.95em;
            padding: 4px 0;
            transition: color 0.15s;
        }
        nav a:hover {
            color: #007bff;
            text-decoration: underline;
        }

        .card {
            border: 1px solid #e5e7eb;
            padding: 20px;
            border-radius: 6px;
            background: #f9fafb;
            margin-bottom: 30px;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        select, button {
            padding: 10px 14px;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            font-size: 1em;
            transition: all 0.2s;
        }
        
        select:focus, button:focus {
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
            outline: none;
        }
        
        button {
            background-color: #007bff;
            color: white;
            cursor: pointer;
            font-weight: 500;
            margin-left: 20px;
        }
        
        button:hover {
            background-color: #0056b3;
        }

        table {
            border-collapse: collapse; 
            width: 100%;
            margin-top: 20px;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        th, td {
            border: none;
            border-bottom: 1px solid #f3f4f6;
            padding: 12px 16px;
            text-align: left;
        }
        th {
            background-color: #eef2ff;
            color: #374151;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8em;
        }
        tr:nth-child(odd) { background-color: #ffffff; }
        tr:nth-child(even) { background-color: #f9fafb; }
        tr:hover td { background-color: #eef2ff; transition: background-color 0.2s; }

        tr:nth-child(2) td {
            background-color: #d1fae5; 
            font-weight: 600; 
            color: #065f46;
            border-left: 4px solid #10b981;
        } 
        
        .footer-nav {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            font-size: 1.05em;
        }
        .footer-nav a {
            color: #4b5563;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 10px;
            border-radius: 4px;
            transition: color 0.2s, background-color 0.2s;
        }
        .footer-nav a:hover {
            background-color: #eef2ff;
            color: #007bff;
        }
            
    </style>
</head>
<body>
    <div class="container">
    <nav>
        <a href="/">A: Level 1</a>
        <a href="/page2" style="color: #007bff; font-weight: 600;">A: Level 2</a>
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
        <div class="footer-nav">
            <a href="/">← Back to Level 1</a> 
            <a href="/page3">Next → Level 3</a>
        </div>
        </div>
    </body>
    </html>
""")

    return "".join(h)

