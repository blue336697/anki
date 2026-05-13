# Swagger相关（springfox等）

### **1、`EnableSwagger2WebMvc与EnableSwagger2WebFlux`**

Swagger组件从2.10.0以后对于配置注解`@EnableSwagger2`注解做出了区别，为了配合响应式编程将这个注解拆分扩充为两个，分别为：`@EnableSwagger2WebMvc`和`@EnableSwagger2WebFlux`，用于区分**阻塞式编程框架**和**响应式编程框架**，并直接去除了`@EnableSwagger2`注解

## 2、对于swagger来说JDK17更改挺多的