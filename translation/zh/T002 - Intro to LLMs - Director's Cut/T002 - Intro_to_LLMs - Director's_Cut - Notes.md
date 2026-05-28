# 给忙碌人士的大语言模型 (LLM) 入门 - 导演剪辑版

[YouTube 视频 - Andrej Karpathy](https://www.youtube.com/watch?v=zjkBMFhNj_g)<br>[幻灯片, PDF - Google Drive](https://drive.google.com/file/d/1pxx_ZI7O-Nwl7ZLNk5hI3WzAsTLwvNU7/view?pli=1)<br>[幻灯片, Keynote - Google Drive](https://drive.google.com/file/d/1FPUpFMiCkMRKPFjhi9MAhby68MHVqe8u/view)<br>笔记由 [mk2112](https://github.com/mk2112) 整理

---

**目录**

- [大语言模型](#大语言模型)
	- [推理](#推理)
	- [训练](#训练)
	- [网络交互](#网络交互)
	- [网络架构](#网络架构)
	- [需要管理辅助](#需要管理辅助)
	- [性能评估](#性能评估)

- [回到未来](#回到未来)
	- [扩展大语言模型](#扩展大语言模型)
	- [工具使用](#工具使用)
	- [学术视角](#学术视角)

- [越狱与安全挑战](#越狱与安全挑战)

---

## 大语言模型

### 推理

以 MetaAI 的 [Llama-2-70b](https://ai.meta.com/llama/) 这样的大语言模型 (LLM) 为例。Llama-2-70b 这个名称标识了模型的关键属性：它是 Llama 模型系列的第二次迭代，包含 $700$ 亿个独立参数。在 DeepSeek V3 和 DeepSeek R1 之前，Llama-2-70b 是权重公开可用的最强大模型。"公开可用权重"这个术语意味着所有模型参数的具体数值与模型架构一起公开发布。

> 这种公开方式与 OpenAI 的 GPT-4o 等模型形成对比。后者用户只能看到和交互推理结果和输入，权重并不公开。

Llama-2-70b 的部署包本质上只由两个文件组成：
- `parameters`：这个文件约 140 GB（每个权重 2 字节，数据类型为 `Float16`），包含权重，即 $700$ 亿个参数
- `run.c`：这个文件中非常紧凑的代码定义了模型架构，并允许通过推理与参数化模型进行训练和交互。这里使用的编程语言是 `C`，但理论上 `Python`、`C++` 或 `Julia` 等语言也可以完成这项任务

> 这两个文件 `parameters` 和 `run.c` 就足以容纳整个模型和基本交互逻辑。你可以下载这些文件（比如到你的 M2 MacBook 上），运行模型，它就能根据输入生成文本。

为了更好地说明这一点，你可以断开网络连接，然后让模型描述某家公司、想出一个食谱或任何类似的任务，模型都会给出回答。这是因为文本完全基于你计算机上加载的权重生成。**对于 Llama-2-70b 这样的标准大语言模型，推理过程中不使用任何外部信息。**

<img src="./img/Pasted%20image%2020231123104403.png" width="250" height="auto" />

> 对于大语言模型，困难的部分在于获得能够生成最佳文本的权重。

### 训练

没有训练就没有推理。<br>
训练非常复杂，除了推理之外，在笔记本电脑上运行训练既不推荐也往往完全不可能。

有趣的是，MetaAI [公开了他们训练 Llama 2 的具体方法](https://arxiv.org/abs/2307.09288)。<br>根据这篇论文，首先我们需要文本让模型接触和学习。需要大量的文本。这些文本通过爬取网络获得，总计约 10 TB 的文本。<br>未训练的模型被加载到所谓的 GPU 集群上，然后暴露给这个巨大的数据集。可以把 GPU 集群想象成一组服务器，每台服务器运行多个[专用显卡或图形处理单元 (GPU)](https://www.nvidia.com/en-us/data-center/a100/)（在百思买买不到的那种）。事实证明，专用 GPU 是我们训练大语言模型的最佳硬件。MetaAI 使用了 $6000$ 块 GPU 训练 $12$ 天，花费约 $200$ 万美元。与已公布的闭源模型数据相比，这个成本相对较低。

> 我们现在拥有的复杂设置旨在将约 10 TB 文本中的知识蒸馏到我们期望的参数集中。**你可以把这个过程理解为有损知识压缩。**这就是大语言模型训练的全部意义。

### 网络交互

大语言模型的核心任务是**在给定上下文（即某些已有的 token 序列）的情况下，找到最可能的下一个 token**。

<img src="./img/Pasted%20image%2020231123111305.png" width="500" height="auto" />

预测结果与用于获得该结果的压缩/权重之间存在密切关系。<br>
一组好的权重比一组差的权重能更好地预测训练集中的下一个词（我们在每种情况下都预先知道下一个词是什么）。因此，更好的权重更紧密地表示数据，这使我们可以用权重压缩的类比来理解。

如果我们的目标是预测下一个词，模型参数应该编码输入文本/token 序列中某些词的不同重要性。如果模型能识别出下面展示的上下文中的重要段落，它就能让这些段落更恰当地影响输出概率。

<img src="./img/Pasted%20image%2020231123112449.png" width="350" height="auto" />

> 大语言模型的"魔法"在于反复进行下一个词的预测，将最近预测出的词加入输入序列，一次又一次地生成下一个词。基于输入的预测贡献于构成基于输入的预测的输入……

<img src="https://api.wandb.ai/files/darek/images/projects/37727390/9ec381c5.gif" width="500" height="auto" />

将输出拼接到先前输入中以形成下一个输入的过程被称为"做梦"（即"编造输入序列的延续"）。这就是为什么例如 OpenAI 对 ChatGPT 声明 `"ChatGPT 可能会犯错。请核实重要信息。"` 的原因之一。大语言模型关于 DOI、ISBN 和日期等的陈述并非基于事实，而是完全基于给定上下文中的感知概率。大语言模型在"鹦鹉学舌"——它认为基于训练数据中最合适的内容。因此某些输出在事实上是正确的，某些则可能只是看起来正确。本质上，这就是有损压缩在起作用。

如果这听起来有趣，我推荐你观看 [Andrej 的 Makemore 系列](https://www.youtube.com/watch?v=PaCmpygFfXo)，其中详细实现和讨论了下一个字符预测的过程。该系列的笔记可以在[这里](../N002%20-%20Makemore%201/N002%20-%20Makemore.ipynb)找到。

### 网络架构

**坐稳了。** 当今的大语言模型共享一个核心构建模块，它构成了模型的大部分：

<img src="./img/Pasted%20image%2020231123114140.png" width="450" height="auto" />

这就是 [Transformer](https://arxiv.org/abs/1706.03762)。这个构建模块在数学含义上已经被完美地描述和理解。Transformer 迭代地影响模型参数，以更好地表示生成正确下一个词的概率。我们可以测量到 Transformer 确实在做这件事。但对于参数如何协同工作来得出概率，我们只有一些最基本的想法。

> 把大语言模型想象成输出预测概率链的模型。大语言模型不是数据库，而是（目前）大多难以理解的产物，因此需要相应地发展出复杂的评估方法。

如果你对 Transformer 有兴趣，[Andrej 关于 GPT 的视频](https://www.youtube.com/watch?v=kCc8FmEb1nY)是一个不错的资源。（笔记在[这里](../N007%20-%20GPT%20From%20Scratch/N007%20-%20GPT.ipynb)）

### 需要管理辅助

假设我们现在建立了一个基于 Transformer 的模型，并且已经用数 TB 的爬取训练文本对其进行了训练，优化模型进行下一个词的预测。**充其量，这使我们的大语言模型成为一个熟练的文档生成器。**

<img src="./img/Pasted%20image%2020231123115954.png" />

然而，ChatGPT、Llama 或 Open Assistant 背后的大语言模型并不仅限于此。你可以向它们提出问题并获得回答。为了实现这种行为，本质上我们继续训练，但更换了数据。具体来说，需要一个由人工编写的、以问题为输入、答案为输出的数据集。

> 可以把这看作[迁移学习](https://www.informatica.si/index.php/informatica/article/view/2828)过程的第二阶段。第一阶段是高数量、低任务特定质量。第二阶段提供较少的数量，但有任务特定性。这是迁移学习的一种特殊情况，称为**微调**。对于 OpenAI，该过程在[这篇论文](https://arxiv.org/abs/2203.02155)中有概述。

<img src="./img/Pasted%20image%2020231123122521.png" width="300" height="auto" />

微调效果*如此*好的事实令人瞩目。但其原因尚不清楚。<br>
知识和任务特定性在这里结合在一起。

<img src="./img/Pasted%20image%2020231123122701.png" width="400" height="auto" />

关于错误行为的收集：我们监控助手模型的 $Q$-$A$ 能力。如果答案不符合我们的预期，我们就让人工反馈循环在给定 $Q$ 的情况下提供正确的 $A$。然后将其添加到每周的微调循环中。

上面讨论的 Llama-2 系列在发布时同时包含基础模型和已经微调过的模型，为你自己的、成本更低的微调提供了基础。

*还没完。*<br>微调的最先进方法至少涉及第三阶段。<br>
这基于这样一种推理：提供两个答案并让用户选择更合适的那个，成本更低。这种行为有时可以在 ChatGPT 等工具中遇到。在 OpenAI，这个第三阶段被称为 [RLHF](https://openai.com/research/learning-from-human-preferences)。

### 性能评估

在经过这个复杂的、资源密集的训练和微调过程之后，大语言模型可以相互比较。例如通过 [Chatbot Arena](https://chat.lmsys.org/)，不同的大语言模型获得类似于国际象棋的*Elo 等级分*。

上述等级分的推导过程在[这篇论文](https://arxiv.org/abs/2306.05685)中有进一步说明。本质上，一个人类用户接收来自未知聊天机器人的两个输出，并选择更好的那个。

<img src="./img/Pasted%20image%2020231123125556.png" /><br>来源：[huggingface.co](https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard)

> 闭源模型效果好得多，但你无法自由使用。"开源 vs. 专有"之争正在进行中。

## 回到未来

### 扩展大语言模型

下一个词预测任务中的性能准确度是一个可以很好预测的函数，取决于：
- $N$，模型中的参数数量
- $D$，用于训练的文本量

<img src="./img/Pasted%20image%2020231123131541.png" width="320" height="auto" /><br>来源：[Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556)

> 随着训练 FLOPS（$D$）的增加，当扩展参数数量 $N$ 时，训练损失 (loss) 呈下降趋势。

所以把算法进步放在一边，我们可以用已有的工具合理地提升性能。<br>
有趣的是，在初始训练步骤之后，我们实际上并不关心下一个词预测本身，但完成的模型在该任务上的表现可以作为更高级别评估的良好指标。

> 这正是当前淘金热的驱动力。这不是算法复杂度的竞赛，而是纯粹的资源、时间和规模的竞赛。业界普遍对仅通过这些非常非常简单（但不容易）的调整就能达到 SOTA（目前）充满信心。

### 工具使用

借助 [ChatGPT on GPT-4 Turbo](https://chat.openai.com/) 或 [Perplexity.Ai](https://www.perplexity.ai/) 等 AI 工具，训练或微调集之外的额外信息来源包括实时互联网连接。ChatGPT 发出特殊的关键词，后端可以将其解释为想要使用必应搜索的请求。后端发出并收集搜索结果，将其交给模型，模型将其整合到回复中。

> 这种"特殊词语"语法当然可以扩展到其他外部应用，如计算器或 Python，从而最大限度地减少上面描述的对预期事实数据（如数学结果）的"做梦"。工具使用为大语言模型增加了一个全新的可用性维度——无论是通过提高事实一致性，还是通过集成 DALL-E 等其他模型。**这被认为是通往通用人工智能 (AGI) 的根本性一步。**

<img src="./img/Pasted%20image%2020231123134345.png" width="450" height="auto" />

### 学术视角

一个公认的学术概念是人脑中的[两种一般运作模式](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow)：
- **系统 1** 描述的是一种缓存，即快速响应、几乎不需要努力的概念。
- **系统 2** 增加了处理复杂性的能力，代价是更缓慢的、逻辑性的、需要努力的思考

<img src="./img/Pasted%20image%2020231123135353.png" /><br>来源：[思考，快与慢](https://search.worldcat.org/en/title/706020998)

**系统 2** 以及从思维树的分支中确定输出的复杂能力正是学术界目前追逐的目标。像 [Dreamer](https://arxiv.org/abs/1912.01603)（用于强化学习）这样的算法可能与思维树没有直接关系，但它们开始朝这个方向发展——即利用潜在想象力进行自我优化。

<img src="./img/Pasted%20image%2020231123135937.png" width="250" height="auto" /><br>来源：[Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601)

强化学习 (Reinforcement Learning) 确实是一股即将更显著融入大语言模型的力量。<br>
目前的问题仍然是：**通用大语言模型的系统 2 是什么？**

> 如上所述，大语言模型并不仅限于作为聊天机器人。更重要的是，它们开始作为 [Software 2.0](https://karpathy.medium.com/software-2-0-a64152b37c35) 操作系统的内核而涌现。虽然昂贵，但正在崛起。你可以看到与"旧栈"操作系统的相似之处——闭源和开源系统并存。

## 越狱与安全挑战

大语言模型的越狱 (Jailbreak) 在社交媒体上有不同程度的讨论，但核心问题在于，训练充分的大语言模型的信息生成在某些领域必须受到严格限制。你不希望恶意询问得到建设性的回应。这是一个核心伦理关切。

早期流传的一种越狱方式是假装在实际询问周围设置一个场景，稀释模型对检测恶意意图的注意力。你讲一个关于某人问某事的故事，让注意力从问题本身转移到场景设定上。

*另一个。* 事实证明 Claude v1.3 不仅理解 Base64 编码，还允许使用 Base64 进行交互：

<img src="./img/Pasted%20image%2020231123142056.png" width="400" height="auto" /><br>来源：[Jailbroken: How Does LLM Safety Training Fail?](https://arxiv.org/abs/2307.02483)

*另一个。* 事实证明，有人发现了一个通用的后缀，如果附加到查询中，可以禁用某些模型的对齐措施：<br>[Universal and Transferable Adversarial Attacks on Aligned Language Models](https://arxiv.org/abs/2307.15043)

*另一个。* 在查询中添加一张带有精心确定噪声的熊猫图像，可以充当密钥，禁用对齐措施：<br>[Visual Adversarial Examples Jailbreak Aligned Large Language Models](https://arxiv.org/abs/2306.13213)

*另一个。* 来自图像的提示注入 (Prompt Injection) 会稀释原始查询的意图，从而控制输出内容。这很有趣。但让响应变成故意格式错误的恶意链接就不好玩了：

<img src="./img/F8XM80SXcAAVcVw.jpg" width="250" height="auto" /><br>
来源：Riley Goodside via [X/Twitter](https://twitter.com/goodside/status/1713000581587976372)

*另一个。* 存在一种叫做"潜伏代理攻击"（sleeper agent attack）的方式。这次攻击向量涉及训练数据。如果恶意意图被嵌入其中，例如设置触发短语的恶意文档，这可能故意扭曲关系，以至于提到该短语就会破坏模型。<br>论文：[Poisoning Language Models During Instruction Tuning](https://arxiv.org/abs/2305.00944), [Poisoning Web-Scale Training Datasets is Practical](https://arxiv.org/abs/2302.10149)

这些攻击大多已被发现、公开、解决和修复。<br>
但你可以看到，**这场追逐正在进行中。**
