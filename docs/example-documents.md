# Example Documents — Templates with Content

Real examples of how documents should look after creation. Use these as reference when reviewing documents Claude Code creates.

---

## Example 1: ADR (Architectural Decision Record)

**File:** `Projects/MyProject/Arquitectura/ADR-Caching-Strategy.md`

```yaml
---
title: "Decision: In-memory caching with Redis vs application-level"
project: myproject
type: decision
status: active
tags: [caching, performance, redis, architecture]
related: ["[[Infraestructura/Deployment-Strategy]]", "[[Documentación-Técnica/Performance-Baselines]]"]
created: 2024-06-15
updated: 2024-06-15
---

## Context

The application has seen performance degradation during peak hours. Response times for frequently accessed data (user profiles, product catalogs) increased from 50ms to 200-500ms.

Current architecture queries the database for every request. No caching layer exists.

We need to reduce load on the database and improve response times before the next product launch (3 weeks).

## Alternatives Evaluated

**Option A: Application-level caching (in-memory)**
- Pros: No external dependencies, simple to implement, fast
- Cons: Can't share cache across multiple server instances, memory usage grows unbounded, requires restart to clear
- Estimated effort: 1-2 days
- Risk: Cache invalidation problems in distributed environment

**Option B: Redis (external cache layer)**
- Pros: Distributed, scales easily, proven, rich data types, good for team familiarity
- Cons: Additional infrastructure, learning curve, latency vs in-memory, cost (~$50-100/month)
- Estimated effort: 3-4 days (including setup + monitoring)
- Risk: Redis becomes bottleneck if not sized correctly

**Option C: CDN + edge caching (Cloudflare, etc.)**
- Pros: Geographic distribution, handles traffic spikes
- Cons: Only works for read-only data, not suitable for personalized content, different vendor
- Estimated effort: 2-3 days
- Risk: Cache invalidation across global network

## Decision

**Implement Redis as the primary caching layer.**

Reasoning:
1. Application will grow to multiple servers (horizontal scaling planned for Q3). Redis enables cache sharing.
2. Team has existing Redis experience from previous projects.
3. Performance gains (50ms vs 200-500ms) justify the complexity.
4. Cost is negligible vs customer impact of slow load times.

## Consequences

- ✅ Response times improve to <100ms for cached queries (validated: previous benchmarks)
- ✅ Scales naturally with additional servers
- ✅ Team can leverage existing Redis knowledge
- ⚠️ Need to implement cache invalidation strategy (potential bugs)
- ⚠️ Additional infrastructure to monitor and maintain
- ⚠️ Could use Redis for sessions too (not required now, but option remains open)

## Implementation Notes

See [[Infraestructura/Redis-Deployment-Guide]] for setup instructions.
Cache invalidation strategy documented in [[Arquitectura/Cache-Invalidation-Strategy]].

## Review Date

Revisit if:
- Redis becomes a bottleneck (monitor Redis memory/CPU monthly)
- Application scales beyond 5 servers (evaluate consistency guarantees)
- Response times still >150ms after implementation
```

---

## Example 2: Problem Document

**File:** `Projects/MyProject/Logs-Técnicos/Database-Connection-Pool-Exhaustion.md`

> **Note:** `Logs-Técnicos/` is a custom folder name used in this example. Use whichever name fits your domain (e.g., `Problemas/`, `Problems/`, `Incidents/`).

```yaml
---
title: "Problem: Database connection pool exhaustion under load"
project: myproject
type: problem
status: active
tags: [postgresql, connection-pooling, pgbouncer, database, performance]
related: ["[[Arquitectura/ADR-Caching-Strategy]]", "[[Runbooks/Database-Health-Check]]"]
created: 2024-05-10
updated: 2024-05-22
---

## Symptoms

- Intermittent "too many connections" errors appearing in logs after 2-3 hours of normal traffic
- HTTP 503 errors returned to clients (request timeout)
- Errors correlate with high-traffic periods (peak hours 9am-5pm)
- Symptoms disappear for 30 minutes after application restart
- Monitoring shows connection count climbing steadily, hitting the 100-connection limit of the database

```sql
SELECT count(*) FROM pg_stat_activity;
-- Returns: 100 (the limit)
```

## Root Cause Analysis

**Initial assumption:** Database query inefficiency
**Actual cause:** Connection pool not configured at application layer

Each application instance opened its own set of connections (5 per instance).
With 20+ instances in production (load balanced), this created:
- 20 instances × 5 connections = 100 connections used
- Zero headroom for additional queries
- When traffic spiked, new requests couldn't get connections

The application's connection library (Node.js `pg` module) doesn't share connections across instances — each instance is isolated.

Connection pool configuration was missing: `max: 10` per instance means each instance reserves 10 connections, but code wasn't using the pool efficiently.

**Root cause timeline:**
1. Initial deployment: 2 instances, 10 connections each = fine (headroom)
2. Load balancer added 5 more instances: 7 × 10 = 70 connections = approaching limit
3. Traffic scaling: 20 instances added for Q2 traffic = 200 connections needed, but DB limit is 100
4. Connection cleanup timeout (idle connections not being released) made the problem worse

## Solution Applied

Implemented **PgBouncer** as a connection pooling layer in transaction pooling mode.

**Architecture before:**
```
App Instance 1 → PostgreSQL (10 conns)
App Instance 2 → PostgreSQL (10 conns)
App Instance 3 → PostgreSQL (10 conns)
... (20 instances total = 200 connections, DB limit 100)
```

**Architecture after:**
```
App Instances (20) → PgBouncer (pool mode: transaction) → PostgreSQL (15 conns)
```

PgBouncer sits between the application and the database:
- Each app instance connects to PgBouncer on `localhost:6432` (internal-only)
- PgBouncer maintains a small pool (15 connections) to the actual database
- When an app query completes, the connection is returned to the pool immediately
- New apps can reuse those connections

**Configuration applied:**
```ini
[databases]
production = host=db.internal port=5432 dbname=prod_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 15
min_pool_size = 5
reserve_pool_size = 3
reserve_pool_timeout = 3
idle_in_transaction_session_timeout = 900000
```

**Deployment:**
- Ran PgBouncer in a dedicated container on each app host (co-located)
- Updated application connection string: `localhost:6432` instead of `db.internal:5432`
- Monitored during rollout on staging first (2024-05-18)
- Rolled to production (2024-05-22) with canary deployment

## Validation

**Before (2024-05-21 9am):**
- Peak hour connection count: 87/100 (no errors yet, but at risk)
- Response time p95: 185ms
- Memory on DB: 45GB

**After (2024-05-22 9am):**
- Peak hour connection count: 12/100 (headroom!)
- Response time p95: 45ms (4x improvement)
- Memory on DB: 42GB (slightly better)
- Zero "too many connections" errors in logs

## Status

✅ **Resolved in production**

Monitoring PgBouncer metrics:
- Connection pool utilization: 12/15 (healthy)
- Transaction time: avg 8ms (good)
- No rejected connections in 5 days

## Remaining Work

- [ ] Document connection pooling strategy in architecture guide
- [ ] Add PgBouncer health checks to monitoring dashboard
- [ ] Plan for PgBouncer scaling if application grows beyond 40 instances

## References

- [[Arquitectura/Database-Connection-Strategy]] — why this approach
- [[Runbooks/Database-Health-Check]] — monitoring procedure
- PgBouncer docs: https://www.pgbouncer.org/
```

---

## Example 3: Runbook

**File:** `Projects/MyProject/Runbooks/Incident-Response-Database-Unavailable.md`

```yaml
---
title: "Runbook: Resolve database connectivity failure"
project: myproject
type: runbook
status: active
tags: [postgresql, database, incident-response, emergency, production]
related: ["[[Logs-Técnicos/Database-Connection-Pool-Exhaustion]]"]
created: 2024-06-01
updated: 2024-06-10
---

## Purpose

Quick procedure to respond when the application can't connect to the database. 

Symptoms:
- 503 errors in application (database connection timeout)
- Logs show "connection refused" or "too many connections"
- Health check endpoint failing
- Customer-facing impact

**Time to resolution target:** 5-10 minutes (detection + fix)

## Prerequisites

- SSH access to database host
- SSH access to at least one application instance
- `psql` command-line tool installed on your machine
- PgBouncer running on app hosts (post-2024-05 deployment)

## Steps

### 1. Confirm the problem (1 minute)

```bash
# From any app instance
ssh app-01.prod.internal

# Try connecting to database directly
psql -h db.internal -U appuser -d production -c "SELECT 1;"
```

**Expected if working:** Returns `?column? 1`

**If error:** "connection refused" or "timeout" → database is down

**If error:** "too many connections" → connection pool exhausted (see Step 2)

### 2. Check connection pool status (2 minutes)

```bash
# Check PgBouncer (runs on localhost:6432)
psql -h localhost -p 6432 -U pgbouncer pgbouncer -c "SHOW CLIENTS;" | head -20

# Check actual database connections
psql -h db.internal -U postgres -d postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

**If count > 90** (near the 100 limit) → connection pool exhaustion is the problem

### 3. Diagnose: Database or connection pool?

```bash
# SSH to the database host directly
ssh db.prod.internal

# Is PostgreSQL running?
systemctl status postgresql-15

# Is PgBouncer running on the app hosts?
ssh app-01.prod.internal "systemctl status pgbouncer"
```

**If PostgreSQL is down:**
```bash
systemctl start postgresql-15
# Wait 30 seconds for startup
systemctl status postgresql-15
```

**If PgBouncer is down:**
```bash
ssh app-01.prod.internal "systemctl start pgbouncer"
ssh app-02.prod.internal "systemctl start pgbouncer"
# etc for all app instances
```

### 4. Force connection cleanup (if connections exhausted)

```bash
# SSH to database
ssh db.prod.internal

# Terminate idle connections (don't kill active queries)
psql -U postgres -d production << 'EOF'
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND query_start < now() - interval '5 minutes';
EOF

# Check connection count again
psql -U postgres -d production -c "SELECT count(*) FROM pg_stat_activity;"
```

**Expected:** Connection count drops to <30, now has headroom

### 5. Verify application recovery (1 minute)

```bash
# Check application health endpoint
curl -I https://api.yourapp.com/health

# Should return: 200 OK

# Check logs for new errors
ssh app-01.prod.internal "tail -50 /var/log/app/error.log" | grep -i connection
```

**Expected:** No new connection errors, health check returns 200

### 6. Monitoring check (ongoing)

Monitor for 5 minutes:
```bash
# Watch connection count in real-time
watch -n 1 'psql -h db.internal -U postgres -d postgres -c "SELECT count(*) FROM pg_stat_activity;" | tail -1'
```

**Expected:** Stays between 10-30 (not climbing)

**If climbing again:** Database load is high. Escalate to senior engineer.

## Verification

✅ Application health check returns 200
✅ No 503 errors in last 5 minutes
✅ Connection count stable (not climbing)
✅ Customers report service restored

## Rollback

This is a diagnosis/fix, not a deployment. No rollback needed. If the problem recurs, escalate.

## Escalation

If after Step 6 the problem returns:
1. Page on-call senior engineer
2. Provide: connection count, error logs, last 10 queries from `pg_stat_statements`
3. Consider database restart (coordinated with team)

## Related Documentation

- [[Logs-Técnicos/Database-Connection-Pool-Exhaustion]] — why this happens
- [[Runbooks/Database-Health-Check]] — monitoring procedure
- PgBouncer monitoring: `/var/log/pgbouncer/pgbouncer.log`
```

---

## What Good Documentation Looks Like

### ✅ Decision Document Should Have

- Clear **context** (why the decision was needed)
- **Alternatives** with trade-offs (not just "we chose X")
- **Consequences** (both positive and negative)
- **Related documents** (links to architecture, runbooks, etc.)
- Recent **dates** (created/updated, not 6 months old)

### ✅ Problem Document Should Have

- **Symptoms** (observable, reproducible)
- **Root cause** (why it happened, with evidence)
- **Solution applied** (exact steps taken)
- **Validation** (before/after metrics proving it's fixed)
- **References** (link to related decisions/runbooks)

### ✅ Runbook Should Have

- Clear **purpose** (what problem it solves)
- **Prerequisites** (what you need before starting)
- **Steps** (numbered, with commands and expected output)
- **Verification** (how to confirm it worked)
- **Rollback** (how to undo if something goes wrong)
- **Escalation** (when to ask for help)

---

## Using These Examples

1. **As templates** — Copy the structure for your own documents
2. **As reference** — Show them to Claude Code to establish quality expectations
3. **For comparison** — When reviewing documents Claude Code creates, compare to these

These examples show documents that have been through real incidents, decisions, and solutions. They have substance — not just templates.