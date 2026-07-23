# 🔐 SSL/TLS Setup Guide for SkillSphere

## Overview
This guide covers setting up SSL/TLS certificates for production deployment using Let's Encrypt and Certbot.

---

## Method 1: Using Let's Encrypt + Certbot (Recommended)

### Prerequisites
- Domain name configured and pointing to your server
- Server accessible via port 80 and 443
- Ubuntu/Debian or RHEL/CentOS

### Step 1: Install Certbot

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# RHEL/CentOS
sudo yum install certbot python3-certbot-nginx
```

### Step 2: Obtain SSL Certificate

```bash
# Standalone mode (simpler for initial setup)
sudo certbot certonly --standalone -d skillsphere.com -d www.skillsphere.com

# Or with Nginx plugin (if Nginx is already running)
sudo certbot --nginx -d skillsphere.com -d www.skillsphere.com
```

### Step 3: Verify Certificate Installation

```bash
sudo certbot certificates
```

Output should show your certificates in `/etc/letsencrypt/live/skillsphere.com/`

### Step 4: Update Nginx Configuration

```nginx
ssl_certificate /etc/letsencrypt/live/skillsphere.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/skillsphere.com/privkey.pem;
```

### Step 5: Auto-Renewal Setup

```bash
# Test renewal
sudo certbot renew --dry-run

# Enable auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check renewal status
sudo systemctl status certbot.timer
```

---

## Method 2: Using Self-Signed Certificates (Development Only)

⚠️ **NOT recommended for production** - only for testing!

```bash
# Generate self-signed certificate (valid for 365 days)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/key.pem \
  -out /etc/nginx/ssl/cert.pem

# Fill in certificate details:
# Country Name (2 letter code): US
# State or Province Name: California
# Locality Name: San Francisco
# Organization Name: SkillSphere
# Organizational Unit: Engineering
# Common Name: skillsphere.com
# Email Address: admin@skillsphere.com

# Verify certificate
openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout
```

---

## Method 3: Using AWS Certificate Manager (for AWS deployments)

### Step 1: Create Certificate in ACM

```bash
aws acm request-certificate \
  --domain-name skillsphere.com \
  --subject-alternative-names www.skillsphere.com \
  --validation-method DNS \
  --region us-east-1
```

### Step 2: Validate Domain

- Follow email validation or add DNS CNAME records
- Certificate status will change to "Issued"

### Step 3: Use with AWS Services

- ALB (Application Load Balancer)
- CloudFront
- API Gateway

---

## Nginx Configuration with SSL

### Complete HTTPS Setup

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name skillsphere.com www.skillsphere.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name skillsphere.com www.skillsphere.com;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/skillsphere.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/skillsphere.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS Header
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Your location blocks here...
}
```

---

## Docker Setup with SSL

### Updated docker-compose.yml

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/nginx/ssl:ro  # Mount Let's Encrypt certs
      - ./staticfiles:/app/staticfiles:ro
      - ./media:/app/media:ro
    environment:
      - TZ=UTC
    depends_on:
      - django
    networks:
      - skillsphere_network

  django:
    # ... existing configuration ...
    environment:
      - SECURE_SSL_REDIRECT=True
      - SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

---

## Monitoring & Maintenance

### Check Certificate Expiration

```bash
# Check expiration date
echo | openssl s_client -servername skillsphere.com -connect skillsphere.com:443 2>/dev/null | \
  openssl x509 -noout -dates

# Days until expiration
echo | openssl s_client -servername skillsphere.com -connect skillsphere.com:443 2>/dev/null | \
  openssl x509 -noout -dates | grep notAfter | \
  awk -F= '{print $2}' | \
  xargs date +%s -d | \
  awk '{print int(($1 - $(date +%s)) / 86400)}'
```

### Test SSL Configuration

```bash
# Using ssllabs.com
curl -s https://www.ssllabs.com/ssltest/analyze.html?d=skillsphere.com

# Using testssl.sh
./testssl.sh https://skillsphere.com
```

### View Certificate Details

```bash
# Check installed certificate
sudo certbot certificates

# Renew specific certificate
sudo certbot renew --cert-name skillsphere.com

# Force renewal
sudo certbot renew --force-renewal
```

---

## Troubleshooting

### Certificate Not Found

```bash
# Check if directory exists
ls -la /etc/letsencrypt/live/

# Verify symlinks
ls -la /etc/letsencrypt/live/skillsphere.com/
```

### Renewal Failing

```bash
# Test renewal
sudo certbot renew --verbose

# Check certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Manually renew
sudo certbot certonly --force-renewal -d skillsphere.com
```

### Nginx Not Reading Certificate

```bash
# Test nginx configuration
sudo nginx -t

# Check nginx error log
sudo tail -f /var/log/nginx/error.log

# Verify certificate permissions
sudo chown root:root /etc/letsencrypt/live/skillsphere.com/*
sudo chmod 644 /etc/letsencrypt/live/skillsphere.com/fullchain.pem
sudo chmod 600 /etc/letsencrypt/live/skillsphere.com/privkey.pem
```

---

## Security Best Practices

### 1. Keep Certificates Updated
- Enable auto-renewal ✅
- Monitor expiration dates
- Test renewal regularly

### 2. Use Strong Ciphers
```nginx
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:...
```

### 3. Enable HSTS
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

### 4. Implement CAA Records
```dns
CAA 0 issue "letsencrypt.org"
CAA 0 issuewild "letsencrypt.org"
```

### 5. Regular Security Audits
- SSL Labs: https://www.ssllabs.com/ssltest/
- Mozilla SSL Configuration: https://ssl-config.mozilla.org/

---

## References

- Let's Encrypt: https://letsencrypt.org
- Certbot Documentation: https://certbot.eff.org
- Mozilla SSL Guidelines: https://wiki.mozilla.org/Security/Server_Side_TLS
- Nginx SSL: https://nginx.org/en/docs/http/ngx_http_ssl_module.html
