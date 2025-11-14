# LangChain + Milvus RAG 平台

本仓库以 LangChain v1.0 为核心，构建支持生产级知识库管理与问答体验的 RAG（Retrieval-Augmented Generation）系统。
后端使用 FastAPI + Milvus 负责解析、切分、嵌入与检索，前端基于 Next.js + shadcn/ui 打造操作控制台，满足上传多种格式文件、查看历史以及与知识库对话等场景。

## 功能亮点
- **多格式解析**：PDF、Office、文本、图片统一进入解析流水线，并登记元数据方便审计。
- **自动检索决策**：聊天接口内置启发式策略，可根据提问复杂度自动决定是否命中向量数据库。
- **Milvus 持久化**：通过 LangChain VectorStore 管理 collection，确保上传后立即可检索。
- **前后台解耦**：Next.js 前端具备文档导航、上传、聊天面板，后端提供标准化 REST API。
- **阶段性文档**：`docs/stage_xx` 按敏捷节奏记录目标、交付物和经验。

## 快速开始
1. **后端服务**
   ```bash
   cd backend
   pip install -e .
   uvicorn app.main:app --reload
   ```
   - Milvus 默认连接 `localhost:19530`，可通过环境变量 `MILVUS_HOST/MILVUS_PORT` 覆盖。
   - 上传文件会保存至 `backend/storage/uploads/` 并写入注册表 `registry.json`。

2. **前端控制台**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - 默认调用 `http://localhost:8000/api/v1`，若需变更请设置 `NEXT_PUBLIC_API_BASE`。

3. **访问体验**
   - 打开浏览器访问 `http://localhost:3000`。
   - 左侧面板可上传/刷新文档，右侧聊天区输入问题即可触发 RAG 流程。

更多阶段性设计、决策与经验请参考 `docs/` 目录。
