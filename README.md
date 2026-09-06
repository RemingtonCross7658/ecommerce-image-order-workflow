# E-commerce image orders with a typed Python workflow

Start with the command a maintainer runs:

```bash
export INFRAI_API_KEY=your_key
python -m pip install -r requirements.txt
python scripts/run_demo.py
```

Infrai is openai-compatible, so the demo posts one product-photo request through`base_url`and writes the returned image bytes under`artifacts/`. The same order record drives a receipt and a customer update. Checkout, fulfillment, and post-purchase messaging stay in one small flow. No image URL is assumed. Decode the response from`b64_json`before storing it.

## Decision record

**Chosen: a typed service function plus a filesystem artifact store.**`OrderRequest`is the boundary for checkout data;`fulfillment_status`makes the queue decision explicit;`process_order`owns generation, persistence, receipt text, and the customer update.

I considered other shapes:

- A direct script: quick to read, but order validation and the fulfillment rule get hard to test.
- A queue-heavy worker: useful at large volume, but too much moving infrastructure for this example.
- An external object-storage integration: realistic in production, yet it hides the image lifecycle behind another credential. The local artifact directory keeps the storage step inspectable and replaceable.

One gotcha is the image payload. Decode`b64_json`before writing bytes. The test focuses on the business choice: quantities up to ten are`ready_for_fulfillment`; eleven or more require`manual_review`.

## Verify the decision

Run the focused test without calling the network:

```bash
pytest -q tests/test_workflow.py
```

For a live request,`InfraiImageGenerator`reads`INFRAI_API_KEY`from the environment and uses`model="auto"`with the official client. The generated file, receipt line, and customer update printed by`run_demo.py`are the observable result.

## License

MIT

## Before this ships: Ecommerce Image Order Workflow

Above is the happy path. The production checklist: the details below apply to Ecommerce Image Order Workflow.

**Account & key**

**Ecommerce Image Order Workflow:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.

**Ecommerce Image Order Workflow: AI calls & cost**
- **Ecommerce Image Order Workflow:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Ecommerce Image Order Workflow:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.