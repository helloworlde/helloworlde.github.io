(function registerHelloWoodWebMCP() {
    "use strict";

    const modelContext = document.modelContext || navigator.modelContext;
    if (!modelContext || typeof modelContext.registerTool !== "function") {
        return;
    }

    const controller = new AbortController();
    let indexPromise;

    function loadIndex() {
        if (!indexPromise) {
            indexPromise = fetch("/index.json", {
                headers: { Accept: "application/json" }
            }).then((response) => {
                if (!response.ok) {
                    throw new Error(`Blog index request failed with HTTP ${response.status}`);
                }
                return response.json();
            });
        }
        return indexPromise;
    }

    function searchableText(post) {
        return [post.title, post.summary, ...(post.tags || [])]
            .join(" ")
            .toLocaleLowerCase();
    }

    function score(post, terms) {
        const title = post.title.toLocaleLowerCase();
        const tags = (post.tags || []).join(" ").toLocaleLowerCase();
        const body = searchableText(post);

        return terms.reduce((total, term) => {
            if (!body.includes(term)) {
                return total;
            }
            return total + (title.includes(term) ? 4 : 0) + (tags.includes(term) ? 2 : 0) + 1;
        }, 0);
    }

    modelContext.registerTool({
        name: "search_hellowood_blog",
        title: "Search HelloWood Blog",
        description: "Search HelloWood's public technical articles by title, summary, and tag. This is read-only and returns canonical article URLs.",
        inputSchema: {
            type: "object",
            properties: {
                query: {
                    type: "string",
                    minLength: 1,
                    description: "Words or phrases to find in the blog. Chinese and English queries are supported."
                },
                limit: {
                    type: "integer",
                    minimum: 1,
                    maximum: 20,
                    default: 5,
                    description: "Maximum number of matching articles to return."
                }
            },
            required: ["query"],
            additionalProperties: false
        },
        annotations: {
            readOnlyHint: true,
            untrustedContentHint: true
        },
        execute: async ({ query, limit = 5 }) => {
            const normalizedQuery = String(query || "").trim().toLocaleLowerCase();
            if (!normalizedQuery) {
                throw new TypeError("query must contain at least one non-whitespace character");
            }

            const safeLimit = Math.min(20, Math.max(1, Number(limit) || 5));
            const terms = normalizedQuery.split(/\s+/u);
            const index = await loadIndex();
            const results = (index.posts || [])
                .map((post) => ({ post, relevance: score(post, terms) }))
                .filter(({ relevance }) => relevance > 0)
                .sort((left, right) => right.relevance - left.relevance)
                .slice(0, safeLimit)
                .map(({ post }) => post);

            return {
                query: String(query).trim(),
                count: results.length,
                results
            };
        }
    }, { signal: controller.signal }).catch((error) => {
        console.warn("Unable to register the HelloWood WebMCP tool", error);
    });

    window.addEventListener("pagehide", (event) => {
        if (!event.persisted) {
            controller.abort();
        }
    });
}());
