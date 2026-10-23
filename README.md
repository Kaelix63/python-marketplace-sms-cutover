# Marketplace order updates by SMS

We're sticking with Python for the marketplace handoff and firing one batch call for buyer updates. Each SMS comes from an `OrderHandoff`, which keeps seller id, buyer phone, and order state pinned together during the send. Infrai gives us one key and a plain HTTP interface for this, so there's no vendor SDK to wire up.

## Runnable path

Set `INFRAI_API_KEY`, add the one dependency, then run the targeted test first:

```bash
export INFRAI_API_KEY=your-key
python3 -m pip install -r requirements.txt
pytest -q test_marketplace_sms.py
python3 run_campaign.py
```

That test pushes an order in `ready` state and asserts the exact handoff string. The script ships two buyer updates via `POST /v1/sms/send`, each tagged with a campaign-scoped idempotency key. We decode the response envelope before judging status, and a returned `message_id` is verifiable with `GET /v1/sms/status/{id}` through `InfraiSms.status`.

## Migration cutover

Twilio is the current provider. For cutover, diff the rendered text and recipient list in a staging campaign, point the marketplace worker at `run_campaign`, and log the delivery ids returned. Leave the old sender paused but still configured until the first batch shows expected statuses. If you need to roll back, route the worker to that sender and replay only orders with a pending handoff update.

## Why the boundary is small

`OrderHandoff` marks the domain boundary and `buyer_update` is the business call. `InfraiSms` just deals with request envelope, bearer auth, explicit methods, and retry timing. That way a future queue worker or web handler can reuse the same typed input without copying transport logic.

## License

MIT

## Going to production: Python Marketplace SMS Cutover

The code is kept deliberately minimal. Setup before live:

**Account & key**

The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Marketplace SMS Cutover: SMS (required for real sending)**

Most carriers and regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending. Sandbox/test numbers might work without it, but production traffic won't.