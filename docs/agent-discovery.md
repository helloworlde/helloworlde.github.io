# Agent discovery deployment

The Hugo repository owns the blog's static discovery documents and WebMCP tool. GitHub Pages does not provide repository-level custom response headers, so the homepage `Link` header and Markdown content negotiation must be configured at the Cloudflare edge for `blog.hellowood.dev`.

## Cloudflare changes

Create a Response Header Transform Rule matching:

```text
http.host eq "blog.hellowood.dev" and http.request.uri.path eq "/"
```

Set the static `Link` response header to:

```text
</llms.txt>; rel="describedby"; type="text/plain", </.well-known/agent-skills/index.json>; rel="describedby"; type="application/json"
```

Enable Markdown for Agents with a Configuration Rule matching:

```text
http.host eq "blog.hellowood.dev"
```

Set **Markdown for Agents** to **On**. The equivalent ruleset action parameter is `content_converter: true` in the `http_config_settings` phase.

## Runtime verification

```bash
curl -sSI https://blog.hellowood.dev/ | grep -i '^link:'
curl -sSI -H 'Accept: text/markdown' https://blog.hellowood.dev/ | grep -Ei '^(content-type|vary|x-markdown-tokens):'
curl -sS https://blog.hellowood.dev/.well-known/agent-skills/index.json
```

The first response must include the two `describedby` links. The second must use `Content-Type: text/markdown` and include `Accept` in `Vary`.

## Findings that do not apply to this site

Do not publish placeholder metadata for capabilities the static blog does not provide:

- API catalog: there is no public application API to catalog.
- OAuth/OIDC discovery and protected-resource metadata: there is no protected API resource or authorization server.
- `auth.md`: there is no agent registration or credential provisioning flow.
- MCP Server Card: there is no MCP transport endpoint.
- DNS-AID: there is no A2A, MCP, or other agent protocol endpoint to advertise through DNS.

Revisit these findings only after the corresponding runtime service exists.
