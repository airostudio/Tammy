# Deployment Guide - ENDCOM.NET AI Assistant

This guide covers different deployment options for ENDCOM.NET.

## 🚀 Quick Deploy Options

### Option 1: Vercel (Recommended for Web Access)

ENDCOM.NET is configured for Vercel deployment with both API and web interface.

**Deploy to Vercel:**

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Deploy:**
```bash
vercel
```

3. **Configure Environment Variables:**
In your Vercel dashboard, add:
- `DATABASE_URL` - Your database connection string
- `SECRET_KEY` - A secure random key
- `OPENAI_API_KEY` - (Optional) For enhanced AI features

4. **Access your deployment:**
- Main site: `https://your-app.vercel.app`
- API docs: `https://your-app.vercel.app/docs`

**Note:** Vercel's free tier has limitations for database persistence. For production, use an external database like:
- PostgreSQL (Supabase, Neon, Railway)
- MongoDB Atlas
- PlanetScale

### Option 2: Docker

**Quick Start:**
```bash
docker-compose up -d
```

**Custom Docker Deployment:**
```bash
# Build
docker build -t endcom-net-ai .

# Run
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e SECRET_KEY=your-secret-key \
  --name endcom-net \
  endcom-net-ai
```

### Option 3: Railway

1. Connect your GitHub repository to Railway
2. Railway will auto-detect the Dockerfile
3. Set environment variables in Railway dashboard
4. Deploy!

### Option 4: Heroku

1. **Create Procfile:**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. **Deploy:**
```bash
heroku create your-app-name
git push heroku main
```

3. **Set environment variables:**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-database-url
```

### Option 5: AWS/Google Cloud/Azure

Use the Docker image or deploy as a containerized application.

**AWS Elastic Beanstalk:**
```bash
eb init -p docker endcom-net-ai
eb create endcom-net-env
eb deploy
```

**Google Cloud Run:**
```bash
gcloud run deploy endcom-net \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 6: VPS (Digital Ocean, Linode, etc.)

1. **SSH into your server:**
```bash
ssh user@your-server-ip
```

2. **Clone repository:**
```bash
git clone https://github.com/yourusername/Tammy.git
cd Tammy
```

3. **Run startup script:**
```bash
./start.sh
```

4. **Set up as a service (systemd):**
```bash
sudo nano /etc/systemd/system/endcom-net.service
```

Add:
```ini
[Unit]
Description=ENDCOM.NET AI Assistant
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Tammy
Environment="PATH=/path/to/Tammy/venv/bin"
ExecStart=/path/to/Tammy/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Start service:**
```bash
sudo systemctl enable endcom-net
sudo systemctl start endcom-net
```

6. **Set up Nginx reverse proxy:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/Tammy/static;
    }
}
```

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./tammy.db  # For local/development
# DATABASE_URL=postgresql://user:pass@host/db  # For production

# Security
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32

# API Settings
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000
```

### Optional Environment Variables

```bash
# OpenAI Integration
OPENAI_API_KEY=sk-...

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# Twilio (SMS/Calls)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
```

## 🗄️ Database Options

### Development (SQLite)
```bash
DATABASE_URL=sqlite+aiosqlite:///./tammy.db
```

### Production (PostgreSQL)

**Supabase:**
```bash
DATABASE_URL=postgresql://user:pass@db.xxxx.supabase.co:5432/postgres
```

**Neon:**
```bash
DATABASE_URL=postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/neondb
```

**Railway:**
```bash
DATABASE_URL=postgresql://postgres:pass@containers-us-west-xx.railway.app:7432/railway
```

## 🌐 Domain Setup

### With Vercel
1. Go to your project settings
2. Add your custom domain
3. Update DNS records as instructed

### With Other Providers
1. Point your domain's A record to your server IP
2. Set up SSL with Let's Encrypt:
```bash
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring & Logging

### Application Logs
```bash
# View logs
tail -f logs/tammy.log

# With Docker
docker logs -f endcom-net-assistant

# With systemd
sudo journalctl -u endcom-net -f
```

### Health Check Endpoint
```bash
curl https://your-domain.com/health
```

### Monitoring Services
- **Uptime**: UptimeRobot, Pingdom
- **APM**: New Relic, Datadog, Sentry
- **Logs**: Papertrail, Loggly

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change SECRET_KEY to a strong random value
- [ ] Set DEBUG=False
- [ ] Use HTTPS (SSL certificate)
- [ ] Use a production database (PostgreSQL, not SQLite)
- [ ] Set up rate limiting
- [ ] Enable CORS only for trusted origins
- [ ] Set up backup strategy
- [ ] Configure firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable authentication if needed

## 🔄 CI/CD Setup

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID}}
        vercel-project-id: ${{ secrets.PROJECT_ID}}
```

## 🐛 Troubleshooting

### Vercel Deployment Issues

**Problem:** 404 errors
**Solution:** Check `vercel.json` configuration and ensure `api/index.py` exists

**Problem:** Database connection fails
**Solution:** Use external database, Vercel doesn't persist SQLite

**Problem:** Build fails
**Solution:** Check `runtime.txt` has correct Python version

### Docker Issues

**Problem:** Container exits immediately
**Solution:** Check logs with `docker logs endcom-net-assistant`

**Problem:** Can't connect to database
**Solution:** Ensure database service is running and connection string is correct

### General Issues

**Problem:** Static files not loading
**Solution:** Check that `static/` and `public/` directories exist

**Problem:** CORS errors
**Solution:** Update CORS configuration in `app/main.py`

## 📞 Support

- Documentation: See README.md
- API Docs: Visit `/docs` on your deployment
- Issues: GitHub Issues

## 🎯 Performance Tips

1. **Use a production ASGI server:**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Enable caching:**
   - Use Redis for session storage
   - Cache API responses

3. **Database optimization:**
   - Use connection pooling
   - Add database indexes
   - Use read replicas for scaling

4. **CDN for static files:**
   - Cloudflare
   - AWS CloudFront
   - Vercel (automatic)

Happy Deploying! 🚀
