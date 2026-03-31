import http from "node:http";
import { randomUUID } from "node:crypto";

const todos = new Map();

function send(res, status, body) {
  res.statusCode = status;
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.end(JSON.stringify(body));
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => (data += chunk));
    req.on("end", () => {
      if (!data) return resolve({});
      try {
        resolve(JSON.parse(data));
      } catch (e) {
        reject(e);
      }
    });
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);
  const method = req.method ?? "GET";

  if (method === "GET" && url.pathname === "/health") {
    return send(res, 200, { ok: true });
  }

  if (url.pathname === "/todos" && method === "GET") {
    const data = Array.from(todos.values()).sort((a, b) => a.createdAt.localeCompare(b.createdAt));
    return send(res, 200, { data });
  }

  if (url.pathname === "/todos" && method === "POST") {
    try {
      const body = await readJson(req);
      const title = typeof body.title === "string" ? body.title.trim() : "";
      if (!title) return send(res, 400, { error: "title is required" });

      const id = randomUUID();
      const todo = { id, title, completed: false, createdAt: new Date().toISOString() };
      todos.set(id, todo);
      return send(res, 201, { data: todo });
    } catch {
      return send(res, 400, { error: "invalid json" });
    }
  }

  const todoIdMatch = url.pathname.match(/^\/todos\/([^/]+)$/);
  if (todoIdMatch) {
    const id = todoIdMatch[1];
    const todo = todos.get(id);
    if (!todo) return send(res, 404, { error: "todo not found" });

    if (method === "GET") return send(res, 200, { data: todo });

    if (method === "PATCH") {
      try {
        const body = await readJson(req);
        if (body.title !== undefined) {
          const title = typeof body.title === "string" ? body.title.trim() : "";
          if (!title) return send(res, 400, { error: "title must be non-empty" });
          todo.title = title;
        }
        if (body.completed !== undefined) {
          if (typeof body.completed !== "boolean") return send(res, 400, { error: "completed must be boolean" });
          todo.completed = body.completed;
        }
        todos.set(id, todo);
        return send(res, 200, { data: todo });
      } catch {
        return send(res, 400, { error: "invalid json" });
      }
    }

    if (method === "DELETE") {
      todos.delete(id);
      res.statusCode = 204;
      return res.end();
    }
  }

  return send(res, 404, { error: "not found" });
});

const port = Number(process.env.PORT ?? 3005);
server.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`[demo] todo server listening on http://localhost:${port}`);
});

