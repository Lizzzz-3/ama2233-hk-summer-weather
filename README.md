# 香港夏季高温与降雨分析

AMA2233 Data Analytics and Visualization 课程小组项目。

研究题目：**香港夏季的高温与降雨如何变化——长期趋势与季节分布分析**。

## 当前计划

请先阅读 [项目总体计划](项目总体计划.md)。当前范围为香港天文台站1991–2025年、每年6–8月，准备分析长期趋势、月份分布和温度与降雨的关联。

计划制作五张核心图：

1. 夏季平均气温年度趋势。
2. 夏季总降雨量年度趋势。
3. 早期与近期各月平均气温对比。
4. 早期与近期各月平均降雨量对比。
5. 夏季温度与降雨量关联散点图。

数据尚未分析，仓库中的计划不代表实际研究结果。

## 当前进度

项目总体计划的前两步已经实现：

- 三份香港天文台原始日数据已保存到 `data/raw/`。
- 已完成 1991–2025 年 6–8 月数据的清洗、日期合并和完整性检查。
- 已生成年度、月度、早期和近期汇总指标。
- `notebooks/01_data_preparation_and_metrics.ipynb` 可以从原始 CSV 重建全部表格。
- 第三步的图 5（温度与降雨量关联散点图及拟合线）已完成，见 `figures/05_temperature_rainfall_scatter.png`；图 2 已有图像和程序；图 4 已完成，图 1、3 待制作。

## 运行方法

需要 Python 3.13 和 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync --all-groups
uv run hk-weather build
```

生成文件位于 `data/processed/` 和 `data/metrics/`。运行测试和质量检查：

```bash
uv run pytest
uv run ruff check .
uv run basedpyright
```

只重新生成图 5（读取现有年度指标，不重建数据表）：

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/02_figure05_temperature_rainfall.ipynb
```

也可在 Jupyter 中打开该 Notebook，从头运行。输出为 `figures/05_temperature_rainfall_scatter.png`（300 dpi）和同名 SVG 矢量图。图表说明见 [figures/README.md](figures/README.md)。

只重新生成图 4（从仓库原始数据复算并核对月度指标）：

```bash
uv run python scripts/figure04_monthly_rainfall.py
```

也可打开 `notebooks/02_figure04_monthly_rainfall.ipynb` 点击 Run All。输出为 `figures/04_monthly_rainfall_comparison.png`（300 dpi）和同名 SVG；详见 [图四运行说明](reports/figure04_使用说明.md)。

## 目录结构

| 目录 | 用途 |
| --- | --- |
| `data/raw/` | 香港天文台原始 CSV |
| `data/processed/` | 清洗合并后的逐日表与完整性表 |
| `data/metrics/` | 年度、月度和时期汇总指标 |
| `notebooks/` | 可复现分析 Notebook |
| `figures/` | 后续五张核心图 |
| `reports/` | 论文、结果摘要和视频材料 |
| `src/` | 数据处理代码 |
| `tests/` | 单元与端到端测试 |

## 一起修改

组员可以直接在GitHub网页上操作。尚未添加为协作者时，按以下步骤提交修改：

1. 登录自己的GitHub账号，打开[项目总体计划](项目总体计划.md)。
2. 点击文件右上角的铅笔按钮 **Edit this file**；如果出现 **Fork this repository**，点击它，在自己的账号下建立仓库副本。
3. 修改文字后，点击 **Preview** 检查格式。
4. 点击 **Commit changes…**／**Propose changes**，填写简短说明，例如“补充雨量数据处理方法”，并确认提交。
5. 按页面提示点击 **Create pull request**，填写标题并确认，把修改申请提交给原仓库。
6. 仓库管理员查看后点击 **Merge pull request**，修改才会进入大家共用的主仓库。

Pull Request（PR）就是“请把我的修改合并到原仓库”的申请。只在自己的Fork中保存，还不会更新原仓库。

如果已被添加为协作者，可以直接在原仓库编辑并提交；较大修改也可通过新分支和PR讨论。每次修改前先查看原仓库的最新版本，尽量避免多人同时改同一段。

修改范围、指标或图表时，请同步更新项目总体计划，并在提交说明中写清改动。操作参考[GitHub官方文件编辑说明](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)。

## 公开数据

- [香港天文台每日气温数据](https://data.gov.hk/en-data/dataset/hk-hko-rss-daily-temperature-info-hko)
- [香港天文台每日总降雨量](https://data.gov.hk/en-data/dataset/hk-hko-rss-daily-total-rainfall)
