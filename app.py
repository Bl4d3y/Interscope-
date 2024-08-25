from flask import Flask, request, Response, render_template_string, g
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
from functools import lru_cache
import requests
import gzip
import io

app = Flask(__name__)
session = FuturesSession()

@lru_cache(maxsize=32)
def fetch_url(url):
    return requests.get(url)

@app.before_request
def before_request():
    g.cache = {}

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interscope</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f7f9fc;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .nav {
                background-color: #007bff;
                padding: 10px;
                text-align: center;
            }
            .nav a {
                color: white;
                margin: 0 15px;
                text-decoration: none;
                font-size: 18px;
            }
            .nav a:hover {
                text-decoration: underline;
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
        <div class="nav">
            <a href="/">Proxy</a>
            <a href="/games">Games</a>
            <a href="/credits">Credits</a>
        </div>
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
            response = fetch_url(search_url)
            return compress_response(response.content, response.headers['Content-Type'])
        except Exception as e:
            return f"Error: {str(e)}"
    
    try:
        if url_or_search in g.cache:
            content, content_type = g.cache[url_or_search]
        else:
            future = session.get(url_or_search)
            response = future.result()
            content = response.content
            content_type = response.headers['Content-Type']
            g.cache[url_or_search] = (content, content_type)
        
        if "text/html" in content_type.lower():
            soup = BeautifulSoup(content, 'html.parser')
            
            tags = soup.find_all(['a', 'link', 'script', 'img', 'video', 'source'])
            futures = []

            for tag in tags:
                if tag.has_attr('href'):
                    tag['href'] = requests.compat.urljoin(url_or_search, tag['href'])
                if tag.has_attr('src'):
                    src_url = requests.compat.urljoin(url_or_search, tag['src'])
                    futures.append(session.get(src_url))
                    tag['src'] = src_url

            [future.result() for future in futures]

            return compress_response(str(soup), content_type)
        else:
            return Response(content, content_type=content_type)
    
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/games')
def games():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interscope Games</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f7f9fc;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .nav {
                background-color: #007bff;
                padding: 10px;
                text-align: center;
            }
            .nav a {
                color: white;
                margin: 0 15px;
                text-decoration: none;
                font-size: 18px;
            }
            .nav a:hover {
                text-decoration: underline;
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
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                background-color: #007bff;
                color: white;
                margin: 10px 0;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
                cursor: pointer;
            }
            li:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Proxy</a>
            <a href="/games">Games</a>
            <a href="/credits">Credits</a>
        </div>
        <div class="container">
            <h1>Interscope Games</h1>
            <ul>
                <li><a href="/proxy?url=https%3A%2F%2F1v1.lol%2F" style="color: white; text-decoration: none;">1v1.lol</a></li>
                <li><a href="/proxy?url=https://shellshock.io" style="color: white; text-decoration: none;">Shell Shockers</a></li>
                <li><a href="/proxy?url=https://krunker.io" style="color: white; text-decoration: none;">Krunker.io</a></li>
            </ul>
        </div>
    </body>
    </html>
    ''')

@app.route('/credits')
def credits():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interscope Credits</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f7f9fc;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .nav {
                background-color: #007bff;
                padding: 10px;
                text-align: center;
            }
            .nav a {
                color: white;
                margin: 0 15px;
                text-decoration: none;
                font-size: 18px;
            }
            .nav a:hover {
                text-decoration: underline;
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
            p {
                text-align: center;
                margin-top: 20px;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Proxy</a>
            <a href="/games">Games</a>
            <a href="/credits">Credits</a>
        </div>
        <div class="container">
            <h1>Interscope Credits</h1>
            <p>This project was created by Lucas.</p>
            <p>Inspiration for this project Interstellar</p>
            <p>If there are any bugs or games you want me to add, add me on Discord @nevrloose</p>
        </div>
    </body>
    </html>
    ''')

def compress_response(content, content_type):
    if "text" in content_type.lower():
        compressed_content = gzip.compress(content.encode('utf-8'))
        response = Response(compressed_content, content_type=content_type)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = len(compressed_content)
    else:
        response = Response(content, content_type=content_type)
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
