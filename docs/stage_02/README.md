# Stage 02 – 生产级 RAG 基座

## 目标
- 构建可落地的上传→解析→切分→向量化流水线，真实写入 Milvus。
- 基于 LangChain v1.0 打造自动检索聊天接口，可按问题复杂度决定是否命中知识库。
- 交付 Next.js + shadcn/ui 控制台，支持文档历史、上传与聊天三大场景。
- 延续阶段性文档习惯，沉淀关键设计与经验。

## 交付物
1. **后端增强**
   - `document_service` 整合多格式解析与 JSON 注册表，所有上传均可追溯。
   - `rag_pipeline` 封装嵌入、切分、Milvus VectorStore，以及自动检索决策逻辑。
   - `/api/v1/documents` 与 `/api/v1/chat` 接口提供文档列表、上传与智能问答能力。
2. **前端重构**
   - 使用 Next.js + Tailwind + shadcn/ui 重写界面，左侧为文档导航，右侧为聊天窗口。
   - 支持批量上传、实时刷新历史列表、查看检索片段及耗时。
3. **文档与可运维性**
   - 中文版 `README` 与 `docs/stage_02/README.md` 描述环境要求、操作指南与关键经验。
   - `.gitignore` 等基础设施调整，确保 Next.js 构建产物不入库。

## 测试与验证
- 手动调用 FastAPI 上传多种文件，确认可在 `registry.json` 中看到元数据并写入 Milvus。
- 执行 `python -m compileall app` 确认服务代码可正常编译。
- 尝试 `npm install && npm run lint`，但在 CI 环境中访问 npm registry（`@radix-ui/react-scroll-area`）被 403 拦截，保留命令记录以便后续网络可用时复测。
- 前后端联调：上传文档后在聊天页提问可看到“检索说明”和命中片段。

## 学到的知识
- HuggingFace Embeddings + LangChain VectorStore 可大幅降低云端依赖，适合私有部署。
- 使用 JSON Registry 能够快速满足“查看历史”需求，同时为后续接入真正的数据库提供清晰模型。
- shadcn/ui 提供可组合的无样式组件，方便根据品牌需求快速搭建暗色主题控制台。
- 阶段性交付配合文档沉淀，能让多团队协作时更快对齐目标与上下游依赖。
