# Deployment Guide

## Development Environment Setup

### 1. Prerequisites

- Python 3.8+ installed
- MongoDB running locally (default: mongodb://localhost:27017)
- Git (for version control)

### 2. Initial Setup

```bash
# Clone or navigate to project directory
cd AI-Powered\ Personalized\ Learning\ Platform/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python setup_db.py

# Start development server
python app.py
```

Server starts at: **http://localhost:5000**

---

## Production Deployment

### 1. Environment Configuration

Create `.env` with production settings:

```
FLASK_ENV=production
DEBUG=False

MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/learning_platform
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET=<generate-strong-random-key>
```

Generate strong keys:

```python
import secrets
print(secrets.token_urlsafe(32))
```

### 2. Database Setup (MongoDB Atlas)

1. Create MongoDB Atlas account
2. Create cluster
3. Create database user with strong password
4. Whitelist IP addresses
5. Get connection string: `mongodb+srv://...`

### 3. Deploying with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Options:

- `-w 4`: 4 worker processes
- `-b 0.0.0.0:5000`: Bind to all interfaces, port 5000
- `--timeout 60`: Timeout per request

### 4. Reverse Proxy with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/app/frontend/static;
        expires 30d;
    }
}
```

### 5. HTTPS/SSL Certificate

Using Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 6. Systemd Service

Create `/etc/systemd/system/learning-app.service`:

```ini
[Unit]
Description=AI Learning Platform
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/app/backend
Environment="PATH=/path/to/app/backend/venv/bin"
ExecStart=/path/to/app/backend/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:5000 \
    --timeout 60 \
    app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable learning-app
sudo systemctl start learning-app
sudo systemctl status learning-app
```

### 7. Process Management with Supervisor

Install:

```bash
pip install supervisor
```

Create `/etc/supervisor/conf.d/learning-app.conf`:

```ini
[program:learning-app]
command=/path/to/app/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
directory=/path/to/app/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/learning-app.log
```

Manage:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status learning-app
```

### 8. Database Backups

**Automated MongoDB backup:**

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --uri="mongodb+srv://..." --out=$BACKUP_DIR/$DATE
# Keep last 7 days
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
EOF

chmod +x backup.sh

# Schedule with crontab
# 0 2 * * * /path/to/backup.sh  (daily at 2 AM)
```

### 9. Logging and Monitoring

**Application Logs:**

```python
import logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

**Monitor with:**

- CloudWatch (AWS)
- Datadog
- New Relic
- Sentry (error tracking)

### 10. Performance Optimization

**Enable caching:**

```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/topics')
@cache.cached(timeout=3600)
def get_topics():
    return apiClient.getTopics()
```

**Database optimization:**

```python
# Index frequently queried fields
db.quiz_attempts.create_index([("user_id", 1), ("timestamp", -1)])
db.user_progress.create_index([("user_id", 1)])
```

**Frontend optimization:**

- Enable gzip compression
- Minify CSS/JavaScript
- Cache static assets (30-day expiry)
- Use CDN for assets

### 11. Security Hardening

```python
# In app.py
app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,    # No JS access
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(days=30)
)

# Add security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### 12. Load Testing

Using Apache Bench:

```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:5000/api/health
```

Using Locust:

```bash
pip install locust

# Create locustfile.py
locust -f locustfile.py --host=http://localhost:5000
```

---

## Deployment Checklist

- [ ] `.env` configured with production values
- [ ] MongoDB Atlas cluster created and accessible
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`python setup_db.py`)
- [ ] JWT_SECRET and SECRET_KEY are strong random values
- [ ] CORS configured for specific domains
- [ ] SSL/HTTPS certificate installed
- [ ] Nginx/reverse proxy configured
- [ ] Gunicorn running with multiple workers
- [ ] Systemd/Supervisor service configured
- [ ] Logging enabled and monitored
- [ ] Database backups scheduled
- [ ] Health monitoring set up
- [ ] Load test passed
- [ ] Security headers configured
- [ ] API rate limiting configured

---

## Deployment Platforms

### Heroku

```bash
# Install Heroku CLI
npm install -g heroku

# Login and create app
heroku login
heroku create learning-platform

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set MONGODB_URI=...

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

### AWS (EC2)

1. Launch Ubuntu instance
2. SSH into instance
3. Install Python, MongoDB, Nginx
4. Clone repository
5. Set up virtual environment
6. Configure and deploy with Gunicorn
7. Set up SSL with Certbot
8. Configure security groups (port 80, 443, 22)

### DigitalOcean

1. Create Droplet (Ubuntu 20.04)
2. SSH access
3. Install dependencies
4. Deploy using Systemd service
5. Configure Nginx and SSL
6. Enable firewall

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend .
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Create `docker-compose.yml`:

```yaml
version: "3"
services:
  mongodb:
    image: mongo:5
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  flask_app:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - mongodb
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/learning_platform

volumes:
  mongo_data:
```

Run:

```bash
docker-compose up -d
```

---

## Monitoring Checklist

- [ ] Application uptime monitoring
- [ ] Database connection monitoring
- [ ] API response time tracking
- [ ] Error rate monitoring
- [ ] User authentication failures tracking
- [ ] Disk space usage monitoring
- [ ] Memory usage monitoring
- [ ] CPU usage monitoring
- [ ] Network throughput monitoring

---

## Scaling Strategy

1. **Vertical Scaling:** Increase server resources (CPU, RAM)
2. **Horizontal Scaling:** Add load balancer + multiple app servers
3. **Database Scaling:** MongoDB sharding for large datasets
4. **Caching:** Redis for frequently accessed data
5. **CDN:** CloudFlare or AWS CloudFront for static assets

---

## Troubleshooting Production Issues

### High Memory Usage

- Check for memory leaks in code
- Limit Gunicorn workers
- Monitor database connections

### Slow API Responses

- Check MongoDB indexes
- Enable caching
- Analyze slow queries
- Increase server resources

### Database Connection Issues

- Verify MongoDB URI
- Check IP whitelist in MongoDB Atlas
- Review connection pool settings

### SSL Certificate Issues

- Check certificate expiration
- Ensure auto-renewal is enabled
- Verify domain DNS records
