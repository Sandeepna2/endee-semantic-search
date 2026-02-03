# Deployment Instructions

Your Semantic Search application is now fully containerized! This means you can deploy it easily to any host.

## 1. Run Everything with Docker
Instead of running python manually, you can now run the whole stack (Database + App) with one command:

```bash
docker-compose up --build -d
```

- **App**: http://localhost:5000
- **Database**: http://localhost:8080

## 2. Deploy to Cloud (Host)
You can deploy this folder to any VPS or Cloud Provider that supports Docker Compose.

### Option A: Render / Railway
1. Push this code to GitHub.
2. Connect your repo to Render/Railway.
3. Select "Docker" as the environment.
4. Note: Endee requires persistence (volumes), so a VPS is often better or a provider with persistent disk support.

### Option B: VPS (AWS EC2, DigitalOcean)
1. **Copy files** to your server:
   ```bash
   scp -r c:/endee-semantic-search user@your-server-ip:~/app
   ```
2. **SSH into server**:
   ```bash
   ssh user@your-server-ip
   cd ~/app
   ```
3. **Run**:
   ```bash
   docker-compose up -d --build
   ```
4. **Ingest Data** (First time only):
   Since the app container runs the app, you can exec into it to run ingestion:
   ```bash
   docker exec -it semantic-search-app python backend/ingest.py
   ```

## 3. Verify
Access your server IP on port 5000 (ensure firewall allows it).
