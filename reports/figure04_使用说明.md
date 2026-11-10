# 图四交付与使用说明

图已生成，可直接将 `figures/04_monthly_rainfall_comparison.png` 放入报告。PNG 为 2580 × 1920、300 dpi；SVG 是可缩放矢量图，字体转为路径。两份内容相同。

## 文件及用途

- `figures/04_monthly_rainfall_comparison.png`：报告插图。
- `figures/04_monthly_rainfall_comparison.svg`：缩放与排版。
- `notebooks/02_figure04_monthly_rainfall.ipynb`：中文分步骤说明、完整代码、计算结果、图片预览，推荐阅读此文件。
- `scripts/figure04_monthly_rainfall.py`：不需要 Notebook 的独立运行程序；与 Notebook 使用相同算法。
- `reports/figure04_values.csv`：实际画图的六个均值、有效年份与 Trace 误差上界。

## 统计定义与核查

严格按项目计划：香港天文台站，1991–2025 年，每年 6–8 月；比较 1991–2000 与 2016–2025，两时期各 10 个完整夏季。

程序直接读取仓库 `data/raw/` 中的三份 CSV。只有三类观测都存在、数值有效且质量标记均为 C 的完整 92 天夏季才进入分析。重复日期报错；缺失不填零；Trace 按 0 mm 近似。

先求每年每月总雨量，再求时期内同一月份总量的跨年平均。不是十年总雨量，也不是日均雨量。复算的 35 个完整夏季、105 个月总量和 6 个时期均值与仓库 `monthly_summer_metrics.csv`、`period_monthly_summary.csv` 一致。

| 月份 | 1991–2000（mm） | 2016–2025（mm） | 近期－早期（mm） |
|---|---:|---:|---:|
| 6 月 | 456.66 | 427.52 | −29.14 |
| 7 月 | 443.26 | 331.43 | −111.83 |
| 8 月 | 514.59 | 498.84 | −15.75 |

两个时期均以 8 月平均月雨量最高，近期三个夏季月份的均值均低于早期，7 月差值最大。这是描述性比较；图中未检验统计显著性，不能单凭此图推出长期趋势或原因。

每根柱的 Trace 近似误差上界为 0.125–0.285 mm，远小于两个时期的差值，不能改变比较方向。上界为 Trace 天数 × 0.05 mm ÷ 有效年份数，真实误差严格小于该上界。

配色：早期 `#246C8A`，近期 `#C05A37`。仓库尚无图三，图三的制作者应复用这两个颜色，以满足图三、四一致的要求。版式与字体参考现有图五，纵轴从 0 开始。

## 在 VS Code 中运行（可选）

不需要把代码复制到一个空文件。用 VS Code 的 File → Open Folder 打开整个项目文件夹 `ama2233-hk-summer-weather`，保持 data、scripts、notebooks、figures 同级。

### 方法一：独立 Python 脚本，最简单

本图脚本可用 Python 3.10 及以上；不需要安装原仓库整个软件包。原仓库完整数据管道另要求 Python 3.13，二者不要混淆。

在项目根目录打开 Terminal → New Terminal，运行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "matplotlib>=3.10,<4"
python scripts/figure04_monthly_rainfall.py
```

Windows 可将前两行替换为 `py -m venv .venv` 和 `.venv\Scripts\activate`，后两行相同。若 VS Code 未选中环境，按 Ctrl/Cmd+Shift+P → Python: Select Interpreter → 选择 `.venv`。

运行成功后 PNG、SVG 保存到 figures，数值表保存到 reports；程序输出核查通过提示。无需手动截图保存图形。

### 方法二：课程风格的 Notebook

1. VS Code 安装 Microsoft 的 Python 和 Jupyter 扩展。
2. 在上面已激活的环境中运行 `python -m pip install ipykernel`。
3. 打开 `notebooks/02_figure04_monthly_rainfall.ipynb`，右上角 Select Kernel 选择该环境。
4. 点击 Run All；依次完成读取、核查、汇总、绘图、保存和预览。
5. 修改后可 Restart Kernel，再 Run All；本交付已用全新命名空间按顺序执行所有代码单元并保存输出。

原仓库已配置 uv 的组员也可以使用现有环境打开此 Notebook，无需改动原数据管道。

## 资料版本与课程参考的边界

GitHub 来源：TZY-polyu/ama2233-hk-summer-weather，提交 `ba6f4368ef4813301a6951dffbf45d57dfdc07c3`。使用该版本的《项目总体计划.md》、各目录 README、全部三个现有 Notebook 和数据清洗/指标代码核对本图定义；没有用仓库外的数据替换。

课程入口：learn.polyu.edu.hk 的 AMA2233 2026 tutorials。已逐项点击附件入口。成功读取 tutorial2sol.html（Matplotlib 导入、图幅、标题、横纵轴；第 14 题以柱状图画离散概率）、tutorial3(solution).html（核密度、PP/QQ 图），以及函数说明 PDF 的单页。图四采用课程中出现的 Matplotlib，分组柱位置、数值标签和 PNG/SVG 导出是项目需要的补充实现。

浏览器未能成功下载各 .ipynb，其他 PDF 未能完整提取，因此没有声称课程全部附件已通读，也没有声称课程提供了本图的完整模板。课程私人附件不包含在公开上传包中。
