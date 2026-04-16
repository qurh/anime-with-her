# AI 配音导演台整合设计 v2.1

## 1. 文档信息

- 日期：2026-04-16
- 状态：实施计划前的整合设计基线
- 目的：把旧版 AI 中配落地文档中的工程化内容，整合进新的 `AI 配音导演台` 产品方案
- 后续用途：作为新版实施计划的唯一设计输入

## 2. 整合结论

当前项目的最终产品形态确定为：

`面向整季角色资产沉淀、按单集生产的 AI 配音导演台`

旧文档中的 `分层重建式 pipeline`、`模块边界`、`状态机`、`质量控制点`、`缓存/重跑/复核机制` 都应保留。  
但旧文档中的“离线批处理工具”定位需要调整为“导演台优先”的产品形态。

整合后的系统不是单纯跑完一条自动流水线，而是：

1. 系统自动完成重体力分析。
2. 人在关键节点确认角色和表演方向。
3. 系统基于确认后的角色资产生成整集初版。
4. 人只精修关键片段。
5. 所有有效修正回流到季级角色资产中。

## 3. 旧文档保留价值

### 3.1 应完整吸收的内容

以下内容与新方向高度一致，应进入最终实施设计：

1. `分层重建式 pipeline`
   先拆解角色、文本、节奏、情绪、时长，再用中文重建目标配音。

2. `多模型协作`
   不用一个大模型包打天下。LLM 负责翻译、改写、总结和质检，音频/视觉/声学任务交给专用模型。

3. `阶段可缓存、可回溯、可替换、可重跑`
   每个阶段必须有清晰输入、输出、状态和错误记录。

4. `质量控制点`
   音频分离、角色归类、ASR 对齐、中文台词、TTS 合成、成片试听都需要质量检测。

5. `关键片段人工精修`
   只把低置信片段、名场面、情绪高峰句、主角关键句推给人工。

### 3.2 需要调整后吸收的内容

以下内容有价值，但不能原样采用：

1. `MVP 路线图`
   原文档强调先跑通自动闭环。新方案应改为先实现“角色分析确认点”，再整集生成。

2. `项目模型`
   原文档偏单项目/单集目录。新方案应升级为：
   `series -> season -> episode -> segment -> render_version`

3. `角色资产`
   原文档偏 voice profile。新方案应升级为：
   `series_character -> season_character_profile -> character_style_card`

4. `人工复核`
   原文档把人工复核作为后置 QA。新方案应前置为关键产品流程：角色确认后才能进入整集生成。

5. `目录结构`
   原文档的 `src/modules` 思路可以借鉴，但当前项目应继续采用 monorepo：
   `apps/backend + apps/worker + apps/web`

### 3.3 不建议采用的内容

以下内容不作为近期主线：

1. 一开始做完整 DAW 式音频工作站。
2. 一开始做大规模分布式多机并发。
3. 一开始追求影视级逐帧口型同步。
4. 一开始承诺所有角色全自动高精度命名。
5. 一开始以整季批量无人值守生产为默认模式。

## 4. 最终业务主轴

### 4.1 内容层级

```text
series
  -> season
    -> episode
      -> segment
        -> render_version
```

含义：

1. `series`：整部动漫。
2. `season`：某一季，是角色资产主要沉淀单位。
3. `episode`：默认生产单位。
4. `segment`：一句或一段台词。
5. `render_version`：单集成片版本。

### 4.2 角色资产层级

```text
series_character
  -> season_character_profile
    -> character_style_card
    -> voice_sample_candidate
    -> performance_reference_clip
```

含义：

1. `series_character` 解决“这个角色是谁”。
2. `season_character_profile` 解决“这一季这个角色怎么说、怎么演”。
3. `character_style_card` 是中文改写与 TTS 控制的核心依据。
4. `voice_sample_candidate` 用于保存候选音色样本与质量分。
5. `performance_reference_clip` 用于保存代表性表演片段。

## 5. 最终工作流

### 5.1 单集生产，两段式流程

每集固定采用两段式流程：

```text
角色分析阶段
  -> 人工确认
  -> 整集生成阶段
  -> 关键片段精修
  -> 发布版本
```

### 5.2 阶段一：角色分析阶段

系统自动执行：

1. 视频导入与标准化
2. 音轨提取
3. 人声/BGM/音效分离
4. VAD 切句
5. 说话人分离
6. 角色聚类与季级角色匹配
7. ASR 与时间对齐
8. 候选音色样本抽取
9. 代表片段筛选
10. 角色表演设定卡初稿生成

阶段输出后必须暂停，进入人工确认。

### 5.3 人工确认点

人工需要确认：

1. 主要角色是否识别正确。
2. 角色是否正确匹配到本季既有角色档。
3. 候选样本是否干净。
4. 代表片段是否能体现角色。
5. 角色表演设定卡初稿是否符合角色理解。

确认后，结果写入 `season_character_profile`。

### 5.4 阶段二：整集生成阶段

系统基于已确认角色资产执行：

1. 原文台词校对
2. 中文语义翻译
3. 中配台词改写
4. 逐句表演模板生成
5. 可控 TTS 合成
6. 时长适配
7. 分轨混音
8. 初版质检
9. 输出单集成片版本

## 6. 模块整合方案

旧文档中的 12 个模块可保留，但需要重新组织为导演台系统中的 5 个域。

### 6.1 资产域

对应模块：

1. `media_ingest`
2. `voice_profile`
3. 对象存储
4. 角色资产数据库

负责：

1. 输入素材管理
2. 角色资产管理
3. 样本与代表片段管理
4. 成片版本资产管理

### 6.2 分析域

对应模块：

1. `audio_separation`
2. `speaker_role`
3. `asr_align`
4. `prosody_emotion`

负责：

1. 拆音轨
2. 分角色
3. 识别台词与时间轴
4. 提取表演特征

### 6.3 生成域

对应模块：

1. `dub_script`
2. `tts_synthesis`
3. `timing_adapter`
4. `mix_master`

负责：

1. 中文配音文案
2. 角色化语音生成
3. 时长适配
4. 混音成片

### 6.4 审校域

对应模块：

1. `qa_review`
2. 角色确认台
3. 片段精修台
4. 版本对比页

负责：

1. 角色分析确认
2. 问题片段标记
3. A/B 候选试听
4. 人工修改回流

### 6.5 编排域

对应模块：

1. `workflow_orchestrator`
2. 队列抽象
3. 阶段状态机
4. 成本与日志系统

负责：

1. 阶段调度
2. 缓存重跑
3. 失败恢复
4. 任务审计
5. 版本 lineage

## 7. 工程形态

当前项目应继续采用 monorepo，并升级为以下结构：

```text
anime-with-her/
├─ apps/
│  ├─ backend/      # 编排 API、资产元数据、版本、审校状态
│  ├─ worker/       # 分析与生成 pipeline 执行器
│  └─ web/          # AI 配音导演台
├─ docs/
│  ├─ requirements/
│  ├─ architecture/
│  ├─ design/
│  └─ plans/
├─ configs/         # pipeline/model/storage/prompt 配置
├─ scripts/         # 初始化、运行、重跑、导出、清理
├─ data/
│  ├─ library/      # series/season 级资产
│  ├─ episodes/     # episode 工作目录
│  ├─ cache/        # 阶段缓存
│  └─ exports/      # 成片输出
├─ models/
├─ logs/
└─ tests/
```

说明：

1. `apps/backend` 不直接跑重模型，只负责编排、元数据和 API。
2. `apps/worker` 承载离线 pipeline。
3. `apps/web` 是产品核心，需要优先支持角色确认与片段精修。
4. `configs/prompts` 必须独立，不能把提示词硬编码在业务代码里。

## 8. 数据目录建议

### 8.1 季级资产目录

```text
data/library/{series_id}/{season_id}/
├─ characters/
│  └─ {character_id}/
│     ├─ profile.json
│     ├─ style_card.json
│     ├─ voice_samples/
│     ├─ reference_clips/
│     └─ embeddings/
└─ season_meta.json
```

### 8.2 单集工作目录

```text
data/episodes/{episode_id}/
├─ input/
├─ analysis/
│  ├─ separation/
│  ├─ speaker_role/
│  ├─ asr_align/
│  ├─ character_candidates.json
│  └─ analysis_review.json
├─ generation/
│  ├─ dub_script/
│  ├─ segment_direction/
│  ├─ tts_segments/
│  ├─ timing/
│  └─ mix/
├─ review/
│  ├─ qa_flags.json
│  ├─ manual_review_queue.json
│  └─ candidate_compare.json
├─ output/
└─ logs/
```

## 9. 状态机与队列

### 9.1 阶段状态

统一阶段状态采用：

```text
pending
running
success
failed
skipped
needs_review
approved
rejected
```

相比旧文档，新增：

1. `approved`
   人工确认通过。

2. `rejected`
   人工确认不通过，需要重跑或修正。

### 9.2 任务队列

首版可以先用本地队列或数据库表模拟，但代码结构保留队列抽象：

```text
episode_queue
stage_queue
segment_queue
review_queue
export_queue
```

### 9.3 关键暂停点

系统必须支持以下暂停点：

1. 角色分析完成后，进入 `needs_review`。
2. 人工确认通过后，进入 `approved`。
3. 才允许开始整集生成。

## 10. 质量控制体系

旧文档的 6 个质量控制点保留，并适配导演台流程：

1. `音频分离质检`
   检查人声是否干净，BGM/SFX 是否可用于后续混音。

2. `角色归类质检`
   检查角色聚类是否拆错或合错。

3. `ASR 与对齐质检`
   检查台词文本和时间轴是否可用。

4. `中配台词质检`
   检查中文是否自然、是否像角色会说的话。

5. `TTS 合成质检`
   检查音色稳定、情绪表达、爆音、机械感和时长偏差。

6. `成片试听质检`
   检查整体可看性、混音协调性和口型违和度。

新增导演台指标：

1. `character_confirmation_rate`
   角色分析一次通过率。

2. `style_card_edit_distance`
   自动设定卡被人工修改的幅度。

3. `key_segment_regeneration_rate`
   关键片段重生成比例。

4. `manual_fix_reuse_rate`
   人工修正回流后被后续片段复用的比例。

## 11. MVP 策略调整

旧路线图是：

`先跑通自动闭环 -> 再补角色一致性 -> 再补表演复刻`

新路线应调整为：

`先搭导演台骨架 -> 先实现角色分析确认点 -> 再跑整集生成闭环 -> 再做关键片段精修`

推荐 MVP 阶段范围：

1. 一部动漫的一季资产结构。
2. 单集生产。
3. 2 到 4 个主要角色。
4. 非重叠对话优先。
5. 角色分析后必须人工确认。
6. 整集生成后支持关键片段重生成。
7. 先不追求影视级口型同步。

## 12. 实施计划应遵循的阶段

后续实施计划建议拆成 6 个阶段：

1. `Phase 1：工程骨架与资产模型`
   建立 series/season/episode/character/segment/version 数据模型、配置体系、状态机和目录结构。

2. `Phase 2：角色分析阶段`
   打通导入、分离、说话人、ASR、候选样本、设定卡初稿与人工确认。

3. `Phase 3：整集生成阶段`
   打通中文改写、表演模板、TTS、时长适配、混音输出。

4. `Phase 4：片段精修阶段`
   支持问题片段筛选、文案修改、表演修改、换样本、单句重生成。

5. `Phase 5：版本与资产回流`
   支持版本对比、发布版本、人工修改回流到季级角色资产。

6. `Phase 6：质量评估与样片收口`
   形成可连续观看样片、QA 报告和下一轮优化清单。

## 13. 最终整合判断

旧文档的最大价值在工程落地，不在产品定位。  
新的最佳方案应把两者合并：

`用旧文档的分层 pipeline 和工程治理能力，承载新的 AI 配音导演台产品形态。`

最终系统要做到：

1. 不是黑盒批处理。
2. 不是重型 DAW。
3. 是围绕角色、片段、版本构建的轻导演台。
4. 单集生产，整季养角色。
5. 表演复刻优先，音色相似为辅。
6. 角色先确认，再整集生成。
7. 关键片段精修，修正结果回流资产。
