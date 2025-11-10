# navigation.py

def build_nav(*args, **kwargs) -> str:
    """
    Backward-compatible nav builder.
    Works with:
      build_nav("a3")            # new style
      build_nav("a3", "A")       # old style (second arg ignored)
      build_nav(active="a3")     # keyword style
    """
    # Extract "active" safely from any call pattern
    active = ""
    if "active" in kwargs:
        active = kwargs.get("active") or ""
    elif len(args) >= 1:
        active = args[0] or ""

    # Universal links (correct routes)
    links = [
        ("a1", "Level 1A", "/"),
        ("a2", "Level 2A", "/page2"),
        ("a3", "Level 3A", "/page3"),
        ("b1", "Level 1B", "/b1"),
        ("b2", "Level 2B", "/b2"),
        ("b3", "Level 3B", "/b3"),
    ]

    html = ['<nav class="topnav" role="navigation" aria-label="Main navigation">']
    for code, label, path in links:
        cls = ' class="active"' if code == active else ""
        html.append(f'<a href="{path}"{cls}>{label}</a>')
    html.append('</nav>')
    return "".join(html)


def nav_styles() -> str:
    return """
    <style>
      .topnav {
          display: flex;
          gap: 12px;
          margin: 12px 0 16px;
          flex-wrap: wrap;
      }
      .topnav a {
          padding: 6px 12px;
          text-decoration: none;
          border-radius: 8px;
          background: #f3f4f6;
          color: #1f2937;
          font-weight: 500;
          transition: background .2s, color .2s;
      }
      .topnav a:hover {
          background: #007bff;
          color: #fff;
      }
      .topnav a.active {
          background: #007bff;
          color: #fff;
          font-weight: 600;
      }
    </style>
    """
