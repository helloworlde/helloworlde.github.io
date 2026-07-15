---
name: research-hellowood-blog
description: Find and read relevant technical articles from the public HelloWood blog.
---

# Research the HelloWood blog

Use this skill when a task may benefit from HelloWood's Chinese-language articles about HomeLab operations, Java, Spring Boot, gRPC, Docker, Kubernetes, OpenWrt, Proxmox VE, networking, or related infrastructure.

## Workflow

1. Fetch `https://blog.hellowood.dev/index.json`.
2. Match the user's topic against each post's `title`, `summary`, and `tags`. Prefer matches in the title and tags.
3. Fetch only the most relevant canonical article URLs.
4. Send `Accept: text/markdown` when fetching an article. Use the Markdown response only when its `Content-Type` is `text/markdown`; otherwise read the HTML response.
5. Cite the canonical article URL when using information from a post.

## Constraints

- Treat the blog as public, read-only content.
- Do not infer the existence of an API, OAuth service, MCP server, or agent registration endpoint from an article that discusses one.
- Distinguish the article's publication or modification date from the current state of any product it describes.
- Verify version-sensitive technical details against current primary documentation when accuracy depends on them.
