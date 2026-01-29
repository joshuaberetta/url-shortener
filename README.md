# Simple URL Shortener

A lightweight URL shortener built with FastAPI, SQLite, and Jinja2 templates.

## Features
- User registration and login
- Custom URL slugs
- Click tracking
- Simple dashboard
- Dockerized for easy deployment

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Open http://localhost:8000

## Deployment (DigitalOcean Droplet)

### Initial Server Setup (Recommended)
Since you are logged in as `root`, it is highly recommended to create a standard user for security before deploying.

1.  **Create a new user** (replace `kobo` with your username):
    ```bash
    adduser kobo
    usermod -aG sudo kobo
    ```

2.  **Add user to Docker group** (so you can run docker without sudo):
    ```bash
    usermod -aG docker kobo
    ```

3.  **Setup SSH for the new user**:
    ```bash
    # Copy root's SSH keys to the new user so you can log in as 'kobo'
    rsync --archive --chown=kobo:kobo ~/.ssh /home/kobo
    ```

4.  **Enable Firewall**:
    ```bash
    # Allow SSH connections
    ufw allow OpenSSH
    # Allow HTTP and HTTPS
    ufw allow 80
    ufw allow 443
    # Enable the firewall
    ufw enable
    ```

5.  **Switch to the new user**:
    ```bash
    su - kobo
    ```

You can now deploy this application as a standalone service or alongside other applications using Nginx.

### Option 1: Standalone (Simple)
Use this if this is the only application running on your server.

1.  **Create a Droplet**: Use the Docker marketplace image or install Docker on a plain Ubuntu droplet.

2.  **Clone & Setup**:
    ```bash
    git clone <your-repo-url>
    cd url-shortener
    
    # Create .env configuration
    echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
    echo "DATABASE_URL=sqlite:///./data/app.db" >> .env
    ```

3.  **Run**:
    ```bash
    # Default runs on port 80
    docker compose up -d --build
    ```
    The app will be accessible directly at your server's IP address.

### Option 2: Multiple Apps with Nginx (Recommended)
Use this method to run multiple applications on the same Droplet using Nginx as a reverse proxy.

#### 1. Prerequisites
Install Nginx and Certbot on your Droplet:
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y
```

#### 2. Configure the App
Run the app on a specific local port (e.g., `8001`) to avoid conflicts.

1.  Create `.env` with a custom `APP_PORT`:
    ```bash
    SECRET_KEY=your_secure_random_string_here
    DATABASE_URL=sqlite:///./data/app.db
    APP_PORT=8001
    ```

2.  Start the container:
    ```bash
    docker compose up -d --build
    ```

#### 3. Configure Nginx
Create a server block to route traffic from your domain to the app's port.

1.  Create a configuration file:
    ```bash
    sudo vim /etc/nginx/sites-available/url-shortener
    ```

2.  Paste the following configuration (replace `yourdomain.com` with your actual domain):
    ```nginx
    server {
        listen 80;
        server_name yourdomain.com;

        location / {
            proxy_pass http://127.0.0.1:8001;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

3.  Enable the site and restart Nginx:
    ```bash
    sudo ln -s /etc/nginx/sites-available/url-shortener /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    ```

#### 4. Setup SSL (HTTPS)
Secure your specific domain automatically with Let's Encrypt:
```bash
sudo certbot --nginx -d yourdomain.com
```

### Adding More Apps
To host additional applications on the same Droplet:
1.  Run the new app on a different port (e.g., `8002`).
2.  Create a new Nginx config file that normally listens on port 80 but `proxy_pass` to `http://127.0.0.1:8002`.
3.  Enable the config and run Certbot.

## Maintenance

- **View Logs**: `docker compose logs -f`
- **Restart**: `docker compose restart`
- **Update**:
  ```bash
  git pull
  docker compose up -d --build
  ```
