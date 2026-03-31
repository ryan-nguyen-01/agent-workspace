import assert from "node:assert/strict";

const base = "http://localhost:3005";

async function req(path, options = {}) {
  const res = await fetch(`${base}${path}`, {
    headers: { "content-type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });
  const text = await res.text();
  const json = text ? JSON.parse(text) : null;
  return { res, json };
}

async function run() {
  {
    const { res, json } = await req("/health");
    assert.equal(res.status, 200);
    assert.equal(json.ok, true);
  }

  let id;
  {
    const { res, json } = await req("/todos", { method: "POST", body: JSON.stringify({ title: "first" }) });
    assert.equal(res.status, 201);
    assert.equal(json.data.title, "first");
    id = json.data.id;
  }

  {
    const { res, json } = await req(`/todos/${id}`);
    assert.equal(res.status, 200);
    assert.equal(json.data.id, id);
  }

  {
    const { res, json } = await req(`/todos/${id}`, { method: "PATCH", body: JSON.stringify({ completed: true }) });
    assert.equal(res.status, 200);
    assert.equal(json.data.completed, true);
  }

  {
    const { res } = await req(`/todos/${id}`, { method: "DELETE" });
    assert.equal(res.status, 204);
  }

  // eslint-disable-next-line no-console
  console.log("[demo] tests passed");
}

run().catch((e) => {
  // eslint-disable-next-line no-console
  console.error(e);
  process.exitCode = 1;
});

