# Sound Voltex asphyxia Best50 Generator

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Release-v1.4.0-00f0ff?style=flat-square" alt="Release">
  <img src="https://img.shields.io/badge/BEMANI-SDVX%20EXCEED%20GEAR%20%2F%20%E2%88%87-ff2d87?style=flat-square" alt="SDVX">
  <img src="https://img.shields.io/badge/Output-1600px%20JPEG%20%2B%20HTML-10b981?style=flat-square" alt="Output">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="License">
</p>

> 专门为 BEMANI 音步游戏 **SOUND VOLTEX EXCEED GEAR / ∇** 打造的高颜值 Best 50 战绩成绩卡与交互式网页生成器。

从 [asphyxia-core](https://github.com/asphyxia-core) 氧无本地存档中提取玩家全曲目成绩，自动按 `(mid, type)` 去重并按 **VOLFORCE (VF)** 降序筛选出 Top 50 个人最佳谱面，生成 **VOLFORCE Afterglow** 结算终端风格的 1600px 高清 JPEG 战绩图，以及自包含响应式 HTML 战报。

---

## 📸 视觉预览

![B50 Preview](assets/preview_sm.jpg)

---

## ✨ 核心亮点

- 🎨 **VOLFORCE Afterglow 结算终端美学**
  - **官方 EXCEED GEAR 主视觉入画**：右侧 hero 使用带来源标注的官方 key visual，叠加黑曜石遮罩与激光环境，既保留街机现场感，又不抢数据阅读。
  - **本地 Barlow Condensed 数字体系**：VOLFORCE、分数、名次、统计全部使用窄体等宽数字，配合微软雅黑 CJK 标题，数字层级一眼可辨。
  - **Top 3 领奖台**：#01 金、#02 冰蓝、#03 铜橙三张大卡，专属描边、名次徽章与 VF 贡献条；#04–#50 进入高密度战绩跑表，#04–#10 用青色侧标延续层级。
  - **VOLFORCE 偏差频谱**：50 根柱围绕平均 VF 上下起伏，前三名金/冰/铜高亮，既是真实数据图，也是 SDVX 的声波意象。
  - **真实数据分布面板**：最后一行自动补位，展示 GRADE 构成、难度构成与 Top 3 VF 占比，全部由当前 50 条记录计算。
  - **缺省素材可降级**：移除背景图后会自动绘制原创的 SDVX 风格 ∇ 棱镜与激光背景，离线、无图也能生成完整海报。
- ⚡ **高清但轻量**
  - **1600px** 宽度、2 倍超采样后缩放，文字与封面边缘更干净；渐进式 JPEG（Quality 90）单张约 **750KB**。
- 📈 **VOLFORCE 贡献度精准分析**
  - 单曲卡片精准展示单曲 VF 及其对总 VOLFORCE 的百分比贡献（精确至小数点后 4 位，如 `250.0 ·12.3456%`）。
- 🌐 **交互式自包含 HTML 仪表盘**
  - 单文件自包含（无外部网络依赖），内嵌高压缩封面缩略图，总体积约 **460KB**。
  - 支持**实时搜索曲名**、**难度胶囊分类筛选**（ALL / NOV / ADV / EXH / MXM / INF）以及**数据表格 / 卡片网格**双视图无缝切换。
- 💡 **一键开箱即用 & 内置 Demo**
  - 双击即可在当前目录自动探测游戏文件运行；提供 `--demo` 演示模式，无需本地存档也可随时预览生成。

---

## 🎛️ 设计说明 / Design Notes

### 方向契约

> **深夜街机结算终端**：黑曜石底、青色数据光，品红/樱粉来自 EXCEED GEAR 官方主视觉；金/冰蓝/铜橙只留给 Top 3。两个 do：让数字成为最高等级、让 Top 3 拥有独立领奖台；两个 don't：彩虹霓虹、等权卡片阵列。

### 构图

```text
┌──────────────────────────────────────────────────────────────┐
│ HERO 360px                                                   │
│ 玩家 / TOTAL VOLFORCE / VF 偏差频谱     官方 EXCEED GEAR 主视觉 │
├──────────────────────────────────────────────────────────────┤
│ TOP 3 / PODIUM   #01 金 · #02 冰蓝 · #03 铜橙                 │
├──────────────────────────────────────────────────────────────┤
│ RANKS 04–50     五列 × 十行；#04–#10 青色侧标                 │
├──────────────────────────────────────────────────────────────┤
│ B50 DISTRIBUTION：GRADE / DIFFICULTY / TOP 3 SHARE           │
├──────────────────────────────────────────────────────────────┤
│ 页脚：生成日期 · 数据来源 · 美术版权                           │
└──────────────────────────────────────────────────────────────┘
```

### 色彩角色

| 角色 | 值 | 用途 |
|------|----|------|
| 底 | `#07090E` | 画布、深色环境 |
| 面 | `#0D1320` / `#111827` | 跑表卡、领奖台 |
| 数据色 | `#38E8FF` | VOLFORCE、分数、当前统计 |
| 强调色 | `#FF3D9A` | 版本标签、品红/樱粉环境光 |
| Top 1 / 2 / 3 | `#FFC857` / `#CFE8FF` / `#FF9A6B` | 领奖台描边、频谱前三柱 |
| 正文 / 次文 / 弱化 | `#F4F8FF` / `#8194AD` / `#6F8299` | 三级文字，弱化仍过 AA |
| 语义色 | GRADE 金/红/青/绿；难度 NOV/ADV/EXH/INF/MXM/ULT | 只表达等级与难度 |

### 字体与数据

- **数字 / 英文标签**：本地 Barlow Condensed（SIL OFL，400/600/700/800），窄体、等宽观感，适合名次与 VOLFORCE。
- **CJK 标题**：微软雅黑 `msyh.ttc`；两行曲名，超长自动省略。
- **2× 超采样**：所有几何与文字先画在 2 倍画布，再 LANCZOS 缩到 1600px，边缘更干净。
- **数据诚实**：所有数字来自当前记录；缺失值显示 `—`；频谱明确标注 “DEVIATION FROM AVG”；分布面板注明由上方曲目计算；官方美术在页脚署名。

---

## 🚀 快速上手

### 1. 下载可执行文件

从 [Releases](https://github.com/ChibaRie/sdvx_asphyxia_best_50/releases) 下载最新版 `SDVX_B50.exe`。

### 2. 双击运行

将 `SDVX_B50.exe` 放置于**游戏根目录**下（与 `asphyxia/` 和 `contents/` 文件夹同级），直接双击运行：

```text
📁 你的游戏根目录\
├── 📁 asphyxia\          ← 氧无服务端文件夹
├── 📁 contents\          ← 游戏资源文件夹（包含音乐与封面）
├── 📄 SDVX_B50.exe       ← 放置于此，双击运行 ✨
└── 📁 b50_output\        ← 自动生成输出目录
    ├── 🖼️ b50.jpg        # VOLFORCE Afterglow 战绩海报（1600px 宽，~750KB）
    └── 🌐 b50.html       # 交互式 HTML 仪表盘（带搜索、筛选、双视图）
```

---

## 🛠️ 命令行高级用法

支持自定义文件路径及快速生成 Demo：

```bash
# 生成内置样本数据（无需游戏存档）
SDVX_B50.exe --demo [输出目录]

# 查看命令行帮助
SDVX_B50.exe --help

# 手动指定游戏路径
SDVX_B50.exe [存档路径] [曲目数据库路径] [音乐资源目录] [输出目录]
```

### 默认路径一览

| 参数 | 默认位置 |
|------|----------|
| **玩家存档** | `./asphyxia/savedata/sdvx@asphyxia.db` |
| **曲目 MDB** | `./asphyxia/plugins/sdvx@asphyxia/webui/asset/json/music_db.json` |
| **音乐封面** | `./contents/data/music` |
| **生成目录** | `./b50_output/` |

---

## 📊 输出规格

| 项目 | 规格参数 |
|------|----------|
| **JPEG 战绩海报** | 1600 × ~2170 px，2× 超采样，渐进式 JPEG（Quality 90，~750KB） |
| **构图** | 360px Hero（官方主视觉 + 玩家/VF/偏差频谱）→ Top 3 领奖台 → #04–#50 五列跑表 → 真实数据分布面板 |
| **卡片排布** | 298 × 128 px 横向卡，100px 圆角封面，两行曲名，难度/GRADE/通关灯/分数/EX/VF/占比 |
| **数字字体** | 本地 Barlow Condensed（OFL），中文标题使用微软雅黑 |
| **HTML 仪表盘** | 单文件自包含，内嵌轻量 Base64 缩略图（~460KB），支持打印与移动端自适应 |
| **展示信息** | 封面、曲名、难度徽章、等级、SCORE、EX SCORE、GRADE、通关状态、VOLFORCE 及贡献占比 |

---

## 🏗️ 项目架构

```text
├── src/                # 核心源代码目录
│   ├── __init__.py
│   ├── gen_b50.py      # 程序入口：CLI 解析、流水线编排、Demo 模式
│   ├── b50data.py      # 数据逻辑：asphyxia DB 解析、Top 50 选取、MDB 关联与封面定位
│   ├── b50_layout.py   # 布局常量、统计、封面与共享徽章原语
│   ├── render_hero.py  # Hero：主视觉、玩家/VF、偏差频谱、统计条
│   ├── render_cards.py # Top 3 领奖台、#04–#50 跑表、分布面板
│   ├── render_png.py   # 公共 API：编排、页脚、JPEG 输出
│   ├── render_theme.py # 视觉系统：调色、字体、形状原语、环境背景
│   ├── render_html.py  # 渲染核心：自包含交互式响应式 HTML 仪表盘生成器
│   └── sample_data.py  # 内置 50 首真实样本数据集（用于 Demo 与资产生成）
├── scripts/            # 工具与维护脚本
│   └── generate_assets.py # 预览图生成工具（一键刷新 assets/）
├── tests/              # 自动化测试套件（pytest 44 项全覆盖）
│   ├── conftest.py
│   ├── test_b50data.py
│   ├── test_render_html.py
│   └── test_render_png.py
├── assets/             # 静态资产与展示样本
│   ├── fonts/          # 渲染字体（微软雅黑 + Barlow Condensed OFL）
│   ├── backgrounds/    # 官方 key visual 与来源说明
│   ├── covers/         # 样本曲目封面缓存
│   ├── b50.jpg         # 完整 50 曲输出样本
│   └── preview_sm.jpg  # README 预览图
├── requirements.txt    # Python 运行时依赖清单
├── SDVX_B50.spec       # PyInstaller 单文件打包规范
└── CHANGELOG.md        # 版本更新历史记录
```

---

## 💻 从源码构建

```bash
# 1. 克隆仓库
git clone https://github.com/ChibaRie/sdvx_asphyxia_best_50.git
cd sdvx_asphyxia_best_50

# 2. 安装依赖
pip install -r requirements.txt pyinstaller pytest

# 3. 运行测试
pytest

# 4. 执行打包
pyinstaller SDVX_B50.spec

# 5. 生成结果位于 dist/SDVX_B50.exe
```

---

## 🔗 相关项目

- [asphyxia-core](https://github.com/asphyxia-core/core) — 游戏本地服务端核心
- [sdvx@asphyxia](https://github.com/22vv0/asphyxia_plugins) — SDVX 插件与 WebUI

---

## 🎨 素材与版权

- **源代码**：MIT License。
- **Barlow Condensed**：Jeremy Tribby，SIL Open Font License 1.1，许可见 `assets/fonts/OFL-BarlowCondensed.txt`。
- **曲目封面 / SOUND VOLTEX 主视觉**：© Konami Amusement 及各自权利人。仓库内仅作为个人、非商业粉丝成绩卡生成的演示与背景素材；这些美术资源**不在 MIT 授权范围内**，请勿用于商业再分发。来源说明见 `assets/backgrounds/README.md`。
- 如果移除 `assets/backgrounds/sdvx_exceed_gear_key.jpg`，渲染器会自动降级为原创的 SDVX 风格 ∇ 棱镜背景，不影响生成。

---

## 📄 开源协议

本项目源代码采用 [MIT License](LICENSE) 授权许可。
