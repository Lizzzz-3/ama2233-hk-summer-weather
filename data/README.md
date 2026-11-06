# 数据目录

- `raw/`：香港天文台官方下载的原始 CSV，不做手工修改。
- `processed/`：清洗、合并后的逐日夏季天气表和年度完整性表。
- `metrics/`：由逐日表计算的年度、月度和时期汇总指标。

所有派生文件由 `uv run hk-weather build` 从 `raw/` 重新生成。
