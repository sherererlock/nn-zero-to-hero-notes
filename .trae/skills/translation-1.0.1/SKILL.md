---
name: translation
description: 将本仓库 (nn-zero-to-hero-notes) 的 .md 或 .ipynb 技术笔记翻译为简体中文，输出到 translation/zh/ 镜像目录，图片同步拷贝。触发词：翻译、中文化、translate、.md、.ipynb、Karpathy 笔记。
metadata:
  version: 1.0.1
---

# 技术笔记汉化工作指令

本 skill 面向 **Andrej Karpathy *neural networks: zero to hero*** 系列学习笔记仓库。
每次调用处理**一个**源文件，产出结构完整的中文译文，落盘到 `translation/zh/` 镜像目录。

**首次调用**时，先用一句话说明你要做什么，然后执行；**后续调用**直接执行。

---

## 1. Inputs

用户调用时**必须提供**：

- **源文件路径**：相对仓库根目录，例如：
  - `N001 - Building Micrograd/N001 - Micrograd.ipynb`
  - `G001 - Deep Dive into LLMs/G001 - Deep Dive into LLMs.md`
  - `T001 - State of GPT/T001 - State_of_GPT - Notes.md`
  - `README.md`

---

## 2. Output Path 镜像规则

| 源路径 | 目标路径 |
|--------|----------|
| `README.md` | `translation/zh/README.md` |
| `G001 - .../G001 - ....md` | `translation/zh/G001 - .../G001 - ....md` |
| `N001 - .../N001 - Micrograd.ipynb` | `translation/zh/N001 - .../N001 - Micrograd.ipynb` |
| `N001 - .../img/foo.png` | `translation/zh/N001 - .../img/foo.png` |

规则：**目录名称、文件名完全保持不变**，仅在路径前加 `translation/zh/`。

---

## 3. Translation Rules（翻译规则）

### 3.1 语气与受众

- 目标语言：**简体中文**
- 受众：深度学习从业者、研究生等技术人员
- 风格：**技术写作风格**，准确、简练，避免口语化
- 保留 Karpathy 的第一人称叙述语气（"我们来看…"、"注意…"）
- 不添加原文没有的内容；不省略原文任何段落

### 3.2 标题翻译规则

**标题只写中文，不加英文括注**。这样 TOC 锚点链接可以正常工作。

```
原文：## Understanding Derivatives
✅ 译文：## 理解导数
❌ 错误：## 理解导数 (Understanding Derivatives)
```

若原文标题本身包含英文专有名词（如模型名、库名），保留英文：
```
原文：## Back to Neural Networks using PyTorch
✅ 译文：## 用 PyTorch 回到神经网络
```

**TOC（目录）锚点**：翻译后同步更新锚点，使其指向新的中文标题 slug。
GitHub slug 规则：中文字符保留，空格转 `-`，大写转小写，去掉标点符号。

```
标题 ## 理解导数   →  锚点 #理解导数
标题 ## Value 类 - 设置  →  锚点 #value-类---设置
```

### 3.3 术语策略

**段落正文、列表、说明文字**中，术语**首次出现**时用「中文 (English)」格式；**同一文档后续段落**仅用中文。

参考术语表（见第 7 节），常见术语处理示例：
- 首次：「梯度下降 (gradient descent)」
- 后续：「梯度下降」

### 3.3 数学公式

- `$...$`（行内）与 `$$...$$`（块级）内的 LaTeX **逐字原样保留**，不得修改
- 变量名、函数名（如 `\frac`, `\sigma`, `x_i`）**不翻译**
- 公式**后面**的文字解释正常翻译

```
原文：The loss is $L = -\sum_i y_i \log \hat{y}_i$, where $y_i$ is the label.
译文：损失函数 (loss) 为 $L = -\sum_i y_i \log \hat{y}_i$，其中 $y_i$ 为标签。
```

### 3.4 代码块（Markdown 文件中的 fenced code block）

` ```python `、` ```bash `、` ```text ` 等代码块**完全保留**，包括：
- 代码本身（变量名、函数名、字符串）
- 代码内的英文注释（`# comment`）
- 语言标签（不得改成 ` ```python代码 `）

### 3.5 Jupyter Notebook 处理规则

.ipynb 是 JSON 文件，包含多种 cell：

| Cell 类型 | 处理方式 |
|-----------|----------|
| `"cell_type": "markdown"` | 翻译 `source` 字段（遵循 3.2、3.4 等规则） |
| `"cell_type": "code"` | **source 与 outputs 原样保留，不动** |
| `metadata`、`kernelspec`、`id`、`execution_count` | **原样保留，不动** |

输出的 .ipynb 必须是合法 JSON，可被 Jupyter 正常打开。

### 3.6 图片

- HTML 写法：`<img src="img/foo.png" alt="说明" ...>`
  - `src` 属性值**原样保留**（路径不变）
  - `alt` 文本翻译为中文
  - 其他属性（`width`、`style` 等）原样保留
- Markdown 写法：`![alt text](img/foo.png)`
  - 括号内路径**原样保留**
  - `alt text` 翻译为中文
- **远程图片**（`http://` / `https://`）：保持 URL 不变，不拷贝
- **本地图片**（`img/xxx.png` 等相对路径）：路径保留，文件**必须**拷贝（见第 4 节 Step 5）

### 3.7 HTML 结构

`<table>`、`<a>`、`<br>`、`<b>`、`<i>`、`<p>`、`<div>` 等标签：
- **标签结构原样保留**
- `href`、`src`、`class`、`style` 等**属性不动**
- **标签之间的文本内容**翻译

```html
<!-- 原文 -->
<a href="https://example.com"><b>Click here</b> to learn more.</a>
<!-- 译文 -->
<a href="https://example.com"><b>点击此处</b>了解更多。</a>
```

### 3.8 GitHub Callouts

`> [!NOTE]`、`> [!WARNING]`、`> [!TIP]`、`> [!IMPORTANT]` 关键字**保持英文**，内容翻译：

```markdown
> [!NOTE]
> This is important.
```
译为：
```markdown
> [!NOTE]
> 这一点很重要。
```

### 3.9 锚点链接

文档内部 TOC 链接 `[链接文字](#anchor-id)` 的处理：

1. **链接文字**翻译为中文。
2. **锚点 id 必须同步更新**为新中文标题的 GitHub slug（因为标题已翻译，原 id 已失效）。

GitHub slug 生成规则（适用于中文标题）：
- 中文字符保留
- 英文字母转小写
- 空格转 `-`
- 去掉标点符号（`？`、`！`、`()`、`.` 等）

```
标题 ## 理解导数           → #理解导数
标题 ## Value 类 - 设置    → #value-类---设置
标题 ## 什么是 Micrograd？ → #什么是-micrograd
```

指向**文档外部**的链接（`href` 含 `http` 或指向其他文件）：`href` 原样不动，链接文字翻译。

---

## 4. Workflow（执行步骤）

**按以下顺序执行，不得跳过：**

1. **校验源文件**：确认源文件存在；若目标路径已有译文，询问用户是否覆盖。

2. **拷贝本地图片**：在仓库根目录运行内置脚本，自动扫描并拷贝所有本地图片：

   ```bash
   python .trae/skills/translation-1.0.1/copy_images.py "<源文件相对路径>"
   ```

   示例：
   ```bash
   python .trae/skills/translation-1.0.1/copy_images.py \
       "N001 - Building Micrograd/N001 - Micrograd.ipynb"
   python .trae/skills/translation-1.0.1/copy_images.py \
       "G001 - Deep Dive into LLMs/G001 - Deep Dive into LLMs.md"
   ```

   脚本自动处理：
   - 扫描 `.md` 的全文 / `.ipynb` 的所有 markdown cell
   - 提取 `<img src="...">` 和 `![](...)` 中的本地图片路径（自动排除远程 URL）
   - 创建 `translation/zh/<原目录>/img/` 目录
   - `shutil.copy2` 逐一拷贝，保持文件名
   - 打印拷贝摘要与缺失文件警告

3. **读取源文件**：读取全部内容（.ipynb 按 JSON 解析；.md 按纯文本读取）。

4. **翻译内容并直接写入**：

   > ⚠️ **严禁**创建任何临时辅助脚本（`.py`、`.sh` 等）来处理翻译或写文件。必须直接使用文件写入工具输出译文。

   - **.md 文件**：整体翻译后，直接用文件写入工具写入目标路径，一次完成。
   - **.ipynb 文件（分批策略）**：notebook 可能有数十个 markdown cell，内容量大。**按 `##` 级别章节分批翻译**，避免单次输出过长：
     1. 读取完整 .ipynb JSON
     2. 以 `##` 标题 cell 为边界，识别各章节范围
     3. 逐章节翻译其内部所有 markdown cell
     4. 所有章节翻译完毕后，将完整 notebook JSON 用文件写入工具**一次性写入**目标路径（indent=1，ensure_ascii=False）
     5. 不得将中间结果写入任何临时文件

6. **输出摘要**：
   ```
   ✅ 译文已生成：translation/zh/...
   📷 拷贝图片：N 张（copy_images.py 输出已列出）
   🌐 远程图片：保持引用不拷贝
   📝 术语首次出现位置：梯度下降→第 2 段，注意力机制→第 5 段，...
   ```

---

## 5. Quality Checklist（产出前自检）

在输出译文之前，逐项核查：

- [ ] 译文标题层级（`#` / `##` / `###`）与原文完全一致，数量相同
- [ ] 所有 `$...$`、`$$...$$` 公式内容未被修改，字符完全相同
- [ ] 所有 fenced code block 原样保留，语言标签未变
- [ ] .ipynb 文件：code cell 的 source 和 outputs 未被修改
- [ ] .ipynb 文件：JSON 合法，可被 `json.load()` 解析
- [ ] 所有本地图片已拷贝到目标 `img/` 目录
- [ ] `<img>` 的 `src` 和 `<a>` 的 `href` 属性未被修改
- [ ] 术语表中的高频术语首次出现时均已括注英文
- [ ] 无整段遗漏未翻译的英文（行内英文术语除外）
- [ ] GitHub Callout 关键字（NOTE/WARNING/TIP）保持英文

---

## 6. Anti-patterns（严格禁止）

| 禁止行为 | 正确做法 |
|----------|----------|
| 标题加英文括注：`## 理解导数 (Understanding Derivatives)` | 标题只写中文：`## 理解导数` |
| TOC 锚点不更新，保留原英文 id | 锚点随中文标题同步更新为新 slug |
| 翻译 code cell 中的代码 | code cell 原样保留 |
| 修改 `$\frac{1}{n}$` 内容 | 公式逐字不动 |
| 把图片路径 `img/foo.png` 改为 `图片/foo.png` | 路径严格不变 |
| 下载远程图片 | 远程 URL 仅保留引用 |
| 修改 .ipynb 的 `kernelspec`/`execution_count` | 原样写回 |
| 把 ` ```python ` 改成 ` ```python代码 ` | 语言标签不变 |
| 在译文中新增原文没有的注释或说明 | 忠实原文，不添加 |
| 把代码注释 `# compute gradient` 翻译成 `# 计算梯度` | code cell 不动 |
| 创建临时 `.py` 脚本来辅助翻译或写文件 | 直接用文件写入工具输出译文 |
| 翻译一半后因内容太长截断，剩余 cell 不翻译 | 按 `##` 章节分批翻译，确保全部 cell 覆盖 |

---

## 7. 术语表（本项目常用术语）

首次出现时使用「中文 (English)」格式；后续段落仅用中文。

| 英文 | 中文 |
|------|------|
| neural network | 神经网络 |
| backpropagation | 反向传播 |
| gradient | 梯度 |
| gradient descent | 梯度下降 |
| loss / loss function | 损失 / 损失函数 |
| tensor | 张量 |
| weight / bias | 权重 / 偏置 |
| activation function | 激活函数 |
| multi-layer perceptron (MLP) | 多层感知机 (MLP) *(缩写首次保留)* |
| attention mechanism | 注意力机制 |
| self-attention | 自注意力 |
| embedding | 嵌入 |
| layer normalization (layer norm) | 层归一化 (layer norm) |
| batch normalization (batch norm) | 批归一化 (batch norm) |
| softmax | softmax *(不译，领域惯用)* |
| cross-entropy | 交叉熵 |
| autograd | 自动微分 (autograd) |
| broadcasting | 广播机制 |
| checkpoint | 检查点 |
| fine-tuning | 微调 |
| tokenizer / tokenization | 分词器 / 分词 |
| RLHF | RLHF *(缩写首次保留)* |
| KV cache | KV 缓存 |
| residual connection | 残差连接 |
| weight decay | 权重衰减 |
| learning rate | 学习率 |
| Adam / SGD | Adam / SGD *(优化器名称不译)* |
| forward pass | 前向传播 |
| backward pass | 反向传播 |
| computational graph | 计算图 |
| transformer | Transformer *(模型名称不译)* |
| language model | 语言模型 |
| pretraining | 预训练 |
| inference | 推理 |
| logit | logit *(不译，领域惯用)* |
| token | token *(不译，领域惯用)* |
| batch | 批次 |
| epoch | 轮次 (epoch) |
| dropout | Dropout *(不译)* |
| regularization | 正则化 |
| hyperparameter | 超参数 |
| overfit / underfit | 过拟合 / 欠拟合 |
| validation set / test set | 验证集 / 测试集 |

> **注意**：`softmax`、`logit`、`token`、`Transformer`、`Dropout`、`Adam`、`SGD`
> 等在中文机器学习领域已是惯用词，**不翻译**，直接使用英文原词。
