# navigation.py
def build_nav(active: str, task: str) -> str:
    if task == "B":
        links = [("b1","Level 1 B (Mission)"),
                 ("b2","Level 2 B (By Economy)"),
                 ("b3","Level 3 B (Above Global)")]
    elif task == "A":
        links = [("a1","Level 1 A"),("a2","Level 2 A"),("a3","Level 3 A")]
    else:
        links = []

    html = ['<nav class="topnav" role="navigation" aria-label="Main navigation">']
    home_cls = ' class="active"' if active=="home" else ""
    html.append(f'<a href="/"{home_cls}>Home</a>')
    for code,label in links:
        cls = ' class="active"' if code==active else ""
        html.append(f'<a href="/{code}"{cls}>{label}</a>')
    html.append('</nav>')
    return "".join(html)

def nav_styles() -> str:
    return """
    <style>
      .topnav{display:flex;gap:12px;margin:12px 0 16px}
      .topnav a{padding:6px 10px;text-decoration:none;border-radius:8px;background:#eee;color:#222}
      .topnav a.active{background:#222;color:#fff}
      .topnav a:hover{background:#ddd}
    </style>
    """
