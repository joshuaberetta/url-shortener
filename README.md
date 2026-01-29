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

The easiest way to deploy is using Docker Compose on a Droplet.

1.  **Create a Droplet**: Use the Docker marketplace image or install Docker on a plain Ubuntu droplet.

2.  **Copy Files**: Copy this project to your droplet (git clone or scp).

3.  **Configure**:
    Create a `.env` file in the project directory:
    ```bash
    SECRET_KEY=your_secure_random_string_here
    DATABASE_URL=sqlite:///./data/app.db
    ```

4.  **Run**:
    ```bash
    docker compose up -d --build
    ```

    The app will listen on port 80. The database will be stored in the `./data` folder on the host, ensuring persistence across restarts.

## Maintenance

- **View Logs**: `docker compose logs -f`
- **Restart**: `docker compose restart`
- **Update**:
  ```bash
  git pull
  docker compose up -d --build
  ```
