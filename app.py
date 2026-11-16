import sqlite3
import string
import random
from flask import Flask, request, jsonify, redirect, Response

app = Flask(__name__)
DB = "urls.db"


def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                code     TEXT UNIQUE NOT NULL,
                url      TEXT NOT NULL,
                clicks   INTEGER NOT NULL DEFAULT 0,
                created  TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)


def gen_code(n=6):
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=n))


@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")


@app.route("/api/urls", methods=["GET"])
def list_urls():
    with sqlite3.connect(DB) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT code, url, clicks, created FROM urls ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/urls", methods=["POST"])
def create_url():
    data = request.get_json() or {}
    url = (data.get("url") or "").strip()

    if not url.startswith(("http://", "https://")):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    code = gen_code()
    with sqlite3.connect(DB) as con:
        # гарантируем уникальность
        while con.execute("SELECT 1 FROM urls WHERE code=?", (code,)).fetchone():
            code = gen_code()
        con.execute("INSERT INTO urls (code, url) VALUES (?, ?)", (code, url))

    return jsonify({"code": code, "url": url}), 201


@app.route("/api/urls/<code>", methods=["DELETE"])
def delete_url(code):
    with sqlite3.connect(DB) as con:
        cur = con.execute("DELETE FROM urls WHERE code=?", (code,))
        if cur.rowcount == 0:
            return jsonify({"error": "not found"}), 404
    return "", 204


@app.route("/<code>")
def follow(code):
    with sqlite3.connect(DB) as con:
        row = con.execute("SELECT url FROM urls WHERE code=?", (code,)).fetchone()
        if not row:
            return "Not found", 404
        con.execute("UPDATE urls SET clicks = clicks + 1 WHERE code=?", (code,))
    return redirect(row[0], code=302)


HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>URL Shortener</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#f4f6fb;
       color:#1f2933;padding:2rem 1rem;display:flex;flex-direction:column;
       align-items:center;min-height:100vh}
  h1{font-size:1.8rem;margin-bottom:1.5rem}
  h1::before{content:"🔗 "}
  form{display:grid;grid-template-columns:1fr auto;gap:.5rem;width:100%;
       max-width:700px;background:#fff;padding:1rem;border-radius:10px;
       box-shadow:0 2px 8px rgba(0,0,0,.06);margin-bottom:1rem}
  input,button{font:inherit;padding:.65rem .9rem;border-radius:8px;
       border:1px solid #e5e7eb;outline:none}
  input:focus{border-color:#6c5ce7;box-shadow:0 0 0 3px rgba(108,92,231,.15)}
  button{background:#6c5ce7;color:#fff;border:none;font-weight:600;cursor:pointer}
  button:hover{background:#5a4bd1}
  ul{list-style:none;width:100%;max-width:700px;display:flex;
     flex-direction:column;gap:.5rem}
  li{background:#fff;padding:.8rem 1rem;border-radius:10px;
     box-shadow:0 2px 8px rgba(0,0,0,.06);display:flex;gap:.75rem;
     align-items:center;border-left:4px solid #6c5ce7;animation:fade .2s ease}
  li a{color:#6c5ce7;font-weight:600;text-decoration:none;min-width:110px}
  li .url{flex:1;font-size:.9rem;color:#6b7280;overflow:hidden;
          text-overflow:ellipsis;white-space:nowrap}
  li .clicks{font-size:.8rem;background:rgba(108,92,231,.12);color:#6c5ce7;
             padding:.15rem .55rem;border-radius:10px;font-weight:600}
  li button{background:transparent;color:#e5484d;border:1px solid transparent;
            padding:.25rem .5rem;font-size:.9rem}
  li button:hover{background:#e5484d;color:#fff}
  li.empty{justify-content:center;color:#6b7280;font-style:italic;
           border-left-color:transparent}
  @keyframes fade{from{opacity:0;transform:translateY(-3px)}to{opacity:1}}
</style>
</head>
<body>
  <h1>URL Shortener</h1>
  <form id="f">
    <input id="url" type="url" placeholder="https://example.com/long/path" required>
    <button>Сократить</button>
  </form>
  <ul id="list"></ul>

<script>
const f = document.getElementById("f");
const list = document.getElementById("list");

const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

async function load() {
  const data = await (await fetch("/api/urls")).json();
  if (data.length === 0) {
    list.innerHTML = '<li class="empty">Ссылок пока нет</li>';
    return;
  }
  list.innerHTML = data.map(u => `
    <li>
      <a href="/${esc(u.code)}" target="_blank">/${esc(u.code)}</a>
      <span class="url" title="${esc(u.url)}">${esc(u.url)}</span>
      <span class="clicks">${u.clicks}</span>
      <button data-code="${esc(u.code)}">✕</button>
    </li>`).join("");

  list.querySelectorAll("button").forEach(b => {
    b.onclick = async () => {
      await fetch(`/api/urls/${b.dataset.code}`, {method: "DELETE"});
      load();
    };
  });
}

f.onsubmit = async e => {
  e.preventDefault();
  const url = document.getElementById("url").value.trim();
  const res = await fetch("/api/urls", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({url})
  });
  if (!res.ok) {
    const err = await res.json();
    alert(err.error || "Ошибка");
    return;
  }
  f.reset();
  load();
};

load();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
