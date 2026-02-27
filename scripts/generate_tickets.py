import json
from datetime import datetime, timedelta

def generate_tickets():
    now = datetime.now()
    tickets = [
         # --- Payment API (Connection Pool) ---
         {
            "ticket_id": "INC-4022",
            "title": "Payment API Outage - Connection Pool Exhausted",
            "created_at": (now - timedelta(days=90)).isoformat(),
            "status": "Resolved",
            "root_cause": "The payment-api service ran out of available connections to the PostgreSQL database cluster (prod-db-01.internal) during a high traffic spike.",
            "resolution": "Increased the database connection pool size in Kubernetes config from 50 to 200. Also restarted the payment-api pods to immediately clear the pending connection queues.",
            "services_affected": ["payment-api", "checkout-ui"],
            "tags": ["database", "timeout", "payment", "ConnectionPoolExhaustedException"]
        },
        {
            "ticket_id": "INC-3811",
            "title": "Database connection limits hit by payment service",
            "created_at": (now - timedelta(days=150)).isoformat(),
            "status": "Resolved",
            "root_cause": "Black Friday traffic surge caused the DB pool manager to reject new connections from the payment pods.",
            "resolution": "Temporarily scaled up read replicas and increased max connections on pgbouncer.",
            "services_affected": ["payment-api"],
            "tags": ["database", "ConnectionPoolExhaustedException"]
        },
        {
            "ticket_id": "INC-3509",
            "title": "Payments failing with 500 status code",
            "created_at": (now - timedelta(days=210)).isoformat(),
            "status": "Resolved",
            "root_cause": "A rogue background job consumed all DB connections, starving the main payment-api service (ConnectionPoolExhausted).",
            "resolution": "Moved background jobs to a separate DB user with a strict connection limit. Restarted payment-api.",
            "services_affected": ["payment-api", "background-worker"],
            "tags": ["database", "timeout", "ConnectionPoolExhaustedException"]
        },
        
        # --- CPU Spike (Retry Loop) ---
        {
            "ticket_id": "INC-4015",
            "title": "CPU Runaway in order-processor due to missing backoff",
            "created_at": (now - timedelta(days=45)).isoformat(),
            "status": "Resolved",
            "root_cause": "A recent deployment introduced an infinite retry loop in the order reconciliation worker. When the downstream inventory-api timed out, the worker retried without exponential backoff, causing CPU saturation and OOM kills.",
            "resolution": "Rollback to previous stable version. Deployed hotfix with resilient retry policy. Set strict CPU limits (500m) on order-processor deployment.",
            "services_affected": ["order-processor"],
            "tags": ["cpu", "OOM", "infinite loop", "retry", "CPU saturation OOM kill runaway loop"]
        },

        # --- Auth Service (TLS Cert Expiry) ---
        {
            "ticket_id": "INC-3104",
            "title": "Auth token validation failing globally (SSL Error)",
            "created_at": (now - timedelta(days=330)).isoformat(),
            "status": "Resolved",
            "root_cause": "The internal TLS certificate used by auth-service to communicate with the LDAP provider expired quietly. Token validation requests failed with SSL: CERTIFICATE_VERIFY_FAILED.",
            "resolution": "Manually rotated the TLS certificate via kubectl. Action Item: Implement cert-manager for automated rotation before expiry.",
            "services_affected": ["auth-service", "user-dashboard"],
            "tags": ["auth", "certificate", "TLS", "SSL: CERTIFICATE_VERIFY_FAILED", "expired"]
        },
        
        # --- Noise / Other ---
        {
            "ticket_id": "INC-3910",
            "title": "High latency on user profile image upload",
            "created_at": (now - timedelta(days=120)).isoformat(),
            "status": "Resolved",
            "root_cause": "S3 bucket networking misconfiguration causing slow uploads.",
            "resolution": "Fixed VPC endpoint routing for the S3 bucket.",
            "services_affected": ["user-service"],
            "tags": ["s3", "network", "latency"]
        }
    ]
    
    with open("mock_tickets.json", "w") as f:
        json.dump(tickets, f, indent=2)
        
    print(f"Generated {len(tickets)} mock tickets to mock_tickets.json")

if __name__ == "__main__":
    generate_tickets()
