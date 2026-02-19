# Deploying Invoice Maker with Google Login

## How it works

- **Authentication**: Streamlit's built-in Google OAuth (≥ 1.41). No third-party auth library needed.
- **Users**: Each Google account is a separate user. Their store profiles are saved in SQLite.
- **Mobile**: Streamlit's `centered` layout renders well on phone browsers out of the box.

---

## Step 1 — Create a Google OAuth 2.0 Client

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → **APIs & Services** → **Credentials**.
2. Click **Create Credentials** → **OAuth 2.0 Client ID**.
3. Application type: **Web application**.
4. Under **Authorised redirect URIs**, add:
   - `http://localhost:8501/oauth2callback` ← for local testing
   - `https://yourdomain.com/oauth2callback` ← for production (replace with your real domain)
5. Save. Copy the **Client ID** and **Client Secret**.

---

## Step 2 — Configure secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
[auth]
cookie_secret = "REPLACE_WITH_RANDOM_STRING"   # python -c "import secrets; print(secrets.token_hex(32))"
redirect_uri  = "https://yourdomain.com/oauth2callback"

[auth.google]
client_id     = "XXXX.apps.googleusercontent.com"
client_secret = "XXXX"
```

> **Never commit `secrets.toml`.** It is already in `.gitignore`.

---

## Step 3 — Run locally (no Docker)

```bash
pip install -r requirements.txt
streamlit run main.py
```

Open `http://localhost:8501` on your phone (on the same Wi-Fi) or browser.

---

## Step 4 — Deploy with Docker (self-hosted VPS / cloud VM)

Any VPS (DigitalOcean Droplet, AWS EC2, Google Compute Engine, Hetzner, etc.)
with Docker installed works. Port 8501 must be open or reverse-proxied.

```bash
# Clone the repo on your server
git clone <repo-url> && cd invoicegen

# Add your secrets (never commit this)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# … edit secrets.toml with your real values …

# Build and start
docker compose up -d --build
```

The app will be at `http://<server-ip>:8501`.

### Put it behind HTTPS with nginx + Certbot (recommended)

```nginx
# /etc/nginx/sites-available/invoicegen
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass         http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade    $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host       $host;
    }
}
```

```bash
sudo certbot --nginx -d yourdomain.com
```

---

## Option A — Render (free tier, easiest)

1. Push the repo to GitHub.
2. Go to [render.com](https://render.com) → New → **Web Service**.
3. Connect your GitHub repo.
4. Settings:
   - **Runtime**: Docker
   - **Port**: 8501
5. Under **Environment** → **Secret Files**, add `.streamlit/secrets.toml` with your real values.
6. Add a **Disk** (e.g. 1 GB) mounted at `/data` so the SQLite database survives redeploys.
7. Deploy. Render gives you a `*.onrender.com` HTTPS URL — use that as your `redirect_uri`.

---

## Option B — Railway

1. Push repo to GitHub.
2. New project → **Deploy from GitHub repo**.
3. Railway auto-detects the Dockerfile.
4. Set environment variables in the Railway dashboard (or use a `secrets.toml` volume).
5. Railway provides HTTPS automatically.

---

## Option C — Google Cloud Run (scales to zero, pay-per-use)

```bash
# Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT/invoicegen

# Deploy (Cloud Run is stateless — use Cloud SQL or Cloud Storage for the DB)
gcloud run deploy invoicegen \
  --image gcr.io/YOUR_PROJECT/invoicegen \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --set-secrets "/app/.streamlit/secrets.toml=invoicegen-secrets:latest"
```

> For Cloud Run, replace SQLite with **Cloud SQL (PostgreSQL)** or store the DB in **Cloud Storage** — Cloud Run containers are ephemeral.

---

## Mobile access checklist

| Item | Status |
|------|--------|
| HTTPS enabled | required by Google OAuth |
| `redirect_uri` matches your domain | required |
| Streamlit layout set to `centered` | already done in code |
| Port 8501 open or reverse-proxied | required |

Once deployed to a public HTTPS URL, any user can open it on their phone, tap **Sign in with Google**, and start creating invoices immediately.
