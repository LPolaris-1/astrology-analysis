# astrology-analysis

Deterministic Western tropical natal-chart calculation and evidence-led deep interpretation for Codex.

这是一个面向 Codex 的西方占星本命盘 Skill。它把“精确排盘”和“解释写作”严格分层：先使用 Swiss Ephemeris 生成并验证唯一的 `chart_data.json`，再从盘面证据出发分析人格、认知、行动、家庭、社群、事业、资源、关系与潜意识。

> Astrology is treated here as an interpretive tradition, not demonstrated scientific causation. The Skill describes tendencies and conditions rather than fate.

## 核心特点

- **确定性排盘**：热带黄道，默认 Placidus 宫制；支持 Whole Sign。
- **硬性精度门禁**：必须使用本地 Swiss Ephemeris `.se1`，不接受静默退回 Moshier。
- **出生时间稳定性审计**：按时间来源给出的误差区间重新采样，分别检查上升、中天、宫头、行星宫位、相位、日夜盘和福点。
- **盲审优先**：先只读取 `chart_data.json` 建立证据矩阵，再参考用户反馈；禁止用经历反向改写星盘。
- **整盘综合**：优先处理命主星、日月升中天、守护星链、相位网络、日夜盘、尊贵与失势、元素和模式，而不是拼接“太阳／月亮／上升”模板。
- **可校正输出**：主要判断都能回指盘面证据，并保留反证、适用条件、可能表现和行动建议。
- **三种交付模式**：单项问答、完整 Markdown、可打印的响应式 HTML 浏览器报告。

## 工作流程

```text
出生信息
  ↓
时区、坐标与时间精度标准化
  ↓
Swiss Ephemeris 排盘 + 硬性校验
  ↓
时间扰动与稳定性审计
  ↓
canonical chart_data.json
  ↓
盲审证据矩阵
  ↓
整盘架构 → 生活领域 → 技术附录
  ↓
用户验证与修正日志
```

当用户要求 HTML 或浏览器报告时，额外执行：

```text
代表性样张 → 浏览器渲染验收 → 完整报告
             → 桌面端检查 → 窄屏检查 → 结构完整性检查
```

## 完整报告结构

1. 审计范围、边界与五项可信度
2. 核心结论与整盘命题
3. 整盘底层架构
4. 人格与情绪调节
5. 思维、沟通与学习
6. 行动、冲突、边界与恢复
7. 家庭与私人根基
8. 创造、兴趣、友谊与社群
9. 事业、工作系统与公共角色
10. 金钱、个人资源、共享资源与风险
11. 感情、亲密、信任与修复
12. 独处、潜意识、休息与精神世界
13. 宫轴综合与逐星角色审计
14. 优势、风险、行动建议与技术附录

主要判断遵循以下证据链：

```text
结论 → 盘面证据 → 约束或反证 → 可能表现 → 实际建议
```

## 目录结构

```text
astrology-analysis/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── birth_to_chart.py
│   ├── natal_pipeline.py
│   ├── self_test.py
│   └── ephe/                 # 本地放置 .se1；仓库不分发
├── references/
├── licenses/
├── requirements.txt
└── README.md
```

## 安装

### 1. 克隆到 Codex Skill 目录

```powershell
git clone https://github.com/LPolaris-1/astrology-analysis.git "$env:USERPROFILE\.codex\skills\astrology-analysis"
Set-Location "$env:USERPROFILE\.codex\skills\astrology-analysis"
```

如果目标目录已经存在，先按你自己的 Skill 管理流程归档和审核；不要直接覆盖。

### 2. 安装 Python 依赖

要求 Python 3.10 或更高版本：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. 准备 Swiss Ephemeris 数据

出于体积和许可边界考虑，仓库不提交 `.se1` 文件。请从 [Astrodienst Swiss Ephemeris](https://www.astro.com/swisseph/) 的官方分发渠道获取以下文件，并放入 `scripts/ephe/`：

- `sepl_18.se1`
- `semo_18.se1`
- `seas_18.se1`

缺少这些文件时，自检会拒绝通过；这是精度门禁，不是可忽略警告。

### 4. 自检

```powershell
python -X utf8 scripts/self_test.py
```

预期结果应包含：

```text
PASS: astrology-analysis self-test
backend=Swiss Ephemeris .se1
```

## 排盘示例

创建 `input.json`：

```json
{
  "subject": "example",
  "date": "2000-01-01",
  "time": "12:34",
  "location": {
    "label": "City, Country",
    "lat": 0.0,
    "lon": 0.0,
    "timezone": "Etc/UTC"
  },
  "house_system": "Placidus",
  "time_precision": {
    "uncertainty_minutes": 5,
    "source": "birth certificate"
  },
  "tradition_mode": "blended",
  "tone": "practical"
}
```

运行：

```powershell
python -X utf8 scripts/natal_pipeline.py --input input.json --output chart_data.json
```

只有当 `validation.status` 为 `passed` 时才能进入解释阶段。报告必须读取 `chart_data.json`，不得凭记忆重算星位、宫位、尊贵状态或相位。

## 出生时间校准与跨体系边界

如果出生时间来自吠陀占星校准、出生证明或其他外部过程，只把它记录为输入来源：

- 西占必须独立重新计算；
- 按合理误差区间检查西占时间敏感因素；
- 不把吠陀占星规则、分盘、宿或大运混入西占证据；
- 不因为某个时间“解释更好听”就选择该时间。

## 反馈与修正

深度报告完成后，可把主要判断标记为：

- `confirmed`
- `partly confirmed`
- `contradicted`
- `unknown`

反馈可以调整权重和表现语言，但不能改写确定性天文数据。出生日期、时间、时区、坐标、黄道或宫制发生变化时，必须生成新的 canonical 版本并重新计算。

## 隐私

不要提交：

- 真实姓名、生日、出生地点或个人经历；
- `input.json`、`chart_data.json`、HTML/PDF报告或修正日志；
- `.env`、令牌、Cookie、SSH配置或本机绝对路径；
- Skill staging、归档、注册表和运行缓存。

## 许可

本仓库包含不同许可边界：

- 使用 `pyswisseph`／Swiss Ephemeris 的计算部分须遵守 GNU AGPL-3.0，或由使用者取得 Astrodienst 的专业许可；
- 解释资料按 `licenses/interpretive-resources-MIT.txt` 及来源权利台账所述使用；
- Swiss Ephemeris 的版权、数据和双许可说明见 `licenses/`。

这不是法律意见。重新分发或商业使用前，请自行核对相应许可条款。

## 项目状态

当前范围仅限西占本命盘。不包含流年、推运、合盘、卜卦、择日、吠陀占星、中国命理或确定性事件预测。
