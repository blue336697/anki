# 关于javassist的学习

### **当在内存中已经生成了一份class（已经类加载过了），当你想去修改这个class时会报错：frozen class (cannot edit)**

![image.png](关于javassist的学习/image.png)

提供的类删除方法都是protected

### **使用@Data等自动生成构造器、getter、setter方法时无法正常使用，也不会报错**

生成的类所构成的excel都是没有具体的值，像是setter并没有生效；所以还是乖乖手写编入