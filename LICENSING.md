# tical-code 代码分层授权规范 (Licensing & Code Layering Policy)

> **文档版本**: 1.0  
> **生效日期**: 2026-05-15  
> **最后更新**: 2026-05-15

---

## 1. 总体授权策略

tical-code 项目采用**分层授权**策略，根据模块的定位和商业价值选择不同的授权方式：

| 层级 | 授权方式 | 说明 |
|------|----------|------|
| **tical-code 框架** | BSL 1.1 (4年保护期) | 源码公开，禁止竞争性托管服务，4年后转 Apache 2.0 |
| **SoulAgent 协议层** | BSL 1.1 (4年保护期) | 源码公开，保护协议实现，4年后转 Apache 2.0 |
| **藏子世间 (Zishijian)** | 商业授权，不开源 | 商业产品，源码不公开 |

**关键术语说明**：
- tical-code 是 **source-available**（源码可获取）项目，**不是** OSI 认可的开源项目
- 请勿使用 "open source" 描述本项目，应使用 "source available" 或 "public source"
- BSL 1.1 保护期结束后，对应版本自动转为 Apache License 2.0

---

## 2. 开源层（Source-Available Layer）— BSL 1.1

以下模块以 BSL 1.1 授权，源码公开，允许非竞争性生产使用：

### 2.1 框架核心 (`core/`)
- `core/networking/` — 通信管理、HTTP 服务器、SSE、Socket.IO、MCP 代理
- `core/message_dispatcher.py` — 消息分发
- `core/handler_factory.py` — 处理器工厂
- `core/metrics.py` / `core/otel_metrics.py` — 可观测性指标

### 2.2 公共组件 (`common/`)
- `common/action_handler.py` — 动作处理器
- `common/action_result.py` — 动作结果
- `common/active_action_manager.py` — 活跃动作管理
- `common/message.py` / `common/message_queue.py` — 消息与队列
- `common/validator.py` — 校验器

### 2.3 工具库 (`utils/`)
- `utils/logger.py` — 日志
- `utils/manager.py` — 共享管理器
- `utils/text.py` — 文本处理
- `utils/screenshot_manager.py` — 截图管理
- `utils/file_change_tracker.py` — 文件变更追踪
- `utils/tos_manager.py` — TOS 管理
- `utils/coze_loop.py` / `utils/coze_sdk.py` — Coze SDK 适配

### 2.4 动作处理器 (`handlers/`)
- `handlers/file_action.py` — 文件操作
- `handlers/run_code_action.py` — 代码执行
- `handlers/workflow_action/` — 工作流引擎

### 2.5 LLM 适配层 (`llm/`)
- `llm/factory.py` — LLM 工厂（Provider 注册与路由）
- 各 Provider 适配器（OpenAI 兼容、Gemini、MiMo 等）

### 2.6 API 接口定义
- OpenAPI / Swagger 规范文件
- Protocol Buffers 定义（如有）
- 公共类型定义和接口抽象

### 2.7 入口与配置
- `run.py` — 应用入口
- `pyproject.toml` — 项目配置
- `install.sh` — 安装脚本

---

## 3. 闭源层（Proprietary Layer）

以下模块**不对外公开源码**，采用商业授权或未来 BSL 1.1 保护：

### 3.1 身份注册协议 (Identity Registration Protocol)
- Agent 身份创建、注册、验证流程
- 去中心化身份标识（DID）实现
- 身份证明签发与验证

### 3.2 存在证明机制 (Proof of Existence)
- 密封协议实现 (`sealed_agent`)
- 不可篡改的存在性证明生成与验证
- 时间戳与锚定机制

### 3.3 记忆协议格式 (Memory Protocol)
- Agent 记忆的编码、加密、存储格式
- 记忆宫殿 (Memory Palace) 核心引擎
- 跨平台记忆迁移协议

### 3.4 商业运营逻辑
- 计费与配额管理
- 商业授权验证
- 企业级功能（RBAC、审计日志、SLA 保障）

### 3.5 藏子世间 (Zishijian)
- 整个产品线为商业闭源产品
- 包含世界观构建引擎、命运系统、叙事引擎等
- 单独的商业授权协议

---

## 4. 第三方贡献规范

### 4.1 CLA（Contributor License Agreement）要求

**所有贡献者必须签署 CLA 后，其贡献才能被合入主分支。**

CLA 核心条款：
1. **版权授予**：贡献者授予 tical-code 项目非独占、全球性、免版税的许可，允许项目在任何授权下使用、复制、修改、分发贡献内容
2. **专利授予**：贡献者授予项目参与者专利许可
3. **原创声明**：贡献者声明其贡献为原创或已获适当授权
4. **再授权权**：贡献者同意 tical-code 可在任何授权下（包括但不限于 BSL 1.1、Apache 2.0、商业授权）再授权其贡献
5. **Mentor 声明**：如贡献者受雇于某组织，需确认其雇主允许该贡献

### 4.2 CLA 签署流程
1. 首次提交 Pull Request 时，CLA 机器人将自动检查签署状态
2. 未签署者将被引导至 CLA 签署页面
3. 签署一次即可，后续贡献无需重复签署
4. 企业贡献者需由授权代表签署企业 CLA

### 4.3 贡献类型
- **代码贡献**：Bug 修复、功能实现、性能优化等
- **文档贡献**：文档改进、翻译、示例代码等
- **Issue 报告**：Bug 报告、功能建议等（无需 CLA）

---

## 5. 商业授权

### 5.1 何时需要商业授权
- 将 tical-code 作为竞争性托管服务提供给第三方
- 在 BSL 1.1 Additional Use Grant 未覆盖的生产场景使用
- 需要闭源层模块的使用权
- 需要企业级支持、SLA 保障

### 5.2 商业授权类型

| 类型 | 适用场景 | 说明 |
|------|----------|------|
| **托管服务授权** | SaaS/PaaS 运营 | 允许将 tical-code 作为托管服务运营 |
| **企业授权** | 内部大规模部署 | 包含闭源模块使用权 + 企业级支持 |
| **OEM 授权** | 嵌入第三方产品 | 允许将 tical-code 嵌入并分发 |
| **闭源模块授权** | 特定功能需求 | 单独获取闭源层模块的使用权 |

### 5.3 联系方式
- 邮箱：licensing@tical-code.dev
- 商业授权咨询将在 48 小时内回复

---

## 6. 合规检查清单

**每次发版前，项目负责人须完成以下检查：**

### 6.1 授权合规

- [ ] 所有新增文件头部包含正确的版权和授权声明
- [ ] 新增依赖的授权协议与 BSL 1.1 兼容
- [ ] 未将闭源层代码混入开源层目录
- [ ] Third-party notices 文件已更新（如使用了新依赖）

### 6.2 代码分层

- [ ] 开源层模块未依赖闭源层模块（仅允许闭源层依赖开源层）
- [ ] API 接口定义在开源层，实现在闭源层的模式正确
- [ ] `import` 路径清晰，不存在循环依赖或越层引用

### 6.3 贡献合规

- [ ] 所有合入 PR 的贡献者已签署 CLA
- [ ] 第三方代码已标注来源和授权
- [ ] 无未经授权的代码复制

### 6.4 发版文档

- [ ] CHANGELOG 中注明授权变更（如有）
- [ ] LICENSE 文件的 Change Date 和版本号正确
- [ ] README 中的授权说明与实际一致

---

## 7. 文件头版权声明模板

### Python 源文件（开源层）
```python
# Copyright (c) 2026 tical-code Contributors
# Use of this software is governed by the Business Source License included
# in the LICENSE file and at https://mariadb.com/bsl11.
# Change Date: 2030-05-15
# On the date above, in accordance with the Business Source License,
# use of this software will be governed by the Apache License, Version 2.0.
```

### Python 源文件（闭源层）
```python
# Copyright (c) 2026 tical-code Contributors
# PROPRIETARY AND CONFIDENTIAL
# This file is part of tical-code proprietary modules.
# Unauthorized copying, distribution, or use is strictly prohibited.
# Contact: licensing@tical-code.dev for commercial licensing.
```

---

## 8. 授权策略决策树

```
新模块归属判断：
│
├─ 是否为框架基础设施（通信、调度、工具）？→ 开源层 BSL 1.1
├─ 是否为协议实现（身份、证明、记忆）？→ 闭源层
├─ 是否为 API/SDK 接口定义？→ 开源层 BSL 1.1
├─ 是否为业务逻辑（计费、运营）？→ 闭源层
├─ 是否为藏子世间产品？→ 商业闭源
└─ 不确定？→ 默认闭源层，经评估后可降级为开源层
```

---

## 9. 授权变更历史

| 日期 | 变更内容 | 版本 |
|------|----------|------|
| 2026-05-15 | 初始建立 BSL 1.1 授权体系 | v0.5 |

---

## 10. 常见问题

**Q: BSL 1.1 和开源有什么区别？**  
A: BSL 1.1 是 source-available 授权，源码公开可见可修改，但对生产使用有限制（竞争性托管服务需商业授权）。4年保护期后自动转为 Apache 2.0，成为真正的开源协议。

**Q: 我可以在公司内部使用 tical-code 吗？**  
A: 可以。内部使用（包括生产环境）不属于竞争性托管服务，完全符合 BSL 1.1 的 Additional Use Grant。

**Q: 我可以基于 tical-code 提供咨询服务吗？**  
A: 可以。咨询、培训、定制开发等服务不属于竞争性托管服务。

**Q: 我想用 tical-code 搭建一个 SaaS 平台怎么办？**  
A: 如果该 SaaS 平台与 tical-code 官方或授权合作伙伴的服务构成竞争，需要购买商业授权。非竞争性 SaaS 使用请咨询 licensing@tical-code.dev。

**Q: 4年后真的会转成 Apache 2.0 吗？**  
A: 是的，BSL 1.1 条款强制要求在 Change Date（2030-05-15）后，对应版本的代码自动以 Apache License 2.0 授权。这是 BSL 的核心保障机制。

---
**商业授权联系:** zizetu@ticalasi.com
