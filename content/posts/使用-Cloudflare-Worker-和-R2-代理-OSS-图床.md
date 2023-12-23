---
title: "使用 Cloudflare Worker 和 R2 代理 OSS 图床"
date: 2023-12-23T19:14:05+08:00
tags:
    - Cloudflare
    - HomeLab
categories: 
    - Cloudflare
    - HomeLab
series: 
    - Cloudflare
featured: true  
---

# 使用 Cloudflare Worker 和 R2 代理 OSS 图床

因为笔记可能会在多个平台发布，因此之前使用阿里云的 OSS 作为图片存储，直接将 OSS 的地址暴露到公网进行访问；但是随着流量逐渐增加，每月产生的流量费用也水高船涨，更重要的是 OSS 只支持 Refer 限制，并不能保证安全，在看到有人分享被刷 CDN 产生巨额费用后觉得必须要重视安全问题。

赛博菩萨 Cloudflare 提供了 R2 作为存储，提供了 5GB 免费的容量，对于个人完全够用了；同时 Worker 支持 CDN 缓存及就近访问，因此使用 Worker 代理 R2 访问完全能满足我的需求

考虑到有多个平台都是用了 OSS 作为链接，需要逐步迁移；因此，使用 Workers 优先从 R2 读取，如果 R2 没有则从 OSS 获取，并存储到 R2 中

## 安装 wrangler

在本地使用 wrangler 开发 Worker

- 安装 wrangler

参考 [Install/Update Wrangler](https://developers.cloudflare.com/workers/wrangler/install-and-update/) 进行安装


## 创建 R2

在 Cloudflare 管理平台创建 R2，或者通过 wrangler 进行创建，参考 [Create buckets](https://developers.cloudflare.com/r2/buckets/create-buckets/)

```bash
wrangler r2 bucket create picture
```

## 创建 Worker 

- 创建项目

```bash
npm create cloudflare@latest
```

- 将 R2 绑定到 Worker

修改 wrangler.toml 配置文件，将 R2 绑定到当前 worker

```
[[r2_buckets]]
binding = "PICTURE"
bucket_name = "picture"
```

- 添加 OSS 地址到环境变量

为了配置方便和安全，将 OSS 的地址添加到环境变量中，修改 wrangler.toml 配置文件：

```
[vars]
REMOTE_DATA_ADDRESS="https://xxx.com"
```

- 实现代码逻辑

修改 `src/index.js` 文件，实现代理逻辑：
解析访问路径，检查是否在 R2 中存在文件，如果存在则从 R2 获取，如果不存在则从 OSS 获取并同步到 R2 中

```javascript
export default {
	async fetch(request, env) {
		const url = new URL(request.url);
		const resoureName = url.pathname;
		console.log("ResourceName: ", resoureName);
		if (resoureName == undefined || resoureName == "" || resoureName == "/") {
			const html = `<!DOCTYPE html><body><p>Hello World</p></body>`;
			return new Response(html, {
				headers: {
					"content-type": "text/html;charset=UTF-8",
				},
			});
		}

		switch (request.method) {
			case 'GET':
				let object = await env.PICTURE.get(resoureName);

				if (object === null) {
					const imageUrl = env.REMOTE_DATA_ADDRESS + "/" + resoureName;
					console.log("Path ", resoureName, " 不存在，从 OSS 拉取");
					const imageResponse = await fetch(imageUrl);
					if (imageResponse.status === 200) {
						console.log("Path ", resoureName, " 拉取成功，保存到 R2");
						const imageData = await imageResponse.arrayBuffer();
						await env.BLOG_PICTURE.put(resoureName, imageData);
						object = await env.BLOG_PICTURE.get(resoureName);
					}
				}

				if (object === null) {
					return new Response(undefined, { status: 404 })
				}

				const headers = new Headers();
				object.writeHttpMetadata(headers);
				headers.set('etag', object.httpEtag);

				return new Response(object.body, {
					headers,
				});

			default:
				return new Response('Method Not Allowed', {
					status: 405,
					headers: {
						Allow: 'GET',
					},
				});
		}
	},
};
```

## 部署 Worker 

在本地使用 wrangler 进行部署

```bash
npx wrangler deploy
```

部署完成后访问文件的地址，返回的数据正常，同时在 R2 检查发现文件已经同步到 R2了，再次访问发现是从 R2 获取的，说明代理成功

![homelab-image-proxy-from-cloudflare-analysis.png](https://img.hellowood.dev/picture/homelab-image-proxy-from-cloudflare-analysis.png)