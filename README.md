# URL Shortener

A minimal single-file URL shortener built with Flask and SQLite.
Paste a long URL, get a short one, track clicks, and manage your links —
all in one `app.py` file (HTML, CSS, and JavaScript are embedded).

## Stack

- **Backend:** Python 3.10+, Flask 3.0, `sqlite3` (stdlib)
- **Database:** SQLite — created automatically on first run
- **Frontend:** HTML5, CSS3, vanilla JavaScript (Fetch API)
- **No dependencies beyond Flask** — no ORM, no build step

## Features

- **Shorten URLs** — generates a random 6-character code.
- **Redirect** — `/<code>` redirects to the original URL and increments the click counter.
- **Click tracking** — each short link shows its hit count.
- **Delete links** — remove any entry from the list.
- **Input validation** — rejects URLs that don't start with `http://` or `https://`.
- **XSS protection** — user-supplied strings are HTML-escaped on the client.
- **Single file** — the entire application (routes + markup + styles + script) lives in `app.py`.

## Getting Started

1. Install Flask:

       pip install flask

2. Run the app:

       python app.py

3. Open http://127.0.0.1:5000

The database `urls.db` is created automatically on first launch.

## API

| Method | Endpoint             | Description                |
|--------|----------------------|----------------------------|
| GET    | `/`                  | Serve the frontend (HTML)  |
| GET    | `/api/urls`          | List all short links       |
| POST   | `/api/urls`          | Shorten a URL              |
| DELETE | `/api/urls/{code}`   | Delete a short link        |
| GET    | `/{code}`            | Redirect to the original   |

### Example

    curl -X POST http://127.0.0.1:5000/api/urls \
      -H "Content-Type: application/json" \
      -d '{"url": "https://example.com/some/long/path"}'

    # → {"code": "aB3xY9", "url": "https://example.com/some/long/path"}

    curl -L http://127.0.0.1:5000/aB3xY9

## What This Project Demonstrates

- Using **raw SQL with the `sqlite3` stdlib** — `CREATE`, `INSERT`,
  `SELECT`, `UPDATE`, `DELETE`, plus a uniqueness check.
- **REST API** with proper status codes and JSON responses.
- **HTTP redirects** (302) and side effects (incrementing counters).
- **Input validation** on the server and **HTML escaping** on the client.
- Serving a **complete SPA-style frontend** from a single file.

## Possible Extensions

- Custom short codes chosen by the user.
- Expiration dates for short links.
- QR code generation for each short link.
- Basic analytics (last visited, referrer).
- Rate limiting to prevent abuse.
- User accounts with private link collections.

## License

MIT
