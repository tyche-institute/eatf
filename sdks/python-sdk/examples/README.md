# Aletheia SDK Examples

Complete examples demonstrating various features of the Aletheia AI Python SDK.

## Prerequisites

1. Install the SDK:
   ```bash
   pip install aletheia-ai
   # or for development:
   pip install -e ..
   ```

2. Start Aletheia backend:
   ```bash
   cd ../../backend
   ./mvnw spring-boot:run
   ```

3. Start Aletheia frontend (optional, for UI verification):
   ```bash
   cd ../../frontend
   npm run dev
   ```

4. Configure credentials (optional):
   ```bash
   export ALETHEIA_API_URL="http://localhost:8081"
   export ALETHEIA_EMAIL="admin@default.local"
   export ALETHEIA_PASSWORD="Admin123!"
   export ALETHEIA_ORGANIZATION="default"
   ```

## Examples

### Partner action flow (`partner_action_flow.py`)

Login → register agent → `PAYMENT_INTENT` action → approve. Run from `sdks/python-sdk/`:

```bash
pip install -e ..
export ALETHEIA_BASE_URL=http://localhost:8081
python examples/partner_action_flow.py
```

See also `bash ../../scripts/partner-smoke.sh http://localhost:8081` from repo root.

### 1. Basic Usage (`basic_usage.py`)

**What it demonstrates:**
- Authentication
- Agent registration
- Event logging with cryptographic signatures
- Evidence package download
- Querying audit events

**Run:**
```bash
python basic_usage.py
```

**Expected output:**
- New agent registered
- Decision logged with timestamp proof and signature
- Evidence package downloaded as `.aep` file

---

### 2. Async Client (`async_client.py`)

**What it demonstrates:**
- Async/await with AsyncAletheiaClient
- Concurrent agent registration
- Parallel event logging
- Concurrent evidence downloads

**Run:**
```bash
python async_client.py
```

**Performance benefits:**
- 3x faster than synchronous client for batch operations
- Ideal for high-throughput scenarios

---

### 3. Delegation Chains (`delegation_chains.py`)

**What it demonstrates:**
- Creating a chain via **`POST /api/v1/delegation-chains`** (Visual Builder `nodes` payload, built by the SDK)
- Policy / metadata stored on the primary node
- `verify_chain` / `get_chain` (implemented by listing chains — there is no GET-by-id route)
- Audit events using **real** `AuditEventType` values (`DELEGATION_CREATED`, `RESPONSE_GENERATED`, `HUMAN_REVIEW_APPROVED`)

**Run:**
```bash
python delegation_chains.py
```

**Use cases:**
- Multi-step AI workflows
- Agent orchestration
- Task delegation with governance

---

### 4. Compliance Reporting (`compliance_reporting.py`)

**What it demonstrates:**
- High-risk agents and audit logging with valid event types
- Tenant-wide status via **`GET /api/v1/agents/stats`** (through `client.compliance.get_compliance_status()`)
- Report generation via **`POST /api/v1/audit/compliance-report`** (`format="JSON"` returns the JSON body as bytes; other formats trigger download)
- ROI figures derived from the report summary (no dedicated ROI API)
- No server-side report catalog (`list_reports` is empty by design)

**Run:**
```bash
python compliance_reporting.py
```

**Output files:**
- `compliance-report-YYYYMMDD.pdf` — bytes from the audit download endpoint (MVP may be plain text)
- `compliance-report-YYYYMMDD.json` — serialized compliance-report API response

---

## Common Issues

### Authentication Error
```
AuthenticationError: Invalid credentials
```

**Solution:**
- Check email/password in code
- Verify backend is running (port 8081 for local `./mvnw spring-boot:run`; often 8080 in Docker)
- Use default credentials: `admin@default.local` / `Admin123!`

### Connection Refused
```
NetworkError: Connection refused
```

**Solution:**
- Start backend: `cd backend && ./mvnw spring-boot:run`
- Verify backend health: `curl http://localhost:8081/health`

### Module Not Found
```
ModuleNotFoundError: No module named 'aletheia'
```

**Solution:**
```bash
pip install -e ..
# or
cd .. && pip install -e .
```

## Next Steps

After running examples:

1. **View in UI:**
   - Agents: http://localhost:3000/agents
   - Audit log: http://localhost:3000/audit
   - Delegation chains: http://localhost:3000/delegation-chains/3d
   - Reports: http://localhost:3000/reports

2. **Explore API:**
   - Swagger UI: http://localhost:8081/swagger-ui.html

3. **Build your integration:**
   - Copy example code as starting point
   - Customize for your use case
   - Add error handling and logging

## Support

- Documentation: https://docs.aletheia.ai/sdk/python
- Issues: https://github.com/aletheia-ai/python-sdk/issues
- Discord: https://discord.gg/aletheia-ai
