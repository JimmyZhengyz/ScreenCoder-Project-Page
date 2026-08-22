# ScreenCoder 静态项目页设计规格

日期：2026-08-22  
状态：等待用户审核  
站点语言：英文  
内部设计文档语言：中文

## 1. 项目目标

为 ScreenCoder 建立一个单页、纯静态、适合 GitHub Pages 的研究项目网站。网站面向研究者、开发者和希望体验 UI-to-Code 工作流的普通访客，统一连接论文、代码、在线 Demo 和数据集。

首版不在页面内执行模型推理，不嵌入 Hugging Face Space，也不依赖数据库、服务端 API 或运行时密钥。页面以轻量预览展示能力，并通过明确按钮跳转到现有公开资源。

## 2. 已确认的产品决定

- 定位：研究项目页与产品 Demo 的混合形态。
- 语言：英文。
- 形态：单页静态网站。
- 在线体验：展示视频或图片预览，跳转至 Hugging Face Space。
- 内容范围：方法、结果、定性案例、数据集、代码、论文、引用和致谢。
- 开发方式：先在没有 remote 的本地 Git staging 仓库中开发和审核。
- 部署方式：最终使用 GitHub Pages 的 `github.io` 项目站点。
- 部署所有者：本阶段有意延后决定；可选择 `leigest519` 或其他获得授权的 GitHub 账号。

## 3. 公开事实基线

项目页只使用以下公开来源作为事实与素材基线：

1. 论文：<https://arxiv.org/abs/2507.22827>
2. 官方代码：<https://github.com/leigest519/ScreenCoder>
3. 在线 Demo：<https://huggingface.co/spaces/Jimmyzheng-10/ScreenCoder>
4. ScreenBench：<https://huggingface.co/datasets/Leigest/ScreenCoder>
5. Hugging Face Paper：<https://huggingface.co/papers/2507.22827>

本地历史报告、旧 README 副本和第三方 fork 不作为页面 claim 的权威来源。公开仓库中的原始素材可以复用，但需记录源路径、commit 和许可证。

## 4. 必须在发布前解决的一致性问题

以下问题不阻塞页面结构开发，但会阻塞对应数字或链接公开：

- arXiv v2 正文将 ScreenCoder Agentic 的 ScreenBench Block 描述为 `0.755`，而主表行中的第一个 Block 数值为 `0.768`；`0.755` 位于 Position 列。发布前必须确认正确表述。
- Hugging Face Dataset Card 的实际仓库为 `Leigest/ScreenCoder`，但示例代码出现 `leigest519/ScreenBench`。页面下载按钮应指向真实可访问的仓库，示例代码需另行核对。
- Screen-10K 在论文中被描述为 10,000 条训练数据，但当前公开入口主要指向 1,000 条 ScreenBench。未确认公开下载地址前，Screen-10K 只作为论文方法内容介绍，不提供下载按钮。

这些内容在实现时通过数据文件中的 `verified` 状态控制：未经确认的数字不会出现在醒目的指标卡中。

## 5. 推荐技术路线

使用原生 HTML、CSS 和少量 Vanilla JavaScript，不引入 Astro、React、Jekyll、数据库或后端。

选择该路线的原因：

- 页面是单页研究展示站，组件复杂度有限。
- GitHub Pages 可以直接托管，无需专有构建平台。
- 减少依赖更新和供应链维护成本。
- 便于未来迁移到任意 GitHub owner/repository。
- 页面在禁用 JavaScript 时仍能阅读主要研究内容。

## 6. 部署可迁移设计

页面不得硬编码以下内容：

- GitHub owner 名称。
- GitHub repository 名称。
- `/ScreenCoder/` 形式的绝对 base path。
- 最终 `github.io` 域名。

所有站内资源使用相对路径，例如：

```html
<img src="./assets/images/teaser.webp" alt="ScreenCoder examples">
<link rel="stylesheet" href="./css/style.css">
```

外部 Paper、Code、Demo 和 Dataset 链接集中保存在一个站点配置文件中。最终确定部署账号时，只需更新 canonical URL、Open Graph URL、sitemap 和部署设置，不修改页面结构。

支持的发布目标包括：

```text
https://leigest519.github.io/ScreenCoder/
https://<other-owner>.github.io/ScreenCoder/
https://<other-owner>.github.io/<other-repository>/
```

## 7. 页面信息架构

### 7.1 Hero

- ScreenCoder 正式论文标题。
- arXiv v2 作者顺序与机构。
- 一句话价值主张。
- Paper、Code、Live Demo、Dataset 四个主按钮。
- 官方 teaser 或从论文 Figure 1 导出的高分辨率主视觉。

### 7.2 Motivation

用两个并列案例解释端到端 MLLM 的核心失败：

- Perception Errors：遗漏、误识别、错误文本或颜色。
- Planning Errors：空间位置、层级和 DOM 结构错误。

### 7.3 Method

以连续流程展示：

```text
UI Screenshot / Design Sketch
  -> Grounding Agent
  -> Planning Agent
  -> Generation Agent
  -> Placeholder Mapping
  -> HTML/CSS + Rendered Webpage
```

每一步提供一句主解释和一段可展开的技术说明。方法图优先使用可缩放 SVG 重绘，保留论文原始语义和标注。

### 7.4 Live Demo

- 展示公开仓库中的 YouTube、Instagram 和 Design Draft 演示。
- 使用静态 poster 和用户点击后加载的视频，避免首屏加载大文件。
- 提供跳转 Hugging Face Space 的主按钮。
- Space 不可用时，静态页面仍完整可阅读。

### 7.5 Results

- ScreenBench 与 Design2Code 主结果。
- Base Model、SFT、RL 的阶段性对照。
- 人工偏好实验与工作流效率实验。
- 指标含义：Block、Text、Position、Color、CLIP。

完整表格作为主证据；醒目的指标卡只使用通过一致性检查的数字。表格在移动端允许水平滚动，并始终显示数据来源。

### 7.6 Data Engine

- 50,000 个网页的初始收集背景。
- Screen-10K 的 10,000 个高质量 image-code pairs。
- 9,000 条 SFT 与 1,000 条 RL 的论文设定。
- ScreenBench 的 1,000 条现代网页 benchmark。
- 已确认公开的数据集入口。

### 7.7 Qualitative Gallery

展示多组 Source、Baseline、ScreenCoder 三列对比。首版优先使用官方仓库和 arXiv v2 已公开案例，不使用内部未发布实验截图。

图片提供明确 caption、模型名称和来源。移动端改为标签切换，避免三列图像过窄。

### 7.8 Citation and Footer

- arXiv BibTeX 复制按钮。
- 作者、机构、代码许可证和论文许可证信息。
- Paper、Code、Demo、Dataset、Hugging Face Paper 链接。
- 对 UIED、Design2Code、DCGen 等公开依赖或基础工作的致谢。

## 8. 视觉方向

采用现代研究项目页风格：浅色背景、深色正文、蓝紫色强调色、宽内容区和清晰的论文式层级。

- 首屏重点是 teaser，不使用复杂 3D 或 WebGL。
- 动效仅用于 section 出现、方法流程和 gallery 切换。
- 尊重 `prefers-reduced-motion`。
- 正文字体与代码字体分离。
- 视觉重点来自真实输入/输出案例，而不是装饰插画。

## 9. 文件结构

```text
ScreenCoder-Project-Page/
├── index.html
├── 404.html
├── README.md
├── assets/
│   ├── images/
│   ├── videos/
│   ├── icons/
│   └── data/
├── css/
│   └── style.css
├── js/
│   └── main.js
├── favicon.svg
├── robots.txt
├── sitemap.xml
└── docs/
    └── superpowers/
        ├── specs/
        └── plans/
```

研究内容与页面结构尽量分离。链接、作者、指标和案例元数据使用 JSON 管理，页面本身不重复散落相同数字。

## 10. 数据流与降级策略

```text
公开来源
  -> 素材与 claim 清单
  -> 已验证结构化数据
  -> 静态页面内容
  -> 本地预览
  -> GitHub Pages
```

- JavaScript 加载失败：导航、正文、图片、表格和外部链接仍可用。
- 视频加载失败：显示 poster、说明文字和直接链接。
- Hugging Face Space 不可用：只影响外部体验按钮，不影响站点。
- 某项指标未确认：隐藏指标卡，保留经过核对的表格或暂不展示该项。
- 外部资源 URL 失效：发布检查失败，阻止正式上线。

## 11. 可访问性与性能要求

- 所有信息图片提供有意义的 `alt` 文本。
- 页面可以使用键盘完成导航和 gallery 切换。
- 焦点状态清晰可见。
- 颜色对比满足 WCAG AA。
- 移动端宽度从 320px 起可用。
- 首屏图片优先加载，其余图片和视频懒加载。
- 图片优先使用 WebP/AVIF，并保留必要的高分辨率来源。
- 页面不请求分析 SDK、广告 SDK 或模型 API。

## 12. 测试与验收

### 内容验收

- 标题、作者、机构和 BibTeX 与 arXiv v2 一致。
- 所有结果数字都有公开来源和核对记录。
- Code、Paper、Demo、Dataset 链接可访问。
- 页面不引用本地绝对路径或内部实验材料。

### 技术验收

- 从任意本地静态服务器根路径可正确访问。
- 部署到任意 GitHub Pages 项目子路径时资源不出现 404。
- Chrome、Safari、Firefox 最新稳定版基本一致。
- 320px、768px、1440px 三档布局无溢出或遮挡。
- 禁用 JavaScript后核心内容仍可阅读。
- Lighthouse 的 Performance、Accessibility、Best Practices、SEO 目标均不低于 90。
- HTML 校验无结构性错误，控制台无未处理异常。

### 安全验收

- 仓库不包含 API key、token、模型凭据、用户上传文件或运行日志。
- 外链使用安全的 `rel` 属性。
- 不在静态页面中调用 Doubao、OpenAI、Qwen 或其他模型 API。

## 13. 开发与发布阶段

1. 建立公开来源和素材 manifest。
2. 核对论文、README、Dataset Card 的关键 claim。
3. 完成桌面与移动线框。
4. 实现语义化 HTML 和基础 CSS。
5. 加入方法图、案例 gallery、视频和结果表。
6. 完成响应式、可访问性、性能和链接测试。
7. 在本地或 private staging 中完成内部审核。
8. 确定最终 GitHub owner、repository 和 canonical URL。
9. 生成最终部署配置并发布至 GitHub Pages。
10. 将 Project Page 链接回填至官方 GitHub README、Hugging Face Space 和其他获得授权的公开入口。

## 14. 非目标

首版不包含：

- 在 GitHub Pages 内执行真实 ScreenCoder 推理。
- 用户登录、上传历史、数据库或结果持久化。
- Hugging Face Space iframe 嵌入。
- 多语言切换。
- 博客、新闻 CMS 或复杂文档系统。
- 在未获授权时修改官方 GitHub、arXiv 或 Hugging Face 页面。

## 15. 发布门槛

只有在以下条件全部满足后才确定部署账号并发布：

- 用户批准最终页面视觉与英文文案。
- 所有公开数字和数据集链接完成一致性核对。
- 已确认有权限使用目标 GitHub owner 和 repository。
- 已确认 teaser、视频和对比图可按其许可证用于项目页。
- 最终站点不包含秘密信息或内部材料。
- GitHub Pages 子路径部署测试通过。

