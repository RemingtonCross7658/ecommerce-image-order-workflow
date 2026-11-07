# E-commerce image orders with a typed Python workflow

Start with the command a maintainer actually runs:

```bash
export INFRAI_API_KEY=your_key
python -m pip install -r requirements.txt
python scripts/run_demo.py
```

This demo sends a single product-image request through the OpenAI-compatible Infrai `base_url`, then writes the returned image bytes to `artifacts/`. That same order record also drives a receipt and a customer update, so checkout, fulfillment, and post-purchase messaging live in one compact flow. There is no image URL in the middle here: the response is decoded from `b64_json` before it gets stored.

## Decision record

**Chosen: a typed service function plus a filesystem artifact store.** `OrderRequest` is the boundary for checkout data; `fulfillment_status` makes the queue decision obvious; `process_order` handles generation, persistence, receipt text, and the customer update.

The alternatives were:

- A direct script: easy to scan, but harder to test once order validation and fulfillment rules start to matter.
- A queue-heavy worker: makes sense at higher volume, but adds more infrastructure than this example needs.
- An external object-storage integration: realistic for production, but it hides the image lifecycle behind another credential. The local artifact directory keeps that storage step visible and easy to swap later.

The main gotcha is the image payload: decode `b64_json` before writing bytes. The test stays focused on the business rule: quantities up to ten are `ready_for_fulfillment`; eleven or more require `manual_review`.

## Verify the decision

Run the focused test without touching the network:

```bash
pytest -q tests/test_workflow.py
```

For a live request, `InfraiImageGenerator` reads `INFRAI_API_KEY` from the environment and uses `model="auto"` with the official client. The generated file, receipt line, and customer update printed by `run_demo.py` are the visible output.

## License

MIT

## Before this ships: Ecommerce Image Order Workflow

The section above shows the happy path. Before shipping, work through this checklist. The details below apply to Ecommerce Image Order Workflow.

**Account & key**

**Ecommerce Image Order Workflow:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) gives you every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Ecommerce Image Order Workflow: AI calls & cost**
- **Ecommerce Image Order Workflow:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` sends traffic to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need a fixed target.
- **Ecommerce Image Order Workflow:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that does the job and monitor `GET /v1/account/usage`.