# AI 模型训练与部署项目综合报告

> 生成时间: 2026-05-27
> 项目目录: /opt/uboss/yu.jiang & /opt/uboss/haojie.liu

---

## 目录

1. [项目总览](#项目总览)
2. [超参数详解](#超参数详解)
3. [训练命令详解](#训练命令详解)
4. [模型训练详情](#模型训练详情)
5. [模型部署详情](#模型部署详情)
6. [GPU资源分配](#gpu资源分配)
7. [数据集汇总](#数据集汇总)
8. [技术栈总览](#技术栈总览)

---

## 项目总览

### yu.jiang 项目

| 项目目录 | 核心功能 | 训练模型 | 部署方式 | GPU使用 |
|----------|----------|----------|----------|---------|
| ffdn | 图像篡改检测 | FFDN (ConvNeXtV2) | Docker | 4卡训练 |
| model-fine-tuning | 文档图像分类 | Qwen3.5-4B (LoRA) | SGLang/vLLM | 单卡训练 |
| ms-swift | 文档图像分类 | Qwen3.5-4B (LoRA) | ModelScope | 单卡训练 |
| paddle-kie | 关键信息抽取 | VI-LayoutXLM | - | GPU训练 |
| vllm | VLM推理服务 | Qwen3-VL-32B-FP8 | Docker | 2卡并行 |
| vllm-uv | VLM推理服务 | Qwen3.5-27B-FP8 | 本地 | 4卡并行 |
| paddle-ocr-vl-git | OCR-VL服务 | PaddleOCR-VL-1.5 | Docker | 多卡多实例 |
| ocr-gpu | OCR GPU服务 | PP-OCRv5 | Docker | 单卡 |
| ocr-onnx | OCR CPU服务 | PP-OCRv5 (ONNX) | Docker | CPU多线程 |

### haojie.liu 项目

| 项目目录 | 核心功能 | 训练模型 | 部署方式 | GPU使用 |
|----------|----------|----------|----------|---------|
| ms-swift/statement-classify | 银行流水分类 | Qwen2.5-VL-3B (LoRA) | HTTP API (8100) | GPU 6 |

---

## 超参数详解

### 一、LoRA 相关参数

| 参数 | 含义 | 调大影响 | 调小影响 | 推荐范围 |
|------|------|----------|----------|----------|
| `lora_rank` (r) | LoRA低秩分解的秩，决定适配器的容量。LoRA将权重更新分解为两个低秩矩阵 A×B，rank就是这两个矩阵的秩 | • 可训练参数增多，模型表达能力增强<br>• 显存占用增加<br>• 训练速度略降<br>• 可能过拟合 | • 参数效率更高，显存更省<br>• 表达能力受限<br>• 可能欠拟合 | 8-64，常用8/16/32 |
| `lora_alpha` | LoRA缩放因子，实际缩放比例为 alpha/rank。控制LoRA更新对原始权重的贡献程度 | • LoRA更新影响更大<br>• 学习速度加快<br>• 可能导致不稳定 | • LoRA更新影响更小<br>• 训练更保守<br>• 收敛可能变慢 | 通常设为rank的2倍，如rank=8时alpha=16或32 |
| `lora_dropout` | LoRA层的Dropout率，防止过拟合的正则化手段 | • 正则化更强<br>• 防止过拟合<br>• 可能欠拟合 | • 正则化更弱<br>• 可能过拟合<br>• 训练更充分 | 0.05-0.1，少样本时可适当增大 |
| `target_modules` | 指定哪些层应用LoRA。"all-linear"表示所有线性层 | • 更多层参与微调<br>• 表达能力更强<br>• 显存增加 | • 更少层参与微调<br>• 参数更少<br>• 可能欠拟合 | 常用"all-linear"或指定关键层如q_proj,v_proj |

**LoRA 参数选择建议**：

| 场景 | rank | alpha | 说明 |
|------|------|-------|------|
| 少样本微调 (<100) | 8-16 | 16-32 | 小秩防止过拟合 |
| 中等样本 (100-1000) | 16-32 | 32-64 | 平衡表达与效率 |
| 大规模微调 (>1000) | 32-64 | 64-128 | 大秩增强能力 |

---

### 二、学习率相关参数

| 参数 | 含义 | 调大影响 | 调小影响 | 推荐范围 |
|------|------|----------|----------|----------|
| `learning_rate` | 初始学习率，控制每次参数更新的步长 | • 收敛更快<br>• 可能跳过最优解<br>• 训练不稳定甚至发散 | • 收敛更慢<br>• 训练更稳定<br>• 可能陷入局部最优 | LoRA微调: 1e-4 ~ 5e-4<br>全量微调: 1e-5 ~ 1e-4 |
| `lr_scheduler_type` | 学习率调度策略，控制训练过程中学习率的变化方式 | - | - | cosine(余弦退火)最常用 |
| `warmup_ratio` / `warmup_steps` | 预热比例/步数，训练开始时学习率从0逐渐增加到设定值 | • 更长的稳定启动<br>• 避免初期震荡 | • 更快进入正常训练<br>• 初期可能不稳定 | 0.05-0.1 (比例) 或 100-500步 |

**学习率调度策略对比**：

| 调度器 | 特点 | 适用场景 |
|--------|------|----------|
| `cosine` | 余弦曲线衰减，平滑过渡 | 最常用，适合大多数场景 |
| `linear` | 线性衰减到0 | 简单任务 |
| `constant` | 保持不变 | 短训练或调试 |
| `polynomial` | 多项式衰减，power控制曲线形状 | FFDN等分割任务常用 |

---

### 三、批次与梯度相关参数

| 参数 | 含义 | 调大影响 | 调小影响 | 推荐范围 |
|------|------|----------|----------|----------|
| `per_device_train_batch_size` | 单卡批次大小，每次训练处理的样本数 | • 显存占用增加<br>• 梯度估计更准确<br>• 训练更稳定 | • 显存占用减少<br>• 梯度噪声更大<br>• 可能帮助泛化 | 根据显存调整，VLM常用1-4 |
| `gradient_accumulation_steps` | 梯度累积步数，累积多次梯度后更新一次参数 | • 等效batch更大<br>• 训练更稳定<br>• 速度略慢 | • 等效batch更小<br>• 更新更频繁 | 配合batch_size使等效batch=16/32/64 |
| **等效批次大小** | = batch_size × gradient_accumulation × gpu_num | • 梯度更准确<br>• 收敛更稳定<br>• 显存不变 | • 梯度噪声更大<br>• 可能帮助跳出局部最优 | 16-128 |

**显存与批次大小参考**：

| 模型 | 显存 | 推荐batch_size | 等效batch |
|------|------|----------------|-----------|
| Qwen2.5-VL-3B | 24GB | 4-8 | 16-32 |
| Qwen3.5-4B | 24GB | 1-2 | 8-16 |
| Qwen3-VL-32B | 80GB×2 | 1-2 | 8-16 |

---

### 四、训练轮次相关参数

| 参数 | 含义 | 调大影响 | 调小影响 | 推荐范围 |
|------|------|----------|----------|----------|
| `num_train_epochs` | 完整遍历数据集的次数 | • 训练更充分<br>• 可能过拟合<br>• 时间更长 | • 可能欠拟合<br>• 时间更短 | 少样本: 5-20<br>多样本: 2-5 |
| `max_steps` | 最大训练步数，与epochs二选一 | • 训练更久<br>• 可能过拟合 | • 可能欠拟合 | 根据数据量计算 |
| `max_length` | 最大序列长度，输入token的最大数量 | • 支持更长输入<br>• 显存占用增加 | • 长文本被截断<br>• 显存更省 | 2048-8192，VLM常用2048 |

---

### 五、精度与显存优化参数

| 参数 | 含义 | 启用影响 | 禁用影响 | 推荐设置 |
|------|------|----------|----------|----------|
| `torch_dtype` | 张量数据类型，bf16/fp16/fp32 | bf16: 显存减半，速度提升，精度损失小 | fp32: 精度最高，显存最大，速度最慢 | bf16 (推荐) |
| `gradient_checkpointing` | 梯度检查点，用计算换显存 | • 显存大幅减少(30-50%)<br>• 计算时间增加约20% | • 显存占用大<br>• 计算更快 | 显存紧张时启用 |
| `flash_attn` | Flash Attention，优化的注意力计算 | • 速度提升2-4倍<br>• 显存减少<br>• 需要特定硬件支持 | • 标准注意力计算 | 支持时启用 |

**精度选择建议**：

| 精度 | 显存占用 | 速度 | 精度损失 | 适用场景 |
|------|----------|------|----------|----------|
| fp32 | 100% | 慢 | 无 | 调试、精度敏感任务 |
| fp16 | 50% | 快 | 较大 | 老硬件 |
| bf16 | 50% | 快 | 小 | **推荐**，需要Ampere+架构 |

---

### 六、优化器相关参数

| 参数 | 含义 | 调大影响 | 调小影响 | 推荐值 |
|------|------|----------|----------|--------|
| `weight_decay` | L2正则化系数，防止过拟合 | • 正则化更强<br>• 权重更小<br>• 可能欠拟合 | • 正则化更弱<br>• 可能过拟合 | 0.01-0.1 |
| `adam_beta1` | Adam一阶矩估计的衰减率 | • 动量更持久<br>• 更平滑 | • 动量更短 | 0.9 |
| `adam_beta2` | Adam二阶矩估计的衰减率 | • 方差估计更平滑 | • 方差估计更敏感 | 0.95-0.999 |
| `max_grad_norm` | 梯度裁剪阈值，防止梯度爆炸 | • 允许更大梯度<br>• 可能不稳定 | • 梯度被裁剪更多<br>• 训练更稳定 | 1.0 |

---

### 七、评估与保存参数

| 参数 | 含义 | 调大影响 | 调小影响 | 推荐值 |
|------|------|----------|----------|--------|
| `eval_steps` | 每隔多少步评估一次 | • 评估更频繁<br>• 及时发现问题<br>• 时间开销增加 | • 评估更少<br>• 训练更快 | 50-500 |
| `save_steps` | 每隔多少步保存checkpoint | • 保存更频繁<br>• 占用更多磁盘 | • 保存更少<br>• 可能丢失好模型 | 100-1000 |
| `save_total_limit` | 保留的checkpoint数量 | • 保留更多模型<br>• 磁盘占用增加 | • 保留更少<br>• 节省磁盘 | 2-5 |

---

### 八、冻结策略参数

| 参数 | 含义 | 启用影响 | 禁用影响 | 推荐设置 |
|------|------|----------|----------|----------|
| `freeze_vit` | 冻结视觉编码器(ViT) | • 只训练语言模型<br>• 显存减少<br>• 视觉能力不变 | • 全模型训练<br>• 显存增加 | VLM微调常用true |
| `freeze_aligner` | 冻结对齐层(连接视觉和语言) | • 对齐层不变<br>• 训练更稳定 | • 对齐层参与训练 | 常用true |
| `freeze_llm` | 冻结语言模型 | • 只训练其他部分<br>• 语言能力不变 | • 语言模型参与训练 | 根据任务需要 |

---

## 训练命令详解

### 一、ms-swift 训练命令

```bash
swift sft \
  --model Qwen/Qwen3.5-4B \
  --tuner_type lora \
  --dataset "train.jsonl" \
  --val_dataset "val.jsonl" \
  --torch_dtype bfloat16 \
  --per_device_train_batch_size 1 \
  --learning_rate 1e-4 \
  --lora_rank 16 \
  --lora_alpha 32 \
  --target_modules all-linear \
  --num_train_epochs 2 \
  --max_length 2048
```

#### 命令参数详解

| 参数 | 含义 | 示例值说明 |
|------|------|------------|
| `swift sft` | ms-swift的有监督微调(Supervised Fine-Tuning)子命令 | 执行SFT训练流程 |
| `--model` | 指定基座模型，从ModelScope/HuggingFace下载 | Qwen/Qwen3.5-4B表示ModelScope上的模型ID |
| `--tuner_type` | 微调器类型 | lora/qlora/dora/full，lora最常用 |
| `--dataset` | 训练数据集路径 | JSONL格式文件 |
| `--val_dataset` | 验证数据集路径 | 用于评估和early stopping |
| `--torch_dtype` | 张量数据类型 | bfloat16混合精度训练 |
| `--per_device_train_batch_size` | 单GPU批次大小 | 1表示每卡每次处理1个样本 |
| `--learning_rate` | 初始学习率 | 1e-4 = 0.0001 |
| `--lora_rank` | LoRA秩 | 16，决定适配器容量 |
| `--lora_alpha` | LoRA缩放因子 | 32，实际缩放=32/16=2 |
| `--target_modules` | 应用LoRA的模块 | all-linear表示所有线性层 |
| `--num_train_epochs` | 训练轮数 | 2表示遍历数据集2次 |
| `--max_length` | 最大序列长度 | 2048 tokens |

#### 其他常用参数

| 参数 | 含义 | 示例 |
|------|------|------|
| `--gradient_accumulation_steps` | 梯度累积步数 | 4 |
| `--warmup_ratio` | 预热比例 | 0.05 |
| `--lr_scheduler_type` | 学习率调度器 | cosine |
| `--weight_decay` | 权重衰减 | 0.1 |
| `--save_steps` | 保存间隔 | 50 |
| `--eval_steps` | 评估间隔 | 50 |
| `--logging_steps` | 日志间隔 | 10 |
| `--output_dir` | 输出目录 | ./output |
| `--split_dataset_ratio` | 验证集比例 | 0.1 |

---

### 二、ms-swift 部署命令

```bash
swift deploy \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --adapters output/v3-20260519-201808/checkpoint-70 \
  --port 8100
```

| 参数 | 含义 |
|------|------|
| `swift deploy` | 启动模型服务，提供OpenAI兼容API |
| `--model` | 基座模型 |
| `--adapters` | LoRA适配器路径，会自动合并到基座模型 |
| `--port` | 服务端口 |
| `--host` | 服务地址，默认0.0.0.0 |

---

### 三、vLLM 推理命令

```bash
vllm serve Qwen/Qwen3-VL-32B-Instruct-FP8 \
  --quantization fp8 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --tensor-parallel-size 2
```

| 参数 | 含义 | 调优建议 |
|------|------|----------|
| `vllm serve` | 启动vLLM推理服务 | - |
| `--quantization` | 量化方式 | fp8/int8/awq/gptq，fp8精度损失最小 |
| `--max-model-len` | 最大上下文长度 | 根据需求设置，越长显存越大 |
| `--gpu-memory-utilization` | GPU显存利用率 | 0.85-0.95，留余量防止OOM |
| `--tensor-parallel-size` | 张量并行GPU数 | 多卡分割模型，需GPU间高速互联 |
| `--dtype` | 数据类型 | auto/bfloat16/float16 |
| `--max-num-seqs` | 最大并发序列数 | 批处理大小，影响吞吐 |

---

### 四、分布式训练命令

```bash
# PyTorch DDP
torchrun --nproc_per_node=4 train.py

# 或使用 accelerate
accelerate launch --num_processes 4 train.py
```

| 参数 | 含义 |
|------|------|
| `--nproc_per_node` | 单节点GPU数量 |
| `--nnodes` | 节点数量(多机训练) |
| `--node_rank` | 当前节点编号 |
| `--master_addr` | 主节点地址 |
| `--master_port` | 通信端口 |

---

### 五、环境变量详解

```bash
export CUDA_VISIBLE_DEVICES=6
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export MODELSCOPE_CACHE=/path/to/cache
```

| 变量 | 含义 | 设置建议 |
|------|------|----------|
| `CUDA_VISIBLE_DEVICES` | 可见的GPU设备ID | 指定使用的GPU，如"0,1"或"6" |
| `PYTORCH_CUDA_ALLOC_CONF` | CUDA内存分配配置 | expandable_segments:True减少碎片 |
| `MODELSCOPE_CACHE` | ModelScope模型缓存目录 | 指定到高速存储 |
| `HF_HOME` | HuggingFace缓存目录 | 同上 |
| `IMAGE_MAX_TOKEN_NUM` | 图像最大token数 | VLM专用，影响图像编码长度 |
| `VIDEO_MAX_TOKEN_NUM` | 视频最大token数 | VLM专用 |
| `OMP_NUM_THREADS` | OpenMP线程数 | CPU推理时设置为核心数 |

---

### 六、MMSegmentation 训练命令 (FFDN)

```bash
python tools/train.py configs/FFDN/FFDN.py \
  --work-dir work_dirs/FFDN \
  --amp
```

| 参数 | 含义 |
|------|------|
| `tools/train.py` | MMSeg训练脚本 |
| `configs/...` | 配置文件路径 |
| `--work-dir` | 工作目录，保存checkpoints |
| `--amp` | 启用自动混合精度 |
| `--resume` | 从checkpoint恢复训练 |
| `--cfg-options` | 命令行覆盖配置项 |

---

### 七、PaddleOCR 训练命令

```bash
python tools/train.py \
  -c configs/kie/vi_layoutxlm/ser_vi_layoutxlm_xfund_zh.yml \
  -o Global.epoch_num=200 \
     Global.learning_rate=0.00005
```

| 参数 | 含义 |
|------|------|
| `-c` | 配置文件路径 |
| `-o` | 覆盖配置项，格式为 key=value |

---

## 模型训练详情

### 1. FFDN - 图像篡改检测 (yu.jiang)

#### 1.1 模型信息

| 属性 | 详情 |
|------|------|
| **模型名称** | FFDN (Feature Fusion and Decomposition Network) |
| **论文来源** | ECCV 2024 |
| **任务类型** | 图像篡改检测 / 语义分割 |
| **骨干网络** | ConvNeXtV2-Base (ImageNet-22k预训练) |
| **模型大小** | 1.6 GB |
| **类别数** | 2类 (未篡改/篡改区域) |

#### 1.2 训练框架

| 组件 | 框架/版本 |
|------|-----------|
| 深度学习框架 | PyTorch 2.0.1+cu118 |
| 分割框架 | MMSegmentation (自定义版) |
| 训练引擎 | MMEngine 0.7.4 |
| 视觉模型库 | timm 0.9.12 |
| 分布式训练 | PyTorch DDP (NCCL) |

#### 1.3 超参数配置与详解

```python
# 训练参数
iters = 100000              # 总迭代次数：10万次迭代
batch_size = 4              # 批量大小：每卡处理4张512x512图像
learning_rate = 1e-4        # 学习率：0.0001，分割任务常用值
weight_decay = 0.05         # 权重衰减：L2正则化，防止过拟合
val_interval = 500          # 验证间隔：每500步评估一次

# 图像尺寸
size = 512                  # 输入尺寸：512×512，平衡精度与显存

# 学习率调度
lr_scheduler = 'PolyLR'     # 多项式衰减：power=0.9平滑下降
power = 0.9                 # 衰减指数：越大衰减越慢
```

#### 1.4 优化策略

| 优化技术 | 配置 | 作用说明 |
|----------|------|----------|
| 优化器 | AdamW | Adam + 权重衰减解耦，训练更稳定 |
| 混合精度 | AMP | 自动混合精度，显存减半，速度提升 |
| 损失函数 | CrossEntropy + LovaszLoss | CE处理像素分类，Lovasz优化IoU |
| 数据增强 | 翻转/灰度/旋转/JPEG压缩 | 增强模型鲁棒性，防止过拟合 |
| OHEM | thresh=0.9 | 困难样本挖掘，关注难分类像素 |
| SyncBN | 多卡同步 | 跨卡统计BN，小batch时更稳定 |

#### 1.5 GPU部署

| 配置项 | 信息 |
|--------|------|
| GPU类型 | NVIDIA GPU (CUDA 11.8+) |
| 训练GPU数 | 4卡并行 |
| 推理GPU | 单卡 (cuda:0) |
| 显存需求 | 训练约10-15GB/卡，推理约3-5GB |

#### 1.6 样本数据

| 数据集 | 样本数 | 用途 |
|--------|--------|------|
| 训练集 | 120,000 | 模型训练 |
| 验证集 | 30,000 | 模型验证 |
| FCD测试集 | 2,000 | 快速压缩检测 |
| SCD测试集 | 18,000 | 慢速压缩检测 |

---

### 2. Qwen3.5-4B - 文档图像分类微调 (yu.jiang)

#### 2.1 模型信息

| 属性 | 详情 |
|------|------|
| **模型名称** | Qwen/Qwen3.5-4B |
| **模型类型** | 多模态视觉语言模型 (VLM) |
| **参数量** | 45.7亿 (4.57B) |
| **微调方式** | LoRA (参数高效微调) |
| **任务类型** | 文档图像分类 (13类) |

#### 2.2 分类类别

```
流水_个人、流水_对公、医疗_出院小结、医疗_病历、医疗_处方笺、
医疗_门诊发票、医疗_费用明细、医疗_住院发票、医疗_报告单、
医疗_医保结算单、医疗_入院记录、医疗_诊断证明、其他
```

#### 2.3 训练脚本详解

```bash
swift sft \
  --model Qwen/Qwen3.5-4B \           # 使用Qwen3.5-4B作为基座模型
  --tuner_type lora \                  # LoRA微调，参数高效
  --dataset "train.jsonl" \            # 训练数据
  --val_dataset "val.jsonl" \          # 验证数据
  --torch_dtype bfloat16 \             # BF16混合精度
  --per_device_train_batch_size 1 \    # 单卡batch=1
  --learning_rate 1e-4 \               # 学习率1e-4
  --lora_rank 16 \                     # LoRA秩=16
  --lora_alpha 32 \                    # LoRA alpha=32，缩放因子=2
  --target_modules all-linear \        # 所有线性层应用LoRA
  --num_train_epochs 2 \               # 训练2个epoch
  --max_length 2048 \                  # 最大序列长度2048
  --enable_thinking false              # 禁用思维链
```

#### 2.4 超参数配置

| 参数类别 | 参数名称 | 配置值 | 选择原因 |
|----------|----------|--------|----------|
| **LoRA配置** | lora_rank | 16 | 13类分类任务，需要一定表达能力 |
| | lora_alpha | 32 | 标准设置，缩放因子=2 |
| | lora_dropout | 0.05 | 轻正则化 |
| | target_modules | all-linear | 全量微调线性层 |
| **训练参数** | learning_rate | 1e-4 | LoRA微调标准学习率 |
| | num_train_epochs | 2 | 数据量适中，2轮足够 |
| | batch_size | 1 | VLM显存限制 |
| | warmup_ratio | 0.05 | 5%预热 |
| | lr_scheduler | cosine | 平滑衰减 |
| | weight_decay | 0.1 | L2正则化 |
| **精度配置** | torch_dtype | bfloat16 | 显存优化 |
| | gradient_checkpointing | true | 进一步节省显存 |

#### 2.5 性能评估

| 检查点 | Epoch | 训练Loss | 验证Loss | Token准确率 |
|--------|-------|----------|----------|-------------|
| checkpoint-50 | 0.96 | 0.0557 | **0.0102** | **100%** |
| checkpoint-100 | 1.92 | 0.0878 | 0.0255 | 98.43% |
| Final | 2.0 | 0.1155 | 0.0255 | 98.43% |

#### 2.6 样本数据

| 数据集 | 样本数 | 图片数 |
|--------|--------|--------|
| 训练集 | 864条 | 865张 |
| 验证集 | 97条 | 98张 |

---

### 3. Qwen2.5-VL-3B - 银行流水分类微调 (haojie.liu)

#### 3.1 模型信息

| 属性 | 详情 |
|------|------|
| **模型名称** | Qwen/Qwen2.5-VL-3B-Instruct |
| **模型类型** | 视觉语言模型 (VLM) |
| **参数规模** | 3B (30亿参数) |
| **微调方式** | LoRA |
| **任务类型** | 银行流水文档图像分类 |

#### 3.2 分类类别

| 代码 | 类别 | 说明 |
|------|------|------|
| 0 | 其他 | 非流水类文档 |
| 203 | 个人流水 | 个人银行流水 |
| 204 | 对公流水 | 企业/对公银行流水 |

#### 3.3 训练脚本详解

```bash
#!/bin/bash

# 环境变量配置
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True  # CUDA内存碎片优化
export IMAGE_MAX_TOKEN_NUM=512                           # 图像编码最大token数
export VIDEO_MAX_TOKEN_NUM=128                           # 视频编码最大token数
export FPS_MAX_FRAMES=16                                 # 视频最大帧数
export MODELSCOPE_CACHE=/opt/uboss/haojie.liu/modelscope # 模型缓存路径

DATA_JSONL=data/train.jsonl

# 训练命令
CUDA_VISIBLE_DEVICES=6 swift sft \       # 使用GPU 6
  --model Qwen/Qwen2.5-VL-3B-Instruct \  # 3B参数的VLM
  --tuner_type lora \                     # LoRA微调
  --dataset "$DATA_JSONL" \               # 训练数据
  --split_dataset_ratio 0.1 \             # 10%作为验证集
  --torch_dtype bfloat16 \                # BF16混合精度
  --per_device_train_batch_size 1 \       # 单卡batch=1
  --gradient_accumulation_steps 4 \       # 梯度累积4步，等效batch=4
  --learning_rate 1e-4 \                  # 学习率1e-4
  --lora_rank 8 \                         # LoRA秩=8，少样本用小秩
  --lora_alpha 32 \                       # LoRA alpha=32，缩放因子=4
  --lora_dropout 0.05 \                   # Dropout=0.05
  --target_modules all-linear \           # 所有线性层
  --num_train_epochs 10 \                 # 10个epoch，少样本需要多轮
  --max_length 2048 \                     # 最大序列长度
  --save_steps 50 \                       # 每50步保存
  --logging_steps 1 \                     # 每步记录日志
  --eval_steps 50                         # 每50步评估
```

#### 3.4 超参数配置

| 参数类别 | 参数名称 | 配置值 | 选择原因 |
|----------|----------|--------|----------|
| **LoRA配置** | lora_rank | 8 | 少样本(29条)，小秩防止过拟合 |
| | lora_alpha | 32 | 缩放因子=4，较大缩放加速收敛 |
| | lora_dropout | 0.05 | 轻正则化 |
| **训练参数** | learning_rate | 1e-4 | 标准LoRA学习率 |
| | num_train_epochs | 10 | 少样本需要多轮训练 |
| | batch_size | 1 | 显存限制 |
| | gradient_accumulation | 4 | 等效batch=4 |
| | effective_batch_size | 4 | 小批量适合少样本 |
| **精度配置** | torch_dtype | bfloat16 | 显存优化 |
| | gradient_checkpointing | true | 节省显存 |

#### 3.5 性能评估

**训练过程**:

| Step | Loss | Token Acc | Learning Rate |
|------|------|-----------|---------------|
| 1 | 0.475 | 85% | 2.5e-05 |
| 10 | 0.151 | 88.4% | 9.80e-05 |
| 30 | 0.007 | 100% | 6.64e-05 |
| 50 | 3.76e-05 | 100% | 2.10e-05 |
| 70 | 3.08e-05 | 100% | 0 |

**测试结果**:

| 类别 | 测试样本数 | 准确率 |
|------|-----------|--------|
| 对公流水 (204) | 54张 | **94.44%** |
| 个人流水 (203) | 56张 | **96.43%** |
| **综合** | 110张 | **95.45%** |

#### 3.6 样本数据

| 属性 | 值 |
|------|-----|
| 总训练样本 | 29条 JSONL记录 |
| 训练图片 | 149张 |

---

### 4. VI-LayoutXLM - 关键信息抽取 (yu.jiang)

#### 4.1 模型信息

| 属性 | 详情 |
|------|------|
| **模型名称** | VI-LayoutXLM |
| **模型类型** | 多模态预训练模型 |
| **任务类型** | KIE (关键信息抽取) |
| **子任务** | SER (语义实体识别) / RE (关系抽取) |

#### 4.2 超参数配置

```yaml
# SER训练配置
Global:
  epoch_num: 200              # 200轮训练
  learning_rate: 0.00005      # 学习率5e-5
  optimizer: AdamW            # AdamW优化器
  warmup_epoch: 2             # 2轮预热
  batch_size: 32              # 批次大小32

Architecture:
  algorithm: "LayoutXLM"      # LayoutXLM算法
  mode: "vi"                  # 视觉无关模式，移除视觉backbone
  num_classes: 7              # 7个实体类别
```

#### 4.3 优化策略

| 优化技术 | 说明 |
|----------|------|
| 视觉无关模式 | 移除Visual backbone，提速不减精度 |
| 知识蒸馏 | UDML知识蒸馏策略 |

#### 4.4 性能评估

| 模型 | 任务 | Hmean |
|------|------|-------|
| VI-LayoutXLM | SER | **93.19%** |
| VI-LayoutXLM | RE | **83.92%** |

---

## 模型部署详情

### 1. vLLM 推理服务

#### 1.1 vllm (Qwen3-VL-32B) - yu.jiang

```yaml
# Docker配置
image: vllm/vllm-openai:v0.10.2
environment:
  - NVIDIA_VISIBLE_DEVICES=3,4    # 使用GPU 3和4
  - CUDA_VISIBLE_DEVICES=0,1      # 容器内映射为0和1
command:
  - --model Qwen3-VL-32B-Instruct-FP8
  - --quantization fp8            # FP8量化
  - --max-model-len 8192          # 最大上下文8K
  - --gpu-memory-utilization 0.90 # 90%显存利用率
  - --tensor-parallel-size 2      # 2卡张量并行
```

| 参数 | 含义 | 设置原因 |
|------|------|----------|
| `--quantization fp8` | FP8量化 | 32B模型量化后显存减半 |
| `--tensor-parallel-size 2` | 2卡并行 | 32B模型需要2卡分割 |
| `--gpu-memory-utilization 0.90` | 显存利用率 | 留10%余量防OOM |

#### 1.2 vllm-uv (Qwen3.5-27B) - yu.jiang

| 配置项 | 详情 |
|--------|------|
| **模型** | Qwen/Qwen3.5-27B-FP8 |
| **框架** | vLLM v0.18.0 |
| **GPU配置** | 4卡并行 (tensor-parallel-size=4) |
| **最大序列长度** | 262,144 |

---

### 2. OCR 服务部署

#### 2.1 ocr-gpu (GPU版本)

```python
det_threshold = 0.3      # 检测阈值：低于此值的文本框被过滤
box_threshold = 0.6      # 文本框置信度阈值
unclip_ratio = 1.5       # 文本框扩展比例：扩大检测框以包含完整文字
batch_size = 6           # 批处理大小
max_side_len = 4000      # 图像最大边长：超过会缩放
```

#### 2.2 ocr-onnx (CPU版本)

```yaml
OMP_NUM_THREADS: 16              # OpenMP线程数=CPU核心数
MKL_NUM_THREADS: 16              # MKL数学库线程数
intra_op_num_threads: 16         # 算子内并行线程数
inter_op_num_threads: 16         # 算子间并行线程数
GraphOptimizationLevel: ORT_ENABLE_ALL  # 启用所有图优化
```

---

### 3. VLM 服务部署 (haojie.liu)

```bash
# 启动脚本 vlm_start.sh
CUDA_VISIBLE_DEVICES=6 swift deploy \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --adapters output/v3-20260519-201808/checkpoint-70 \
  --port 8100
```

| 参数 | 含义 |
|------|------|
| `swift deploy` | 启动OpenAI兼容API服务 |
| `--adapters` | LoRA适配器路径，自动合并到基座模型 |
| `--port 8100` | 服务监听端口 |

---

## GPU资源分配

### 总体分配表

| GPU ID | 项目 | 用户 | 模型/服务 |
|--------|------|------|-----------|
| GPU 0 | paddle-ocr-vl-git | yu.jiang | PaddleOCR-VL-1.5 |
| GPU 2 | paddle-ocr-vl-git | yu.jiang | PaddleOCR-VL-1.5 |
| GPU 3-4 | vllm | yu.jiang | Qwen3-VL-32B (2卡并行) |
| GPU 4 | alfred/image-correct | yu.jiang | 文档预处理 |
| GPU 6 | ms-swift | haojie.liu | Qwen2.5-VL-3B 推理 |
| GPU 7 | model-fine-tuning | yu.jiang | Qwen3.5-4B 训练 |

### 多卡配置示例

```bash
# 单卡训练
CUDA_VISIBLE_DEVICES=7 swift sft ...

# 多卡张量并行 (vLLM)
--tensor-parallel-size 2

# 多卡数据并行 (DDP)
torchrun --nproc_per_node=4 train.py
```

---

## 数据集汇总

### 训练数据集

| 数据集 | 规模 | 用户 | 用途 | 格式 |
|--------|------|------|------|------|
| DocTamperV1 | 173,000 | yu.jiang | 篡改检测 | LMDB |
| 文档分类数据 | 961条 | yu.jiang | Qwen3.5微调 | JSONL |
| 银行流水分类 | 29条 | haojie.liu | Qwen2.5-VL微调 | JSONL |
| XFUND | 中文表单 | yu.jiang | KIE训练 | 标注文件 |

### 数据格式示例

**JSONL格式 (VLM微调)**:
```json
{
  "images": ["images/1.jpg"],
  "messages": [
    {"role": "system", "content": "你是文档图像分类助手..."},
    {"role": "user", "content": "<image>"},
    {"role": "assistant", "content": "203"}
  ]
}
```

| 字段 | 含义 |
|------|------|
| `images` | 图片路径列表 |
| `messages` | 对话消息列表 |
| `role` | 角色：system/user/assistant |
| `content` | 内容，`<image>`是图片占位符 |

---

## 技术栈总览

### 深度学习框架

| 框架 | 版本 | 用途 | 特点 |
|------|------|------|------|
| PyTorch | 2.0.1+ / 2.6.0+ | 通用深度学习 | 动态图，生态丰富 |
| PaddlePaddle | 2.6.2 / 3.x | OCR/KIE任务 | 百度飞桨，中文友好 |
| MMSegmentation | 自定义 | 语义分割 | OpenMMLab生态 |

### 训练/微调框架

| 框架 | 版本 | 用途 | 特点 |
|------|------|------|------|
| ms-swift | 4.2.1 | LLM/VLM微调 | ModelScope官方，支持多种tuner |
| PEFT | 0.19.1 | 参数高效微调 | HuggingFace，LoRA/QLoRA等 |
| MMEngine | 0.7.4 | 训练引擎 | OpenMMLab统一引擎 |

### 推理框架

| 框架 | 版本 | 用途 | 特点 |
|------|------|------|------|
| vLLM | 0.10.2 / 0.18.0 | LLM/VLM推理 | 高吞吐，PagedAttention |
| SGLang | - | LLM推理 | 灵活解码 |
| ONNX Runtime | - | CPU推理优化 | 跨平台，高性能 |
| TensorRT | 7.2.3.4 | GPU推理加速 | NVIDIA官方，极致性能 |

---

## 附录：快速参考

### 常用超参数推荐值

| 参数 | 少样本 (<100) | 中等样本 (100-1000) | 大样本 (>1000) |
|------|---------------|---------------------|----------------|
| lora_rank | 8 | 16 | 32-64 |
| learning_rate | 1e-4 | 1e-4 | 5e-5 |
| num_train_epochs | 10-20 | 5-10 | 2-5 |
| batch_size | 1-2 | 2-4 | 4-8 |
| warmup_ratio | 0.05 | 0.05 | 0.1 |

### 显存估算

| 模型 | FP32 | BF16 | LoRA (rank=16) |
|------|------|------|----------------|
| 3B | ~12GB | ~6GB | ~7GB |
| 4B | ~16GB | ~8GB | ~9GB |
| 7B | ~28GB | ~14GB | ~15GB |
| 27B | ~108GB | ~54GB | ~55GB |

### 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| OOM (显存不足) | batch_size太大 | 减小batch_size，启用gradient_checkpointing |
| 训练不收敛 | 学习率太大 | 减小learning_rate，增加warmup |
| 过拟合 | 数据太少/训练太久 | 增加dropout，减少epochs，数据增强 |
| 欠拟合 | 模型容量不足 | 增大lora_rank，减少冻结层 |

---

> 报告完成
