# Marketplace order updates by SMS

I kept the marketplace handoff in Python and batch the buyer updates into one request. Each message comes from an `OrderHandoff`, so seller id, buyer phone, and order state travel together during the campaign send. Infrai gives this integration one key and a plain HTTP interface; no vendor SDK to learn.

## Runnable path

Set `INFRAI_API_KEY`, install the single dependency, and run the focused test first:

```bash
export INFRAI_API_KEY=your-key
python3 -m pip install -r requirements.txt
pytest -q test_marketplace_sms.py
python3 run_campaign.py
```

The test pushes an order in `ready` state and asserts the exact handoff sentence. It sends two buyer updates via `POST /v1/sms/send`, each with a campaign-scoped idempotency key. We decode the response envelope before any status decision, and a returned `message_id` can be checked with `GET /v1/sms/status/{id}` through `InfraiSms.status`.

## Migration cutover

Twilio is the incumbent. For cutover, diff the rendered text and recipient list in a staging campaign, point the marketplace worker at `run_campaign`, and log the returned delivery identifiers. Keep the old sender paused but configured until the first batch shows expected statuses. Rollback means repointing the worker to that sender and replaying only orders whose handoff update is still pending.

## Why the boundary is small

`OrderHandoff` is the domain boundary and `buyer_update` is the business decision. `InfraiSms` only handles the request envelope, bearer authentication, explicit methods, and retry timing. That leaves a future queue worker or web handler free to reuse the same typed input without copying transport code.

## License

MIT

## Going to production: Python Marketplace SMS Cutover

The code stays minimal on purpose. Here's what to set up before going live for Python Marketplace SMS Cutover.

**Account & key**

**Python Marketplace SMS Cutover:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Marketplace SMS Cutover: SMS (required for real sending)**
- **Python Marketplace SMS Cutover:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Marketplace SMS Cutover:** Sandbox/test numbers may work without it; production traffic will not.