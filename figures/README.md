# 图表

第三步的图 5 已完成；图 1–4 待其他组员制作。

## 图 5：夏季温度与降雨量关联

- [高清 PNG](05_temperature_rainfall_scatter.png)：300 dpi，2580 × 1920 像素，可直接放入报告。
- [SVG 矢量图](05_temperature_rainfall_scatter.svg)：可缩放，字体已转为路径以便跨设备使用。
- [绘图 Notebook](../notebooks/02_figure05_temperature_rainfall.ipynb)：从现有年度指标重建这张图。

数据为香港天文台站 1991–2025 年每年 6–8 月的 35 个完整夏季。横轴为夏季总雨量（mm），纵轴为夏季平均气温（°C），同一年对应一个点；输入为 `data/metrics/annual_summer_metrics.csv`。

拟合线为带截距的普通最小二乘（OLS）：以雨量解释温度，仅覆盖实际观测雨量范围。它展示未经去趋势的线性关联，不能解释为因果。第四步的去趋势相关、不确定性和异常年份影响分析另行开展。

在项目根目录重新生成：

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/02_figure05_temperature_rainfall.ipynb
```
