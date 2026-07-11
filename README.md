# 基于IT知识的RAG智慧问答系统

IT知识智慧问答系统是一个面向IT教育领域的智能问答平台，融合基于知识库的精确检索与基于大模型的语义理解，为学习者提供多学科、多轮对话的专业答疑服务。系统采用「BM25 关键词检索 + RAG 增强生成」双通路融合架构，覆盖多学科领域知识，支持流式交互与对话历史管理。

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn + WebSocket |
| 大语言模型 | DeepSeek V4 Pro（通过 DashScope 兼容 API） |
| 向量数据库 | Milvus（Hybrid Search：Dense + Sparse） |
| 嵌入模型 | BGE-M3（BAAI，支持 Dense/ Sparse/ Colbert 混合检索） |
| 重排序 | BGE-Reranker-Large |
| 关系数据库 | MySQL |
| 缓存 | Redis |
| BM25 检索 | rank-bm25 + jieba 分词 |
| LLM 框架 | LangChain |
| 文档处理 | PyMuPDF + python-docx + python-pptx + RapidOCR |
| 查询分类 | BERT-base-chinese 微调（5000 条标注数据训练） |
| 前端 | 原生 HTML/CSS/JS（marked.js 渲染 Markdown） |
| 评估框架 | RAGAS |

## 项目结构

```
integrated_qa_system/
├── app.py                  # FastAPI 应用入口 + WebSocket 流式接口
├── new_main.py             # 集成问答系统核心（双通路调度）
├── api.py                  # SSE 流式 API（备用）
├── use_api.py              # API 调用示例
├── config.ini              # 配置文件（MySQL / Redis / Milvus / LLM / 检索参数）
├── requirments.txt         # Python 依赖
├── base/
│   ├── config.py           # 配置解析模块
│   └── logger.py           # 日志模块
├── mysql_qa/
│   ├── main.py             # MySQL 问答子系统入口
│   ├── db/mysql_client.py  # MySQL 客户端封装
│   ├── cache/redis_client.py # Redis 客户端封装
│   ├── retrieval/bm25_search.py # BM25 检索（置信度阈值分流）
│   └── utils/preprocess.py # 文本预处理
├── rag_qa/
│   ├── rag_main.py         # RAG 子系统入口
│   ├── core/
│   │   ├── new_rag_system.py   # RAG 核心（回溯/子查询/HyDE 多策略检索）
│   │   ├── rag_system.py       # 基础 RAG 系统
│   │   ├── vector_store.py     # Milvus 向量存储（Hybrid Search + Rerank）
│   │   ├── document_processor.py # 多模态文档加载与分块
│   │   ├── query_classifier.py # BERT 查询意图分类器
│   │   ├── strategy_selector.py # LLM 驱动的检索策略自适应选择
│   │   ├── prompts.py          # Prompt 模板
│   │   └── bert_query_classifier/ # BERT 分类器训练权重
│   ├── edu_document_loaders/   # 教育文档加载器（PDF/Word/PPT/图片 OCR）
│   ├── edu_text_spliter/       # 中文递归文本分割器
│   ├── models/
│   │   ├── bge-m3/             # BGE-M3 嵌入模型
│   │   ├── bge-reranker-large/ # BGE 重排序模型
│   │   ├── bert-base-chinese/  # BERT 中文基础模型
│   │   └── nlp_bert_document-segmentation_chinese-base/ # 文档分段模型
│   ├── rag_assesment/          # RAGAS 评估脚本与数据
│   └── classify_data/          # 查询分类训练数据（5000 条）
├── static/
│   └── index.html              # Web 前端页面
└── logs/
    └── app.log                  # 应用日志
```

## 核心特性

### 双通路检索架构

系统采用 BM25 精确匹配 + RAG 语义理解的**双通路融合**策略：

1. **BM25 快速通道**：查询首先经过 BM25 关键词检索（基于 MySQL 知识库 + Redis 缓存），当置信度 ≥ 阈值时直接返回答案，实现毫秒级响应
2. **RAG 深度通道**：BM25 置信度不足时，自动回退到 RAG 语义理解通路，通过 Milvus 向量检索 + LLM 生成更全面的答案

### 多策略智能检索

RAG 通路集成了四种检索策略，由 LLM 驱动的策略选择器自适应选取：

| 策略 | 适用场景 |
|------|----------|
| 直接检索 | 一般性查询 |
| 回溯问题（Step-back） | 需要更高层次概括的复杂问题 |
| 子查询分解 | 多层次、多方面的复合问题 |
| HyDE（假设性文档嵌入） | 查询词与文档表述差异较大的场景 |

每种策略均经过 **BGE-M3 Hybrid Search（Dense + Sparse 混合检索）+ BGE-Reranker 重排序**，最终选取相关度最高的上下文片段送入 LLM。

### 查询意图分类

使用 **BERT-base-chinese 微调**的二分类器，将用户查询分为「通用知识」和「专业咨询」两类，基于 5000 条标注数据训练，不同类别路由到不同的处理分支。

### 流式交互

- **WebSocket 流式响应**：LLM 生成结果以 token 级别实时推送到前端
- **多轮对话**：支持对话历史管理，自动维护最近 5 轮对话上下文
- **学科过滤**：支持按 AI、Java、大数据等学科类别筛选知识范围

### 多模态文档支持

教育文档加载器支持 PDF、Word (.docx)、PPT (.pptx)、图片 (.png / .jpg)、Markdown、Text 等格式，内置 OCR 识别，配合中文递归文本分割器实现父子块双粒度分块策略。

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+
- Redis 7.0+
- Milvus 2.5+
- CUDA 12.4+（推荐，用于 GPU 加速）

### 安装依赖

```bash
pip install -r requirments.txt
```

### 配置

编辑 `config.ini`，根据实际环境修改数据库连接和 API 密钥：

```ini
[mysql]
host = 127.0.0.1
user = root
password = 123456
database = edu_qa

[redis]
host = 127.0.0.1
port = 6379
password = 1234

[milvus]
host = 127.0.0.1
port = 19530
database_name = itcast
collection_name = edurag_final

[llm]
model = deepseek-v4-pro
dashscope_api_key = your_api_key
dashscope_base_url = https://api.deepseek.com
```

### 启动服务

```bash
# 启动 FastAPI Web 服务（含 Web 前端）
python app.py

# 或命令行交互模式
python new_main.py
```

启动后访问 `http://127.0.0.1:8000` 打开 Web 界面。

## API 接口

### 创建会话

```
POST /api/create_session
```

### 非流式查询

```
POST /api/query
```

请求体：

```json
{
    "query": "什么是人工智能？",
    "source_filter": "ai",
    "session_id": "uuid-string"
}
```

### 流式查询（WebSocket / SSE）

```
WebSocket /api/stream
```

消息类型：`start` / `token` / `end` / `error`

### 获取学科列表

```
GET /api/sources
```

### 获取 / 清除对话历史

```
GET /api/history/{session_id}
DELETE /api/history/{session_id}
```

## 工作流程

```
用户提问
    │
    ├─→ 日常问候检测 ──→ 直接返回问候语
    │
    └─→ BM25 关键词检索（MySQL + Redis 缓存）
            │
            ├─ 置信度 ≥ 0.85 ──→ 直接返回精准答案
            │
            └─ 置信度 < 0.85
                    │
                    ├─→ BERT 查询意图分类
                    │
                    ├─→ LLM 策略选择（直接/回溯/子查询/HyDE）
                    │
                    └─→ BGE-M3 Hybrid Search + BGE-Reranker
                            │
                            └─→ LLM 流式生成答案
```

## RAGAS 评估结果

| 指标 | 数值 | 说明 |
|------|------|------|
| 忠实度（Faithfulness） | 0.95 | 答案对检索上下文的忠实程度 |
| 答案相关性（Answer Relevancy） | 0.92 | 答案与问题的相关性 |
| 上下文相关性（Context Relevancy） | 0.90 | 检索上下文与问题的相关性 |
| 上下文召回率（Context Recall） | 0.93 | 检索覆盖关键信息的完整度 |

## 支持的学科领域

- AI（人工智能）
- Java（Java 编程）
- BigData（大数据）
