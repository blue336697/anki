# Feign

### 1、默认postMapping的默认ContentType

没有指定contentType时，默认为Form-data

### 常用参数

**常用（通用 Feign 层）**

- **connectTimeout/readTimeout**: 连接/读取超时，毫秒。影响调用等待时长。
- **loggerLevel**: 日志级别（NONE/BASIC/HEADERS/FULL），控制请求/响应打印粒度。
- **retryer**: 重试策略（禁用/默认/自定义），决定超时或 5xx 等失败时是否重试与次数、间隔。
- **errorDecoder**: 异常解码器，把非 2xx 响应转换为业务异常。
- **encoder/decoder**: 请求编码器与响应解码器（JSON、Form、Multipart 等）。
- **contract**: 注解契约（原生 Feign vs Spring MVC 注解），通常使用 SpringMvcContract。
- **requestInterceptors**: 请求拦截器，统一加签、透传 Header、链路追踪等。
- **options(followRedirects)**: 其它请求级选项，如是否跟随重定向。
- **decode404**: 将 404 也走解码器（而非抛异常）。

### **Spring Cloud OpenFeign 常用属性（按客户端或 default 作用域）**

- feign.client.config.<name>.connectTimeout/readTimeout: 超时。
- feign.client.config.<name>.loggerLevel: 日志级别。
- feign.client.config.<name>.retryer: 重试（可填 neverRetry 或自定义类名）。
- feign.client.config.<name>.errorDecoder/encoder/decoder/contract: 指定实现类名。
- feign.client.config.<name>.decode404: 是否解码 404。
- 作用域说明：<name> 为 @FeignClient(name=...) 或 default 全局。

### **HTTP 客户端选择与相关参数**

- **OkHttp**（推荐）
- feign.okhttp.enabled=true 启用；超时仍以 Feign connect/readTimeout 为准。
- 进阶：自定义 OkHttpClient Bean（连接池大小、keep-alive、写超时等）。
- **Apache HttpClient**
- feign.httpclient.enabled=true 启用。
- feign.httpclient.maxConnections/maxConnectionsPerRoute: 连接池大小。
- feign.httpclient.connectionTimeout/connectionRequestTimeout/timeToLive: 连接/取连接/存活期。
- feign.httpclient.followRedirects/disableSslValidation: 重定向/SSL 校验。

### **压缩与性能**

- feign.compression.request.enabled/response.enabled: 开启请求/响应 GZIP。
- feign.compression.request.mime-types/min-request-size: 指定压缩的内容类型与最小大小。
- feign.circuitbreaker.enabled: 打开熔断（Resilience4j），可配合 fallback/fallbackFactory。
- feign.metrics.enabled（版本依赖）: 暴露 Micrometer 指标。

```yaml
spring:
  main:
    allow-bean-definition-overriding: true

feign:
  okhttp:
    enabled: true            # use OkHttp as HTTP client
  httpclient:
    enabled: false           # disable Apache HttpClient (二选一)
  compression:
    request:
      enabled: true
      mime-types: application/json,application/xml,text/plain
      min-request-size: 2048
    response:
      enabled: true
  circuitbreaker:
    enabled: true            # enable resilience4j circuit breaker (需依赖)

  client:
    config:
      default:               # global default
        connectTimeout: 2000
        readTimeout: 3000
        loggerLevel: BASIC   # NONE/BASIC/HEADERS/FULL
        decode404: true
      user-service:          # per client override (@FeignClient(name="user-service"))
        connectTimeout: 1500
        readTimeout: 2500
        loggerLevel: FULL

# Apache HttpClient 方式的连接池参数（若启用 httpclient）
# feign:
#   httpclient:
#     enabled: true
#     maxConnections: 200
#     maxConnectionsPerRoute: 50
#     connectionTimeout: 2000
#     connectionRequestTimeout: 2000
#     timeToLive: 900
```

全局配置

- @EnableFeignClients注解通过指定或者全路径扫描的机制（(basePackages = "com.example.feign.client")），把@FeignClient的类全部扫描出来，通过动态代理的形式去调用Http客户端

```java
package com.example.feign.config;

import feign.Logger;
import feign.Retryer;
import feign.codec.ErrorDecoder;
import feign.Request;
import okhttp3.ConnectionPool;
import okhttp3.OkHttpClient;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

/**
 * Global Feign configuration.
 * Provide logger level, retryer, timeouts, interceptor and OkHttp client.
 */
@Configuration
@EnableFeignClients(basePackages = "com.example.feign.client")
public class FeignGlobalConfig {

    /**
     * Set Feign logger level.
     * @return logger level
     */
    @Bean
    public Logger.Level feignLoggerLevel() {
        return Logger.Level.BASIC;
    }

    /**
     * Disable retries globally (recommend in most cases).
     * Use custom policy if interface is idempotent.
     * @return retryer
     */
    @Bean
    public Retryer feignRetryer() {
        return Retryer.NEVER_RETRY;
    }

    /**
     * Configure Feign request options (timeouts, redirects).
     * Note: values here can be overridden by application.yml per client.
     * @return request options
     */
    @Bean
    public Request.Options feignRequestOptions() {
        return new Request.Options(2000, TimeUnit.MILLISECONDS, 3000, TimeUnit.MILLISECONDS, true);
    }

    /**
     * Global error decoder to translate non-2xx response into exceptions.
     * @return error decoder
     */
    @Bean
    public ErrorDecoder feignErrorDecoder() {
        return new com.example.feign.error.GlobalErrorDecoder();
    }

    /**
     * Register a global request interceptor (e.g., trace and auth headers).
     * @return interceptor
     */
    @Bean
    public feign.RequestInterceptor traceInterceptor() {
        return new com.example.feign.interceptor.TraceInterceptor();
    }

    /**
     * OkHttp client with connection pool and timeouts.
     * Enabled when feign.okhttp.enabled=true.
     * @return OkHttpClient
     */
    @Bean
    public OkHttpClient okHttpClient() {
        return new OkHttpClient.Builder()
                .connectTimeout(2, TimeUnit.SECONDS)
                .readTimeout(3, TimeUnit.SECONDS)
                .writeTimeout(3, TimeUnit.SECONDS)
                .connectionPool(new ConnectionPool(100, 5, TimeUnit.MINUTES))
                .retryOnConnectionFailure(false)
                .build();
    }
}
```

错误码

```java
package com.example.feign.error;

import feign.Response;
import feign.codec.ErrorDecoder;

/**
 * Global error decoder.
 * Convert HTTP status and body to meaningful exceptions.
 */
public class GlobalErrorDecoder implements ErrorDecoder {

    /**
     * Decode non-2xx responses.
     * @param methodKey feign method key
     * @param response http response
     * @return runtime exception
     */
    @Override
    public Exception decode(String methodKey, Response response) {
        int status = response.status();
        String message = "Remote error, status=" + status + ", method=" + methodKey;
        if (status >= 500) {
            return new RuntimeException("Server error: " + message);
        } else if (status == 404) {
            return new RuntimeException("Not found: " + message);
        } else if (status == 429) {
            return new RuntimeException("Too many requests: " + message);
        }
        return new RuntimeException("Client error: " + message);
    }
}
```

拦截器和降级配置

```java
package com.example.feign.interceptor;

import feign.RequestInterceptor;
import feign.RequestTemplate;

import java.util.UUID;

/**
 * Trace and auth interceptor.
 * Add common headers before sending requests.
 */
public class TraceInterceptor implements RequestInterceptor {

    /**
     * Apply headers for each request.
     * @param template request template
     */
    @Override
    public void apply(RequestTemplate template) {
        template.header("X-Trace-Id", UUID.randomUUID().toString());
        // template.header("Authorization", "Bearer " + tokenProvider.get());
        template.header("Accept-Encoding", "gzip");
    }
}

package com.example.feign.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * Example feign client.
 * name must match application.yml section feign.client.config.user-service.
 */
@FeignClient(
        name = "user-service",
        url = "${user.service.url:http://localhost:8081}",
        configuration = com.example.feign.config.FeignGlobalConfig.class,
        fallbackFactory = com.example.feign.client.UserClientFallbackFactory.class
)
public interface UserClient {

    /**
     * Ping endpoint.
     * @return ok string
     */
    @GetMapping("/api/ping")
    String ping();
}
```

### **为什么必须标在接口上（以及为何用接口）**

- 本质：Feign 通过 JDK 动态代理在运行期为接口生成实现。代理将“方法调用”翻译为“HTTP 请求”。JDK 动态代理只能代理接口，不能直接代理具体类。
- Spring 集成流程：@FeignClient → FeignClientsRegistrar 扫描 → 注册 FeignClientFactoryBean → 调用 Feign.Builder.target(...) → 创建 JDK 代理实例并注入到容器。
- 设计原因：
- 接口即“契约”，天然无状态，便于声明式映射 HTTP 请求，方法签名可被 Contract 解析成请求模板。
- 类型安全与可测试：接口易于 Mock/替换，解耦实现与调用方。
- 运行期开销更小：直接用 JDK 代理，无需 CGLIB 生成子类，也避免要求无参构造等限制。