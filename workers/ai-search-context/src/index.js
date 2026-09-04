const MAX_REQUEST_BYTES = 64 * 1024;
const MAX_PAGE_TEXT_CHARS = 20000;

const META_FIELDS = new Set([
  "title",
  "description",
  "url",
  "tags",
  "document_id",
  "content_type",
]);

function compactText(value) {
  return value.replace(/\s+/g, " ").trim();
}

export function normalizeDocumentURL(referrer, blogOrigin) {
  if (!referrer) return null;

  try {
    const candidate = new URL(referrer);
    const origin = new URL(blogOrigin);
    if (candidate.origin !== origin.origin || candidate.pathname.startsWith("/api/ai/")) {
      return null;
    }
    candidate.hash = "";
    candidate.search = "";
    return candidate;
  } catch {
    return null;
  }
}

export function buildContextPrompt(context, question) {
  const fields = [
    "当前文档（由站点自动提供，请优先依据它回答）：",
    `标题：${context.title || "未知"}`,
    `URL：${context.url}`,
    `标签：${context.tags || "无"}`,
    `内容类型：${context.content_type || "page"}`,
  ];

  if (context.description) fields.push(`摘要：${context.description}`);
  if (context.text) fields.push(`正文：\n${context.text}`);
  fields.push(`\n用户问题：${question}`);
  return fields.join("\n");
}

export function enrichChatPayload(body, context) {
  const messages = body.messages.map((message) => ({ ...message }));
  let userIndex = -1;

  for (let index = messages.length - 1; index >= 0; index -= 1) {
    if (messages[index].role === "user" && typeof messages[index].content === "string") {
      userIndex = index;
      break;
    }
  }

  if (userIndex < 0) throw new Error("A user message with string content is required");
  messages[userIndex].content = buildContextPrompt(context, messages[userIndex].content);

  const incomingOptions = body.ai_search_options ?? {};
  const incomingRetrieval = incomingOptions.retrieval ?? {};
  const shouldFilterCurrentPost =
    context.document_id && new URL(context.url).pathname.startsWith("/posts/");

  return {
    ...body,
    messages,
    ai_search_options: {
      ...incomingOptions,
      retrieval: {
        ...incomingRetrieval,
        ...(shouldFilterCurrentPost
          ? { filters: { document_id: context.document_id } }
          : {}),
      },
    },
  };
}

async function extractDocumentContext(response, fallbackURL) {
  const context = {
    title: "",
    description: "",
    url: fallbackURL,
    tags: "",
    document_id: "",
    content_type: "",
    text: "",
  };

  const metaHandler = {
    element(element) {
      const name = (element.getAttribute("name") || "").toLowerCase();
      if (META_FIELDS.has(name)) context[name] = element.getAttribute("content") || "";
    },
  };

  const textHandler = {
    text(chunk) {
      if (context.text.length >= MAX_PAGE_TEXT_CHARS) return;
      context.text += `${chunk.text} `;
    },
  };

  await new HTMLRewriter()
    .on("head meta[name]", metaHandler)
    .on(".ai-search-document", textHandler)
    .transform(response)
    .arrayBuffer();

  context.text = compactText(context.text).slice(0, MAX_PAGE_TEXT_CHARS);
  context.url = context.url || fallbackURL;
  return context;
}

async function loadDocumentContext(request, env) {
  const documentURL = normalizeDocumentURL(request.headers.get("Referer"), env.BLOG_ORIGIN);
  if (!documentURL) return null;

  const response = await fetch(documentURL, {
    headers: { Accept: "text/html" },
    cf: { cacheEverything: true, cacheTtl: 300 },
  });

  if (!response.ok || !response.headers.get("content-type")?.includes("text/html")) {
    return { url: documentURL.href, text: "" };
  }

  return extractDocumentContext(response, documentURL.href);
}

function jsonError(message, status) {
  return Response.json({ error: { message } }, { status });
}

async function handleChat(request, env) {
  const contentLength = Number(request.headers.get("Content-Length") || 0);
  if (contentLength > MAX_REQUEST_BYTES) return jsonError("Request body is too large", 413);

  let body;
  try {
    body = await request.json();
  } catch {
    return jsonError("Request body must be valid JSON", 400);
  }

  if (!body || !Array.isArray(body.messages) || body.messages.length === 0) {
    return jsonError("messages must be a non-empty array", 400);
  }

  const context = await loadDocumentContext(request, env);
  if (!context) return jsonError("A valid blog page Referer is required", 400);

  let payload;
  try {
    payload = enrichChatPayload(body, context);
  } catch (error) {
    return jsonError(error.message, 400);
  }

  const result = await env.AI_SEARCH.chatCompletions(payload);
  if (result instanceof ReadableStream) {
    return new Response(result, {
      headers: {
        "Cache-Control": "no-store",
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Content-Type-Options": "nosniff",
      },
    });
  }

  return Response.json(result, {
    headers: { "Cache-Control": "no-store" },
  });
}

async function forwardStats(request, env) {
  return fetch(`${env.AI_SEARCH_PUBLIC_ENDPOINT}/stats`, {
    method: "POST",
    headers: { "Content-Type": request.headers.get("Content-Type") || "application/json" },
    body: request.body,
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "POST" && url.pathname === "/api/ai/chat/completions") {
      return handleChat(request, env);
    }

    if (request.method === "POST" && url.pathname === "/api/ai/stats") {
      return forwardStats(request, env);
    }

    if (request.method === "GET" && url.pathname === "/api/ai/health") {
      return Response.json({ ok: true, component: "cloudflare-ai-search" });
    }

    return jsonError("Not found", 404);
  },
};
