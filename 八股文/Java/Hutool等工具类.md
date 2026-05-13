# 有关Hutool、Guava、SpringUtils等工具类及遇到的坑

## Excel工具类——poi工具类

**HuTool的Excel相关工具类的底层都是使用poi来实现的，就等于在上面封装了一层**

### **Excel导入解析**

首先我们需要了解Excel的每个解析单位

- sheets：不同的页，相当于一个库中不同的表

![image.png](有关Hutool、Guava、SpringUtils等工具类及遇到的坑/image.png)

- row每行，一般第一行为这个类的标题，红框就是一行
- cell单元格，最小处理单位，绿色框出来的

![image.png](有关Hutool、Guava、SpringUtils等工具类及遇到的坑/image 1.png)

## 坑

### **记录一次2023.7.10号使用工具类遇到的“BUG”**

在使用HuTool的Excel相关工具类时，读取一行自动封装成一个对象，对于Java对象中的字段一般都是String类型，这样解析就算解析到空格也是可以进行映射的，**但是特殊字段类型就会出现映射失败的状态**，在7.10上线对账系统时，需求一解析Excel中，如下图如果在空行中某便某一列放一个空格或者其他什么符号，那么这一列就会被解析成一个对象，那么这个对象也就某个字段会被映射值，或者每个都是null（如果这个空格或者符号出现在没有意义的列上面——图中圆圈），**那么特殊字段，例如Date就会解析这个null或者空格或者某种符号就会解析错误并报错**

![image.png](有关Hutool、Guava、SpringUtils等工具类及遇到的坑/image 2.png)

### **Fail to save: an error occurs while saving the package : The part /docProps/core.xml failed to be saved in the stream with marshaller org.apache.poi**

如果直接生成excel时间太久导致返回到前端的时间太长，tomcat切断连接就会出现这个错误，正确做法

1. 应该是存储在dfs上让前端调用接口下载，而不是直接返回
2. 优化接口性能。

### **序列化的坑**

也不是真正意义上的坑，就是要注意项目用的Jar包版本和使用的工具包所引用的另外一些Jar包版本是否一致，不一致一定要做好低版本兼容

- Map<String, Object> params = BeanUtil.beanToMap(param, false, true);

> 这个方法通过post发出去以后好像解析不了
> 

```java
//低版本
public static Map<String, Object> beanToMap(Object bean, boolean isToUnderlineCase, boolean ignoreNullValue) {
    return beanToMap(bean, new LinkedHashMap(), isToUnderlineCase, ignoreNullValue);
}
 
public static Map<String, Object> beanToMap(Object bean, Map<String, Object> targetMap, final boolean isToUnderlineCase, boolean ignoreNullValue) {
    return bean == null ? null : beanToMap(bean, targetMap, ignoreNullValue, new Editor<String>() {
        public String edit(String key) {
            return isToUnderlineCase ? StrUtil.toUnderlineCase(key) : key;
        }
    });
}
 
public static Map<String, Object> beanToMap(Object bean, Map<String, Object> targetMap, boolean ignoreNullValue, Editor<String> keyEditor) {
    if (bean == null) {
        return null;
    } else {
        Collection<BeanDesc.PropDesc> props = getBeanDesc(bean.getClass()).getProps();
        Iterator i$ = props.iterator();
 
        while(true) {
            String key;
            Object value;
            do {
                while(true) {
                    Method getter;
                    do {
                        if (!i$.hasNext()) {
                            return targetMap;
                        }
 
                        BeanDesc.PropDesc prop = (BeanDesc.PropDesc)i$.next();
                        key = prop.getFieldName();
                        getter = prop.getGetter();
                    } while(null == getter);
 
                    try {
                        value = getter.invoke(bean);
                        break;
                    } catch (Exception var11) {
                    }
                }
            } while(ignoreNullValue && (null == value || value.equals(bean)));
 
            key = (String)keyEditor.edit(key);
            if (null != key) {
                targetMap.put(key, value);
            }
        }
    }
}
```

Map<String, Object> params = BeanUtil.beanToMap(param, args[0]);

```java
	//高版本
	public static Map<String, Object> beanToMap(Object bean, String... properties) {
        int mapSize = 16;
        Editor<String> keyEditor = null;
        if (ArrayUtil.isNotEmpty(properties)) {
            mapSize = properties.length;
            Set<String> propertiesSet = CollUtil.set(false, properties);
            keyEditor = (property) -> {
                return propertiesSet.contains(property) ? property : null;
            };
        }
 
        return beanToMap(bean, new LinkedHashMap(mapSize, 1.0F), false, keyEditor);
    }
```

### **新版本的excel-starter支持导出时字体颜色**

某些系统导出列表数据的时候，字体需要标记颜色，excel-starter升级支持了这种情况，需要的可以试用下；其他需要个性化展示的，可以继承DefaultExcelWorkbookBuilder自行实现

![image.png](有关Hutool、Guava、SpringUtils等工具类及遇到的坑/image 3.png)

![image.png](有关Hutool、Guava、SpringUtils等工具类及遇到的坑/image 4.png)

### **Excel导出**

在目前做众联的excel导出时，发现可以提前通过配置来规范一个导出格式，内部使用的是poi的原始excel组建自己封装的一套，直接传入如下就可以调用在页面配置的模版了

**调用方法** 

```java
this.excelConfigTemplate.exportFromBeanList(volist, "模版名字", request, response);
```

**模版例子** 

```java
{
    "excelName": "百行-百融费用对账单",
    "sheetName": "对账明细列表",
    "headers": [
        "*账单ID",
        "客户名称",
        "*ApiCode",
        "实际客户名称",
        "*账单月份",
        "百融发送账单时间",
        "客户账单金额",
        "客户付费方式",
        "客户对账周期",
        "客户付费周期",
        "应付百融账单金额",
        "百行发送账单时间",
        "客户核账情况",
        "客户核账时间",
        "客户核账金额",
        "客户未核账金额",
        "核账差异",
        "账单调整原因",
        "百行开票情况",
        "百行开票日期",
        "百行开票金额",
        "客户回款情况",
        "客户回款日期",
        "客户回款金额",
        "客户未回款金额",
        "百融占比",
        "应付百融核账金额",
        "应付百融结算金额",
        "百行对账/回款情况",
        "百行对账时间",
        "百融开票时间",
        "百行回款时间"
    ],
    "dsTitles": [
        "billNo",
        "companyName",
        "apiCode",
        "actualCompanyName",
        "billMonth",
        "brSendBillTime",
        "customerBillAmount",
        "proxyPayModeCn",
        "proxyConfirmPeriodCn",
        "proxyPayPeriodCn",
        "proxyBrAmount",
        "proxySendBillTime",
        "customerCheckStatusCn",
        "customerCheckTime",
        "customerCheckAmount",
        "customerUncheckAmount",
        "customerCheckDiff",
        "adjustReason",
        "customerInvoiceStatusCn",
        "customerInvoiceTime",
        "customerInvoiceAmount",
        "customerPaymentStatusCn",
        "customerPaymentTime",
        "customerPaymentAmount",
        "customerUnPaymentAmount",
        "proxyBrPercent",
        "proxyBrCheckAmount",
        "proxyBrSettleAmount",
        "proxyReconciliationPaymentStatusCn",
        "proxyReconciliationTime",
        "brInvoiceTime",
        "proxyPaymentTime"
    ],
    "dsFormat": [
        2,
        2,
        2,
        2,
        22,
        5,
        2,
        2,
        2,
        5,
        22,
        2,
        22,
        5,
        5,
        5,
        2,
        2,
        22,
        5,
        2,
        22,
        5,
        5,
        5,
        5,
        5,
        2,
        22,
        22,
        22
    ],
    "widths": [
        5000,
        6000,
        7000,
        7100,
        3840,
        3840,
        3840,
        3840
    ]
}
```

> 在这个 JSON 对象中，dsFormat 是一个数组，用于指定每个数据列的格式。其中，dsFormat 数组的长度应该与 dsTitles 数组的长度相同，每个元素的值表示对应数据列的格式，具体格式如下：
> 
> 
> 
> | **名字** | **序号** | **意义** |
> | --- | --- | --- |
> | `GENERAL` |  | 水平对齐是一般对齐的。文本数据左对齐。数字、日期和时间右对齐。布尔类型居中。更改对齐方式不会更改数据类型。 |
> | `LEFT` |  | 水平对齐是左对齐的，即使在从右到左模式下也是如此。对齐单元格左边缘的内容。如果指定了缩进量，则单元格的内容将从左侧缩进指定的字符空格数。字符空间基于工作簿的默认字体和字体大小 |
> | `CENTER` |  | 水平对齐方式居中，这意味着文本在整个单元格中居中。 |
> | `RIGHT` |  | 水平对齐方式为右对齐，这意味着单元格内容在单元格的右边缘对齐，即使在从右到左模式下也是如此。 |
> | `FILL` |  | 指示单元格的值应在单元格的整个宽度上填充。如果右侧的空白单元格也具有填充对齐方式，则它们也会使用类似于 centerContinuous 的约定填充该值。附加规则：
> 1. 只能追加整个值，不能追加部分值。
> 2. 该列不会加宽以“最适合”填充值
> 3. 如果追加值的其他匹配项超过单元格左/右边缘的边界，则不要追加该值的其他匹配项。
> 4. 填充单元格的显示值，而不是基础原始数字。 |
> | `JUSTIFY` |  | 水平对齐对齐（左右齐平）。对于每行文本，将单元格中换行文本的每一行向右和向左对齐（最后一行除外）。如果单元格中没有一行文本换行，则文本不对齐。 |
> | `CENTER_SELECTION` |  | 水平对齐方式在多个单元格中居中。有关要跨越多少个单元格的信息在工作表部件中相关单元格的行中表示。对于在对齐方式中跨越的每个单元格，需要写出一个单元格元素，其样式 Id 与引用中心连续对齐的样式 ID 相同。 |
> | `DISTRIBUTED` |  | 指示单元格内每行文本中的每个“单词”均匀分布在单元格的宽度上，并具有齐平的左右边距。当还有要应用的缩进值时，单元格的左侧和右侧都由缩进值填充。“单词”是一组没有空格字符的字符。单元格内的两行由回车符分隔。 |

```java
if (dsFormat == 1) {
    style.setAlignment(HorizontalAlignment.LEFT);
} else if (dsFormat == 2) {
    style.setAlignment(HorizontalAlignment.CENTER);
} else if (dsFormat == 3) {
    style.setAlignment(HorizontalAlignment.RIGHT);
} else if (dsFormat == 4) {
    style.setAlignment(HorizontalAlignment.RIGHT);
    style.setDataFormat(HSSFDataFormat.getBuiltinFormat("0"));
} else if (dsFormat == 5) {
    style.setAlignment(HorizontalAlignment.RIGHT);
    style.setDataFormat(HSSFDataFormat.getBuiltinFormat("#,##0.00"));
} else if (dsFormat == 6) {
    style.setAlignment(HorizontalAlignment.RIGHT);
    style.setDataFormat(HSSFDataFormat.getBuiltinFormat("0.00%"));
} else {
    short builtinFormat;
    if (dsFormat == 61) {
        style.setAlignment(HorizontalAlignment.RIGHT);
        builtinFormat = wb.createDataFormat().getFormat("0.000%");
        style.setDataFormat(builtinFormat);
    } else if (dsFormat == 62) {
        style.setAlignment(HorizontalAlignment.RIGHT);
        builtinFormat = wb.createDataFormat().getFormat("0.0000%");
        style.setDataFormat(builtinFormat);
    } else if (dsFormat == 7) {
        style.setAlignment(HorizontalAlignment.RIGHT);
        style.setDataFormat(HSSFDataFormat.getBuiltinFormat("0.00"));
    } else if (dsFormat == 21) {
        style.setAlignment(HorizontalAlignment.RIGHT);
        builtinFormat = HSSFDataFormat.getBuiltinFormat("m/d/yy h:mm");
        style.setDataFormat(builtinFormat);
    } else if (dsFormat == 22) {
        style.setAlignment(HorizontalAlignment.RIGHT);
        builtinFormat = HSSFDataFormat.getBuiltinFormat("m/d/yy");
        style.setDataFormat(builtinFormat);
    } else {
        style.setAlignment(HorizontalAlignment.CENTER);
    }
}

```

---

### **HSSF和XSSF**

- setColumnWidth()方法：在传值时需要专为short的问题

> 在 Apache POI 库中，setColumnWidth() 方法的第一个参数是 int 类型的列索引，第二个参数是 int 类型的列宽度。但是，由于历史原因，这些参数在 HSSF（用于处理 .xls 文件）和 XSSF（用于处理 .xlsx 文件）中都被声明为 short 类型。
> 
> 
> 因此，如果你使用 `XSSF`，你可以直接传递 `int` 类型的参数给 `setColumnWidth()` 方法，因为 `XSSF` 库会自动将 `int` 类型的参数转换为 `short` 类型。但是，如果你使用 `HSSF`，你需要将 `int` 类型的参数显式转换为 `short` 类型，否则会出现编译错误。
> 
> 在你的示例代码中，你使用了 `XSSF`，因此你可以直接传递 `int` 类型的参数给 `setColumnWidth()` 方法，而不需要显式转换为 `short` 类型。但是，如果你使用 `HSSF`，你需要将参数显式转换为 `short` 类型，否则会出现编译错误。
> 
> ```java
> for(int dsTitlesIndex = 0; dsTitlesIndex < dsTitles.length; ++dsTitlesIndex) {
>     sheet.setColumnWidth((short)dsTitlesIndex, (short)widths[dsTitlesIndex]);
>     XSSFCell cell = headerRow.createCell(dsTitlesIndex);
>     cell.setCellValue(headers.length > dsTitlesIndex ? headers[dsTitlesIndex] : "");
>     cell.setCellStyle(style);
> }
> ```
> 

### **分隔字符串API区别**

![image.png](有关Hutool、Guava、SpringUtils等工具类及遇到的坑/image 5.png)

### **CopyProperties的区别**

- hutu的CopyProperties与spring提供的有着明显的区别，其中对于spring的当复制与被复制的类的字段类型不同则不会赋值成功，具体值为null
- 同时hutu的copyProperties在使用string转int时还会自动转换，比如string的"1,2"会被转化为12

### **HuTool中readBySax(InputStream in, int rid, RowHandler rowHandler)与readBySax(InputStream in, String idOrRidOrSheetName, RowHandler rowHandler)的区别**

### **google中的Immutable与Jdk中的Collections.unmodifiableCollection**

Google的Guava库中的`Immutable`集合和JDK中的`Collections.unmodifiableCollection`都提供了创建不可修改集合的方法，但它们之间存在一些差异：

1. **不变性**：Guava的`Immutable`集合，一旦创建，就不能改变。它不仅保证集合本身不可变，而且保证集合中的元素也不可变。而`Collections.unmodifiableCollection`只是创建了一个不可修改的视图，如果原始集合改变，视图也会改变。**如果往unmodifiableList使用add方法则会报错，同理往immutableList使用add也会报错**
2. **效率**：由于`Immutable`集合在创建时就确定了其不可变性，因此它可以进行一些优化，例如省略不必要的安全检查，使用更紧凑的内部数据结构等。而`Collections.unmodifiableCollection`则需要在每次操作时进行安全检查。
3. **安全性**：`Immutable`集合在序列化时可以保持其不可变性，而`Collections.unmodifiableCollection`在反序列化时可能会失去其不可变性。

在使用时，你需要根据你的需求来选择合适的方法。如果你需要一个真正的不可变集合，你应该使用Guava的`Immutable`集合。如果你只是需要一个不可修改的视图，你可以使用`Collections.unmodifiableCollection`。

请注意，不可变集合并不意味着线程安全。如果集合中的元素是可变的，你仍然需要进行同步来保证线程安全。

### **slf4j.MDC**

mdc和logTrace配合可以实现日志打印链路ID，当使用线程池的时候，可以使用setTaskDecorator，来增强异步子线程去使用主线程的ID

```java
ThreadPoolTaskExecutor threadPoolTaskExecutor = new ThreadPoolTaskExecutor();
threadPoolTaskExecutor.setTaskDecorator(new TaskDecoratorForMdc());
 
public class TaskDecoratorForMdc implements TaskDecorator {
    @Override
    public Runnable decorate(Runnable runnable) {
        try {
            Optional<Map<String, String>> contextMapOptional =Optional.ofNullable(MDC.getCopyOfContextMap());
            return () -> {
                try {
                    contextMapOptional.ifPresent(MDC::setContextMap);
                    runnable.run();
                } finally {
                    MDC.clear();
                }
            };
        } catch (Exception e) {
            return runnable;
        }
    }
}
```

### **cn.hutool.poi.exceptions.POIException: POIXMLException: Zip bomb detected! The file would exceed the max. ratio of compressed file size to the size of the expanded data.**

前提：excel本质上是一个压缩比很高的一种格式，当在使用别的压缩算法去压缩excel效果并不是很明显

压缩比：文本中存在数字1亿个1，当使用压缩算法后写成文本的“1亿个1”，那么原始可能有几个g，压缩后只有几Kb

原因：因为hutool检测到压缩比高的惊人，所以就害怕直接吃满内存，所以报了这个错

业务原因：是因为excel中隐藏的单元格格式太大

### **hutool中的ListUtil.empty()以及MapUtil.empty();**

这两个返回的集合都是不能进行编辑的！

### **Hutool中的Holder**

在 Hutool 工具库中，`Holder` 是一个通用的容器对象，用于持有一个值。

`Holder` 类的主要用途是将一个值封装到一个可变的容器中，这样你就可以在方法之间传递这个容器，并在需要的时候改变容器中的值。这在 Java 中是有用的，因为 Java 只支持方法参数的值传递，而不支持引用传递。

以下是一个 `Holder` 的使用示例：

```java
import cn.hutool.core.lang.Holder;
 
public class HolderExample {
    public static void main(String[] args) {
        Holder<Integer> holder = Holder.of(1);
        System.out.println(holder.get()); // 输出 1
 
        changeValue(holder);
        System.out.println(holder.get()); // 输出 2
    }
 
    public static void changeValue(Holder<Integer> holder) {
        holder.set(2);
    }
 
    @Test
    public void test09() {
        Bill bill = new Bill();
        bill.setId(1L);
        bill = new Bill();
        List<Bill> bills = Lists.newArrayList();
        //报错，因为bill被改变了
        bills.stream().map(temp -> this.test10(bill));
    }
 
    @Test
    public void test11() {
        Bill bill = null;
        Holder<Bill> holder = new Holder<>(bill);
        if (Objects.isNull(bill)) {
            bill = new Bill();
            bill.setId(1L);
            holder.set(bill);
        }
        List<Bill> bills = Lists.newArrayList();
        //这样则不会报错
        bills.stream().map(temp -> this.test10(holder.get()));
    }
     
    public Bill test10(Bill bill){
        System.out.println(bill.getId());
        return bill;
    }
}
```

---

在这个例子中，我创建了一个 `Holder` 对象来持有一个 `Integer` 值。然后，我将这个 `Holder` 对象传递给 `changeValue` 方法，这个方法改变了 `Holder` 中的值。当我再次获取 `Holder` 中的值时，我得到的是新的值。这就是 `Holder` 的主要用途。

### **hutool中excelReader当使用bigdecimal类型接收时，对于单元格手动删除还是清除内容来说都会自动转化成0**

所以在解析金额类一般用string接收，然后在校验，避免0的二义性

```java
cn.hutool.core.convert.impl.NumberConverter#convert

cn.hutool.core.util.NumberUtil#toBigDecimal(java.lang.String)
```