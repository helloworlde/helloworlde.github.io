---
title: gRPC 中监听 Sream 和 Transport 的事件
type: post
date: 2020-12-23T22:34:46+08:00
tags:
  - gRPC
featured: true
---

gRPC 提供了拦截器可以监听请求的事件，但是对于 Stream 或者 Transport 的具体事件，无法通过拦截器实现；gRPC 提供了 StreamTracer 和 TransportFilter 支持这样的能力

## StreamTracer

`StreamTracer` 用于监听流的所有事件，包括流关闭、出入站消息、出入站流大小等信息

`StreamTracer` 有用于客户端的 `ClientStreamTracer` 和用于服务端的 `ServerStreamTracer`

### 客户端

客户端的 `StreamTracer` 在拦截器中注入，当有请求被执行时，可以向 `callOptions` 添加自定义的 `ClientStreamTracer.Factory`，这样就会创建相应的 `StreamTracer`，实现监听

- CustomClientInterceptor.java

在拦截器中指定

```java
public class CustomClientInterceptor implements ClientInterceptor {
    @Override
    public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(MethodDescriptor<ReqT, RespT> method, CallOptions callOptions, Channel next) {
        callOptions = callOptions.withStreamTracerFactory(new CustomClientStreamTracerFactory<>(method, callOptions, next));

        return next.newCall(method, callOptions);
    }
}
```

- CustomClientStreamTracerFactory.java

在实现类中重写需要监听的事件方法

```java
public class CustomClientStreamTracerFactory<ReqT, RespT> extends ClientStreamTracer.Factory {

    private final MethodDescriptor<ReqT, RespT> method;
    private final CallOptions callOptions;
    private final Channel next;

    public CustomClientStreamTracerFactory(MethodDescriptor<ReqT, RespT> method, CallOptions callOptions, Channel next) {
        this.method = method;
        this.callOptions = callOptions;
        this.next = next;
    }

    @Override
    public ClientStreamTracer newClientStreamTracer(ClientStreamTracer.StreamInfo info, Metadata headers) {
        return new CustomClientStreamTracer<>(method, callOptions, next, info, headers);
    }
}

@Slf4j
class CustomClientStreamTracer<ReqT, RespT> extends ClientStreamTracer {

    public CustomClientStreamTracer(MethodDescriptor<ReqT, RespT> method, CallOptions callOptions, Channel next, StreamInfo info, Metadata headers) {
        log.info("Method:" + method.getFullMethodName() + " Next:" + next.authority() + " Header: " + headers.toString());
    }
}

```

### 服务端

服务端的 `StreamTracer` 在构建 Server 时指定，在执行请求时会监听相应的方法

- 构建 Server

```java
Server server = ServerBuilder.forPort(1235)
                             .addStreamTracerFactory(new CustomServerStreamTracerFactory())
                             .build();
```

- CustomServerStreamTracerFactory.java

可以在 `CustomServerStreamTracer` 中重写要监听的事件的方法

```java
public class CustomServerStreamTracerFactory extends ServerStreamTracer.Factory {
    @Override
    public ServerStreamTracer newServerStreamTracer(String fullMethodName, Metadata headers) {
        return new CustomServerStreamTracer(fullMethodName, headers);
    }
}

@Slf4j
class CustomServerStreamTracer extends ServerStreamTracer {

    private final String fullMethodName;

    private final Metadata headers;

    public CustomServerStreamTracer(String fullMethodName, Metadata headers) {
        this.fullMethodName = fullMethodName;
        this.headers = headers;
    }
}
```

## Transport 监听

可以监听 `Transport` 的就绪和终止事件

### Server 端

- CustomServerTransportFilter.java

```java
@Slf4j
public class CustomServerTransportFilter extends ServerTransportFilter {

    @Override
    public Attributes transportReady(Attributes transportAttrs) {
        log.info("CustomServerTransportFilter transportReady, transportAttrs: {}", transportAttrs);
        return super.transportReady(transportAttrs);
    }

    @Override
    public void transportTerminated(Attributes transportAttrs) {
        log.info("CustomServerTransportFilter transportTerminated, transportAttrs: {}", transportAttrs);
        super.transportTerminated(transportAttrs);
    }
}
```
