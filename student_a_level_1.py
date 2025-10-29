def get_page_html(form_data):
    print("About to return page home page...")
    page_html="""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Global Immunisation Insight Portal</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f7f9fc;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }

        .container {
            background-color: #ffffff;
            border: 1px solid #d0d7de;
            padding: 40px;
            margin: 50px 20px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            max-width: 700px;
            width: 100%;
        }

        h1 {
            color: #0056b3;
            font-size: 2.5em;
            font-weight: 700;
            border-bottom: 3px solid #0056b3;
            padding-bottom: 15px;
            margin-top: 0;
            margin-bottom: 25px;
        }

        p {
            line-height: 1.6;
            margin-bottom: 15px;
        }

        p:first-of-type {
            font-size: 1.1em;
            color: #666;
            padding-bottom: 20px;
            border-bottom: 1px dashed #e0e0e0;
        }

        a {
            display: block;
            text-decoration: none;
            color: #1a1a1a;
            background-color: #f0f4f8;
            padding: 14px 20px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 5px solid transparent;
            transition: all 0.3s ease;
            font-weight: 500;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            position: relative;
        }

        a:hover {
            background-color: #e3eaf2;
            color: #0056b3;
            border-left: 5px solid #ff9900;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        img {
            display: block;
            margin-top: 40px;
            opacity: 0.6;
            transition: opacity 0.3s ease;
            border-radius: 4px;
        }
        
        img:hover {
            opacity: 1;
        }

    </style>
</head>
<body>
    <div class="container">
        <h1>Global Immunisation Insight Portal</h1>
        <p>This is the first dynamically generated page!</p>
        <p><a href="/page2">Sub Task A Level 2</a></p>
        <p><a href="/page3">Sub task A Level 3</a></p>
        <p><a href="/b1">Sub Task B: Level 1 (Mission)</a></p>
        <p><a href="/b2">Sub Task B: Level 2</a></p>
        <p><a href="/b3">Sub Task B: Level 3</a></p>
        <img src="images/rmit.png" style="width: 30%; height: auto;">
    </div>
</body>
</html>
    """
    return page_html
