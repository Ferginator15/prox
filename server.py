from flask import Flask, request, Response, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Simple Web Proxy (Backend Powered)</title>
  <style>
    body { background:#111; color:#eee; font-family:Arial,sans-serif; margin:0; padding:0; }
    .container { max-width:700px; margin:30px auto; background:#222; padding:2em; border-radius:12px; box-shadow:0 2px 8px #0006; }
    h1 { text-align:center; color:#79b8ff; }
    form { display:flex; gap:10px; margin-bottom:16px; justify-content:center; }
    input[type="url"] { flex:1; padding:8px; border-radius:5px; border:none; font-size:1em; }
    button { background:#2ea44f; color:#fff; border:none; border-radius:5px; padding:8px 18px; font-size:1em; cursor:pointer; transition:background 0.2s; }
    button:hover { background:#22863a; }
    .note { color:#ffb347; font-size:0.98em; margin-bottom:0.6em; text-align:center; }
    #result { margin-top:2em; background:#181818; border-radius:8px; padding:1em; font-size:1em; }
    iframe { display: none; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Backend Web Proxy</h1>
    <div class="note">
      <b>Note:</b> This proxy works with most sites. JS/CSS may break for complex websites.<br>
      <b>Security:</b> This is a demo; sanitize in production!
    </div>
    <form method="get" action="/" autocomplete="off">
      <input type="url" name="url" placeholder="Enter a website URL (e.g. https://example.com)" required>
      <button type="submit">Fetch</button>
    </form>
    {% if data %}
    <div id="result">
      {{ data|safe }}
    </div>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    url = request.args.get("url")
    data = None
    if url:
        # Basic validation (for demo)
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        try:
            resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            resp.encoding = resp.apparent_encoding
            # Basic content filtering: only render text/html
            if 'text/html' in resp.headers.get('Content-Type', ''):
                data = resp.text
            else:
                data = "<pre>Non-HTML content fetched. Content-Type: {}</pre>".format(
                    resp.headers.get('Content-Type', 'unknown')
                )
        except Exception as e:
            data = f"<pre>Could not fetch: {e}</pre>"
    return render_template_string(HTML, data=data)

@app.route("/api/proxy")
def api_proxy():
    url = request.args.get("url")
    if not url:
        return "Missing url", 400
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    try:
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
