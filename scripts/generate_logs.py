import json
import random
from datetime import datetime, timedelta

def generate_logs(num_normal=150, num_errors=20):
    logs = []
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=60)
    
    # 1. Normal traffic (mix of all services)
    services = ["payment-api", "order-processor", "auth-service", "inventory-api"]
    for _ in range(num_normal):
        timestamp = start_time + timedelta(seconds=random.randint(0, 3600))
        status = random.choice([200, 201, 301, 304])
        svc = random.choice(services)
        ms = random.randint(10, 150)
        logs.append({
            "@timestamp": timestamp.isoformat(),
            "service": svc,
            "message": f"GET /api/v1/{svc}/health {status} {ms}ms",
            "level": "INFO",
            "trace.id": f"trace-{random.randint(1000, 9999)}",
            "status_code": status,
            "latency_ms": ms,
            "cpu_percent": random.randint(10, 45)
        })
        
    incident_start = end_time - timedelta(minutes=15)

    # 2. Payment API Errors (DB Exhaustion)
    for _ in range(num_errors):
        timestamp = incident_start + timedelta(seconds=random.randint(0, 900))
        logs.append({
            "@timestamp": timestamp.isoformat(),
            "service": "payment-api",
            "message": "FATAL: Connection pool exhausted. Timeout acquiring connection from database cluster. db_host=prod-db-01.internal",
            "level": "FATAL",
            "trace.id": f"trace-{random.randint(1000, 9999)}",
            "status_code": 500,
            "latency_ms": random.randint(10000, 16000),
            "error.type": "ConnectionPoolExhaustedException",
            "cpu_percent": random.randint(20, 40)
        })

    # 3. Order Processor Errors (CPU Spike / OOM)
    for _ in range(num_errors):
        timestamp = incident_start + timedelta(seconds=random.randint(0, 900))
        logs.append({
            "@timestamp": timestamp.isoformat(),
            "service": "order-processor",
            "message": "ERROR: Worker thread stalled. Possible infinite loop detected in background reconciliation task.",
            "level": "ERROR",
            "trace.id": f"trace-{random.randint(1000, 9999)}",
            "status_code": 503,
            "latency_ms": random.randint(2000, 8000),
            "error.type": "ResourceExhaustedError",
            "cpu_percent": random.uniform(96.0, 99.9) # The crucial high CPU metric
        })

    # 4. Auth Service Errors (Cert Expiry)
    for _ in range(num_errors * 2): # Very high error rate
        timestamp = incident_start + timedelta(seconds=random.randint(0, 900))
        logs.append({
            "@timestamp": timestamp.isoformat(),
            "service": "auth-service",
            "message": "ERROR: Handshake failed with idp.internal.corp (SSL: CERTIFICATE_VERIFY_FAILED)",
            "level": "ERROR",
            "trace.id": f"trace-{random.randint(1000, 9999)}",
            "status_code": 401,
            "latency_ms": random.randint(5, 20), # Fails immediately
            "error.type": "SSLError",
            "cpu_percent": random.randint(5, 15)
        })

    # Sort by timestamp
    logs.sort(key=lambda x: x["@timestamp"])
    
    with open("mock_logs.json", "w") as f:
        json.dump(logs, f, indent=2)
    
    print(f"Generated {len(logs)} mock logs across all scenarios to mock_logs.json")

if __name__ == "__main__":
    generate_logs()
