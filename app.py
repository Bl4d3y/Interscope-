from flask import Flask, request, Response, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interscope Proxy</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f7f9fc;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 60%;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                text-align: center;
                margin-top: 50px;
                color: #007bff;
            }
            form {
                text-align: center;
                margin-top: 30px;
            }
            input[type="text"] {
                width: 80%;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ccc;
                font-size: 16px;
            }
            button {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                background-color: #007bff;
                color: white;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Interscope Proxy</h1>
            <form action="/proxy" method="get">
                <input type="text" name="url" placeholder="Enter URL or search term">
                <button type="submit">Go</button>
            </form>
        </div>
    </body>
    </html>
    ''')

@app.route('/proxy')
def proxy():
    url_or_search = request.args.get('url')

    if not url_or_search:
        return "Please enter a URL or search term."

    if not url_or_search.startswith('http'):
        search_query = url_or_search.replace(' ', '+')
        search_url = f"https://www.google.com/search?q={search_query}"
        try:
            response = requests.get(search_url)
            return Response(response.content, content_type=response.headers['Content-Type'])
        except Exception as e:
            return f"Error: {str(e)}"
    
    try:
        response = requests.get(url_or_search)
        return Response(response.content, content_type=response.headers['Content-Type'])
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
