def get_page_html(form_data):
    print("About to return page home page...")
    page_html="""<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Global Immunisation Insight Portal</title>
    </head>
    <body>
        <h1>Global Immunisation Insight Portal</h1>
        <p>This is the first dynamically generated page!</p>
        <p><a href="/page2">Sub Task A Level 2</a></p>
        <p><a href="/page3">Sub task A Level 3</a></p>
        <p><a href="/b1">Sub Task B: Level 1 (Mission)</a></p>
        <p><a href="/b2">Sub Task B: Level 2</a></p>
        <p><a href="/b3">Sub Task B: Level 3</a></p>
        <img src="images/rmit.png" style="width: 30%; height: auto;">
    </body>
    </html>
    """
    return page_html
