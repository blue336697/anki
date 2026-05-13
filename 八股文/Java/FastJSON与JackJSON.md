# FastJSON/JackJSON的学习以及遇到的坑

### **坑**

- 当使用HttpUtil.post(url, JSONObject.toJSONString(param), 5000);其中的JSONObject.toJSONString(param)，序列化参数时，如果param参数中存在完全两个一样的实体，那么Json会将其进行简化成一个；原先在使用Feign远程调用接口时，则不需要关心这些，Feign对其进行了透明化，现在使用新的模板发送时，则是通过HTTP调用post，所以需要自己选择序列化的方法

> {"111","lhj"},{"111","lhj"}--------→{"111","lhj"}
> 

### **解析Json字符串至Map的两种方式**

- 原始数据Json字符串如下：

```json
{
  "3001908": "星展银行（中国）有限公司（银联数据）",
  "3001250": "大连银行股份有限公司（银联数据）"
}
```

处理方法：

展开源码

- 原始Json字符串如下：

```json
[
  {
    "apicode": "3001908",
    "实际客户名称": "星展银行（中国）有限公司（银联数据）"
  },
  { "apicode": "3001250", "实际客户名称": "大连银行股份有限公司（银联数据）" }
]
```

---

处理方法：

```java
 @Test
   public void test01() {
       String config = "[ { "apicode": "3001908", "实际客户名称": "星展银行（中国）有限公司（银联数据）" }, { "apicode": "3001250", "实际客户名称": "大连银行股份有限公司（银联数据）" } ]";
       List<JSONObject> list = JSONArray.parseArray(config, JSONObject.class);
       Map<String, String> collect = list.stream().filter(Objects::nonNull)
               .collect(Collectors.toMap(item -> item.getString("apicode"), item -> item.getString("实际客户名称")));
   }
```

---

### **循环依赖检测——SerializerFeature.DisableCircularReferenceDetec**

使用方法如下，使用后Json不会在进行引用检测，重复引用对象时就不会被$ref 代替，也就是说当出现重复饮用时，Json结构体会拿**$ref**符号去替换重复引用的字段名。取消引用检测后随后会使存储的数据是完整的，但是在循环引用时也会导致 StackOverflowError 异常。

```java
// 对象存在自引用，自己序列化
String userJson = JSONObject.toJSONString(user, SerializerFeature.DisableCircularReferenceDetect);
```

---

### **什么是重复引用**

![image.png](FastJSON JackJSON的学习以及遇到的坑/image.png)

```java
class User {
    private String name;
    private User friend;
 
    public User(String name) {
        this.name = name;
    }
 
    public void setFriend(User friend) {
        this.friend = friend;
    }
}
 
public class Main {
    public static void main(String[] args) {
        User user1 = new User("Alice");
        User user2 = new User("Bob");
 
        // 创建循环引用
        user1.setFriend(user2);
        user2.setFriend(user1);
 
        // 禁用循环引用检测（DisableCircularReferenceDetect）
        String jsonWithCircularReference = JSON.toJSONString(user1, SerializerFeature.DisableCircularReferenceDetect);
        System.out.println("JSON with circular reference detect disabled:");
        System.out.println(jsonWithCircularReference);
 
        // 默认开启循环引用检测
        String jsonWithoutCircularReference = JSON.toJSONString(user1);
        System.out.println("JSON without circular reference (disabled):");
        System.out.println(jsonWithoutCircularReference);
    }
}
```

---

![image.png](FastJSON JackJSON的学习以及遇到的坑/image 1.png)

```java
public void test01() {
        JSONObject base = new JSONObject();
        base.put("class_info", "班级信息");
 
        List<String> userNames = new ArrayList();
        JSONObject programs = new JSONObject();
        userNames.add("学生一");
        userNames.add("学生二");
        if (!CollectionUtils.isEmpty(userNames)) {
            for (String name : userNames) {
                JSONObject baseInfo = base;
                baseInfo.put("user_name", name);
                programs.put(name, baseInfo);
            }
            log.info("=====关闭引用检测前===:{}", JSON.toJSON(programs));
            programs = JSON.parseObject(JSON.toJSONString(programs, SerializerFeature.DisableCircularReferenceDetect));
            log.info("=====多关闭引用检测后===:{}", JSON.toJSON(programs));
        }
}
```

---

### **JackJson序列化循环引用问题：实际上就是对象的相互引用，导致序列化陷入死循环**

> 序列化A时，发现需要B，然后又去序列化B，序列化B时又发现需要A即死循环产生，就跟Spring对象实例化时的循环依赖一样，因为本质上序列化是要调用Getter来获取自己属性的对象
> 
> 
> 目前的解决方法就是标注@JsonBackReference 标记引用结束 或@JsonIgnore忽略当前属性的序列化。两者的原理都是在序列化时忽略被标记的属性；
> 
> 我看在对账系统的用的方法就是尽量将字段类型不要设置成对象，而是涉及这个对象需要用到的字段即可
>