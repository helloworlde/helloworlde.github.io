import assert from "node:assert/strict";
import test from "node:test";

import {
  buildContextPrompt,
  enrichChatPayload,
  normalizeDocumentURL,
} from "../src/index.js";

test("accepts only same-origin blog document URLs", () => {
  const accepted = normalizeDocumentURL(
    "https://blog.hellowood.dev/posts/pve-9-install-nvidia-driver/?from=test#part",
    "https://blog.hellowood.dev",
  );

  assert.equal(accepted.href, "https://blog.hellowood.dev/posts/pve-9-install-nvidia-driver/");
  assert.equal(normalizeDocumentURL("https://evil.example/posts/a/", "https://blog.hellowood.dev"), null);
  assert.equal(normalizeDocumentURL("https://blog.hellowood.dev/api/ai/health", "https://blog.hellowood.dev"), null);
});

test("injects current document information into the latest user message", () => {
  const context = {
    title: "PVE 9 安装 Nvidia 驱动",
    url: "https://blog.hellowood.dev/posts/pve-9-install-nvidia-driver/",
    tags: "PVE, Nvidia, CUDA",
    content_type: "posts",
    document_id: "doc-123",
    description: "安装说明",
    text: "Linux 6.14 and Nvidia 550",
  };
  const payload = enrichChatPayload(
    { messages: [{ role: "user", content: "当前页面讲了什么？" }], stream: true },
    context,
  );

  assert.match(payload.messages[0].content, /PVE 9 安装 Nvidia 驱动/);
  assert.match(payload.messages[0].content, /当前页面讲了什么/);
  assert.deepEqual(payload.ai_search_options.retrieval.filters, { document_id: "doc-123" });
});

test("does not force a post filter for non-post pages", () => {
  const payload = enrichChatPayload(
    { messages: [{ role: "user", content: "有哪些文章？" }] },
    { title: "首页", url: "https://blog.hellowood.dev/", document_id: "home", text: "" },
  );

  assert.equal(payload.ai_search_options.retrieval.filters, undefined);
});

test("formats a compact current-document prompt", () => {
  const prompt = buildContextPrompt(
    { title: "标题", url: "https://blog.hellowood.dev/posts/a/", tags: "tag", text: "正文" },
    "问题",
  );
  assert.match(prompt, /标题：标题/);
  assert.match(prompt, /URL：https:\/\/blog\.hellowood\.dev\/posts\/a\//);
  assert.match(prompt, /正文：\n正文/);
  assert.match(prompt, /用户问题：问题/);
});
