"""
RegLoop AI - Production Deployment & Operations Guide

Guidelines for deploying the obligation extraction system to production.
"""

# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

DEPLOYMENT_CHECKLIST = """
PRE-DEPLOYMENT
==============
□ Run full test suite: python tests_examples.py
□ Verify database migration: python -c "from database.db import init_db; init_db()"
□ Check requirements.txt is complete
□ Review security configuration
□ Set environment variables
□ Configure logging level
□ Test with sample documents

PRODUCTION DEPLOYMENT
=====================
□ Use production ASGI server (Uvicorn, Gunicorn)
□ Configure reverse proxy (nginx)
□ Set up SSL/TLS certificates
□ Configure database backup
□ Set up monitoring & alerts
□ Configure rate limiting
□ Set up log aggregation
□ Configure health checks

POST-DEPLOYMENT
===============
□ Verify API health: GET /
□ Test upload endpoint: POST /upload
□ Test extraction: POST /documents/{id}/analyze
□ Monitor error logs
□ Track performance metrics
□ Set up alerting

ONGOING OPERATIONS
==================
□ Daily backup of SQLite database
□ Monitor API response times
□ Track extraction accuracy
□ Review error logs weekly
□ Update keyword lists as needed
□ Performance tuning based on usage
□ Security patches
"""

# ============================================================================
# PRODUCTION DEPLOYMENT SCRIPT
# ============================================================================

"""
Deploy to Production (Example for Linux)
=========================================

1. Clone repository
   git clone <your-repo> /opt/regloop-ai
   cd /opt/regloop-ai/backend

2. Create Python virtual environment
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt
   pip install gunicorn  # For production ASGI server

4. Initialize database
   python -c "from database.db import init_db; init_db()"

5. Create systemd service file
   Create: /etc/systemd/system/regloop-ai.service
   
6. Start service
   systemctl start regloop-ai
   systemctl enable regloop-ai

7. Configure nginx reverse proxy
   - Forward traffic to localhost:8000
   - Add SSL certificates
   - Enable compression

8. Monitor
   systemctl status regloop-ai
   journalctl -u regloop-ai -f
"""

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

ENVIRONMENT_VARIABLES = """
# Production Environment Variables

# Database
DATABASE_URL=sqlite:///./regloop.db  # Or postgresql://user:pass@host/db

# Logging
LOG_LEVEL=INFO  # INFO, WARNING, ERROR, DEBUG
LOG_FILE=/var/log/regloop-ai.log

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
CORS_ORIGINS=["https://yourfrontend.com"]
SECRET_KEY=your-secret-key-here

# Feature Flags
ENABLE_EXTRACTION=true
MAX_UPLOAD_SIZE_MB=50
MAX_OBLIGATIONS_PER_RUN=100
"""

# ============================================================================
# MONITORING & OBSERVABILITY
# ============================================================================

MONITORING_SETUP = """
Monitoring Setup
================

1. Application Metrics
   - API response time (target: < 1s)
   - Document upload success rate
   - Obligation extraction success rate
   - Database query performance
   - Error rate (target: < 0.1%)

2. System Metrics
   - CPU usage
   - Memory usage (target: < 500MB)
   - Disk space (SQLite database growth)
   - Network I/O

3. Logging
   - Application logs to syslog
   - Error logs to separate file
   - Access logs from reverse proxy
   - Log rotation daily

4. Alerting
   - Alert on extraction failures
   - Alert on API errors
   - Alert on database growth
   - Alert on performance degradation
   - Alert on out-of-disk errors

5. Tools
   - Prometheus for metrics
   - Grafana for dashboards
   - ELK stack for logging
   - Alertmanager for alerts
"""

# ============================================================================
# BACKUP & RECOVERY
# ============================================================================

BACKUP_STRATEGY = """
Backup & Recovery Strategy
===========================

1. Database Backups
   - Schedule: Daily at 2 AM
   - Retention: 30 days
   - Location: Separate storage
   
   Script:
   #!/bin/bash
   BACKUP_DIR="/var/backups/regloop"
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   sqlite3 /opt/regloop-ai/backend/regloop.db \
     ".backup '/var/backups/regloop/backup_$TIMESTAMP.db'"
   
2. Incremental Backups
   - Use rsync to copy database
   - Compress older backups
   
3. Test Restores
   - Monthly restore test
   - Document recovery procedure
   - Time Recovery Objective: 1 hour
   - Recovery Point Objective: 1 day

4. Disaster Recovery
   - Keep backup on separate server
   - Document recovery procedure
   - Test recovery quarterly
"""

# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================

PERFORMANCE_TUNING = """
Performance Optimization
========================

1. Database Optimization
   - Enable WAL (Write-Ahead Logging) for SQLite
   - Create indexes on frequently queried fields
   - Periodic VACUUM and ANALYZE
   - Connection pooling

   In database/db.py:
   engine = create_engine(
       DATABASE_URL,
       connect_args={"check_same_thread": False},
       pool_size=20,  # Connection pool
       max_overflow=40,  # Overflow connections
       echo=False,  # Disable query logging in production
       execution_options={"sqlite_synchronous": 1}  # Faster SQLite
   )

2. API Optimization
   - Enable gzip compression
   - Cache GET responses
   - Implement request throttling
   - Use connection pooling

3. Extraction Optimization
   - Batch obligations when saving
   - Limit document size
   - Add extraction timeouts
   - Cache extractor instance (singleton)

4. Monitoring
   - Track slow queries
   - Track slow API endpoints
   - Profile extraction performance
   - Monitor database size growth

5. Scaling
   - SQLite works fine for 100k+ obligations
   - For larger scale: migrate to PostgreSQL
   - Use read replicas for analytics
   - Implement caching layer (Redis)
"""

# ============================================================================
# SECURITY HARDENING
# ============================================================================

SECURITY_CHECKLIST = """
Security Hardening Checklist
=============================

1. API Security
   □ Enable CORS properly (only trusted domains)
   □ Implement rate limiting
   □ Add request validation
   □ Use HTTPS only (SSL/TLS)
   □ Implement authentication/authorization
   □ Add API key validation
   □ Sanitize file uploads
   □ Implement CSRF protection

2. Database Security
   □ Use strong database credentials
   □ Restrict database access
   □ Enable encryption at rest
   □ Encrypt backups
   □ Regular security patches
   □ Audit database access

3. File Security
   □ Validate uploaded file types
   □ Scan uploads for malware
   □ Store uploads outside web root
   □ Implement file access controls
   □ Set appropriate file permissions

4. Infrastructure
   □ Firewall rules
   □ SSH key authentication (no passwords)
   □ Regular security patching
   □ Disable unnecessary services
   □ Monitor system logs
   □ Enable SELinux/AppArmor

5. Application
   □ Review source code security
   □ Dependency vulnerability scanning
   □ Secure configuration management
   □ Error handling (no stack traces)
   □ Secure logging (no sensitive data)

Example Security Headers (nginx):
add_header Strict-Transport-Security "max-age=31536000" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer" always;
"""

# ============================================================================
# SCALING STRATEGY
# ============================================================================

SCALING_GUIDE = """
Scaling Strategy
================

Phase 1: Single Server (MVP)
- Single FastAPI instance
- SQLite database (local file)
- No replication
- Good for: 0-10k obligations, < 100 uploads/day

Phase 2: Dedicated Database Server
- FastAPI on web server
- SQLite → PostgreSQL
- Database on separate server
- Good for: 10k-100k obligations, < 1000 uploads/day

Phase 3: Multiple API Instances
- Load balancer (nginx)
- Multiple FastAPI instances
- Shared PostgreSQL database
- Redis for caching
- Good for: 100k-1M obligations, > 10k uploads/day

Phase 4: Distributed System
- Kubernetes orchestration
- Multiple API replicas
- PostgreSQL with replication
- Elasticsearch for logging
- Prometheus for monitoring
- Horizontal scaling by demand

Migration from SQLite to PostgreSQL:
1. Export data: python -c "from database.db import export_to_psql; export_to_psql()"
2. Update DATABASE_URL in environment
3. Migrate schema
4. Update connection string
5. Test thoroughly
6. Switch traffic
"""

# ============================================================================
# INCIDENT RESPONSE
# ============================================================================

INCIDENT_RESPONSE_PLAN = """
Incident Response Plan
======================

1. High API Response Time
   - Check CPU/memory usage
   - Check database query performance
   - Check if extraction is running long
   - Restart API if necessary
   - Scale horizontally if needed

2. High Error Rate
   - Check application logs
   - Check database connection
   - Check disk space
   - Check network connectivity
   - Rollback recent changes

3. Database Corruption
   - Restore from latest backup
   - Check backup integrity
   - Verify data after restore
   - Run consistency checks
   - Update monitoring

4. Security Incident
   - Isolate affected systems
   - Review access logs
   - Check for unauthorized access
   - Reset credentials
   - Apply security patches

5. Document Storage Full
   - Clean up old uploads
   - Archive to external storage
   - Add disk space
   - Configure cleanup script

6. API Down
   - Check service status
   - Review logs for errors
   - Check system resources
   - Restart service
   - Failover to backup if available

Incident Documentation:
- What happened?
- When did it happen?
- Root cause?
- How was it resolved?
- What can be improved?
- Update runbooks
"""

# ============================================================================
# OPERATIONAL RUNBOOKS
# ============================================================================

RUNBOOKS = """
Operational Runbooks
====================

1. Restart API Service
   systemctl restart regloop-ai
   systemctl status regloop-ai
   Check logs: journalctl -u regloop-ai -f

2. Database Backup
   sqlite3 /opt/regloop/regloop.db ".backup '/backups/backup_$(date +%s).db'"
   Verify backup size and integrity

3. Emergency Rollback
   git revert <commit>
   Re-run tests
   Deploy
   Monitor

4. Scale Up
   Update API_WORKERS environment variable
   Restart service
   Monitor metrics

5. Database Maintenance
   sqlite3 regloop.db "VACUUM;"
   sqlite3 regloop.db "ANALYZE;"
   Check database size

6. Clear Old Documents
   DELETE FROM documents WHERE uploaded_at < date('now', '-90 days');
   DELETE FROM uploads WHERE (filename) NOT IN (SELECT filename FROM documents);

7. Extract Performance Report
   SELECT category, COUNT(*) as count, AVG(priority) as avg_priority
   FROM obligations
   GROUP BY category;

8. System Health Check
   Check API response: curl http://localhost:8000/
   Check database: sqlite3 regloop.db "SELECT COUNT(*) FROM obligations;"
   Check logs for errors: grep ERROR /var/log/regloop-ai.log | tail -20
"""

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_SETUP = """
Logging Configuration
====================

Recommended Log Format:
%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s

Log Levels:
DEBUG   - Detailed diagnostic information
INFO    - General informational messages
WARNING - Warning messages for potential issues
ERROR   - Error messages for failures
CRITICAL - Critical errors requiring immediate attention

Production Settings:
- Log Level: INFO (DEBUG only for troubleshooting)
- Log Rotation: Daily or when size > 100MB
- Retention: 30 days
- Format: JSON for easy parsing
- Destinations: File + syslog

Log Management:
- Aggregate logs to central location
- Set up alerts for ERROR/CRITICAL
- Periodic log review
- Secure log storage (encrypted)

Example Structured Logging:
{
    "timestamp": "2024-06-09T10:30:45Z",
    "level": "INFO",
    "service": "regloop-ai",
    "message": "Obligation extraction completed",
    "document_id": 1,
    "obligations_count": 15,
    "duration_ms": 523,
    "user_id": "user123"
}
"""

# ============================================================================
# COST OPTIMIZATION
# ============================================================================

COST_OPTIMIZATION = """
Cost Optimization (Zero API Costs!)
===================================

Your obligation extraction system costs:
✓ Extraction: $0 (local processing)
✓ APIs: $0 (no paid services)
✓ Licenses: $0 (open source)
✓ Per-document fee: $0

Infrastructure Costs (typical):
- Small VM: $5-20/month
- Database storage: $0-10/month (SQLite local)
- Backup storage: $1-5/month
- Total: $6-35/month

Compared to:
- Claude API: $0.003 per 1K input tokens (~$30/month for same volume)
- OpenAI API: $0.005 per 1K tokens (~$50/month)
- Azure AI: $1-10 per 1K requests (~$100+/month)

Annual Savings (vs. paid APIs): $200-600+

Cost Reduction Tips:
1. Use SQLite (local database, no server cost)
2. Single server for MVP
3. Shared infrastructure
4. Minimal logging in production
5. Cloud storage for backups (cheap)
6. CDN not needed (internal use)
"""

# ============================================================================
# HEALTH CHECKS & MONITORING
# ============================================================================

HEALTH_CHECK_IMPLEMENTATION = """
Health Checks & Monitoring
==========================

Add health check endpoint to main.py:

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        # Check extractor
        from services.obligation_extractor import get_extractor
        get_extractor()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": "connected",
            "extractor": "ready"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }, 500

Monitoring Script (cron job every 5 minutes):
#!/bin/bash
curl -f http://localhost:8000/health > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "$(date): Health check failed" >> /var/log/regloop-health.log
    # Send alert
    systemctl restart regloop-ai
fi

Performance Metrics:
- GET /metrics endpoint
- Track API latency
- Track extraction time
- Track database query time
- Track error rate
"""

# ============================================================================
# SUMMARY
# ============================================================================

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*70)
    print("DEPLOYMENT CHECKLIST")
    print("="*70)
    print(DEPLOYMENT_CHECKLIST)
    print("\n" + "="*70)
    print("PRODUCTION MONITORING")
    print("="*70)
    print(MONITORING_SETUP)
    print("\n" + "="*70)
    print("SECURITY HARDENING")
    print("="*70)
    print(SECURITY_CHECKLIST)
    print("\n✓ Review all sections before deploying to production")
