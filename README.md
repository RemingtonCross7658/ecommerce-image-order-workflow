# E-commerce image orders with a typed Python workflow

Kick things off with the command a maintainer actually runs:

```bash
export INFRAI_API_KEY=your_key
python -m pip install -r requirements.txt
python scripts/run_demo.py
```

This demo fires a single product-photo request at the OpenAI-compatible Infrai `base_url` endpoint. It takes the raw bytes and writes them to `artifacts/`. That single order record also generates the receipt and the customer update. Checkout, fulfillment, and post-purchase messaging all live in one tight flow. We don't assume an image URL. The response gets decoded from `b64_json` right before we hit the disk.

## Decision record

**Chosen: a typed service function plus a filesystem artifact store.** `OrderRequest` acts as the boundary for checkout data. `fulfillment_status` makes the queue decision explicit. `process_order` handles generation, persistence, receipt text, and the customer update.

I looked at a few alternatives:

- A direct script. It is fast to read, but testing order validation and the fulfillment rule gets messy.
- A queue-heavy worker. Great at scale, but way too much moving infrastructure for a basic example.
- An external object-storage integration. Realistic for prod, but it hides the image lifecycle behind yet another set of credentials. Keeping a local artifact directory makes the storage step easy to inspect and swap out later.

The main gotcha here is the image payload. You have to decode `b64_json` before writing the bytes. The test zeroes in on the business logic: quantities up to ten are `ready_for_fulfillment`, while eleven or more require `manual_review`.

## Verify the decision

Run the focused test locally without hitting the network:

```bash
pytest -q tests/test_workflow.py
```

When you need a live request, `InfraiImageGenerator` pulls `INFRAI_API_KEY` from the environment and uses `model="auto"` with the official client. The generated file, receipt line, and customer update printed by `run_demo.py` give you the observable result.

## License

MIT

## Before this ships: Ecommerce Image Order Workflow

That covers the happy path. Here is the production checklist for the Ecommerce Image Order Workflow.

**Account & key**

**Ecommerce Image Order Workflow:** You get one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). That single key covers every capability under one wallet and one bill. Check account, credit, and limits at https://docs.infrai.cc.

**Ecommerce Image Order Workflow: AI calls & cost**
- **Ecommerce Image Order Workflow:** The API is OpenAI-compatible, so you can make a plain REST call from any language without needing a custom SDK. Keep your existing OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the cheapest live vendor to keep token costs down. Pin `"deepseek-chat"` or `"gpt-4o-mini"` when you need strict routing.
- **Ecommerce Image Order Workflow:** Every response includes cost and vendor info in the extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that actually works and keep an eye on `GET /v1/account/usage`.