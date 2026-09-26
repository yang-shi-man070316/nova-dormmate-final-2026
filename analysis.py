import pandas as pd
import matplotlib.pyplot as plt

# 设置中文，防止方框
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 读取csv
df = pd.read_csv("web/dormmate.csv")

# 基础统计
count_total = len(df)
avg_temp = df["temperature"].mean()
avg_hum = df["humidity"].mean()
max_temp = df["temperature"].max()
min_temp = df["temperature"].min()
max_hum = df["humidity"].max()
min_hum = df["humidity"].min()

# 按状态统计数量
status_count = df["status"].value_counts()
# 筛选需要关注的记录（规则：温度>30℃ 或者湿度>70%）
warn_records = df[(df["temperature"] > 30) | (df["humidity"] > 70)]

# ========== 1. 状态柱状图 chart.png【优化后的代码】 ==========
plt.figure(figsize=(6, 4.5))

status_count.plot(kind="bar", color="#4A90E2")

plt.title("环境状态统计", fontsize=13, pad=12)
plt.xlabel("状态", fontsize=11)
plt.ylabel("记录条数", fontsize=11)

plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.xticks(rotation=0)

plt.tight_layout()
plt.savefig("chart.png", dpi=150)
plt.close()

# ========== 2. 温湿度趋势折线图 trend.png【优化后的代码】 ==========
plt.figure(figsize=(8, 4.5))

# 温度：橙红色；湿度：蓝绿色
plt.plot(df["time"], df["temperature"],
         color="#E63946", marker="o", linestyle="-",
         linewidth=2, markersize=6, label="温度(℃)")

plt.plot(df["time"], df["humidity"],
         color="#457B9D", marker="s", linestyle="-",
         linewidth=2, markersize=6, label="湿度(%)")

plt.title("温湿度随时间变化趋势", fontsize=13, pad=12)
plt.xlabel("时间", fontsize=11)
plt.ylabel("数值", fontsize=11)

plt.grid(True, linestyle="--", alpha=0.4)
plt.legend(loc="best", frameon=True, fontsize=10)

plt.tight_layout()
plt.savefig("trend.png", dpi=150)
plt.close()

# ========== 生成 report.html（这部分完全没变！） ==========
html_content = f"""
<html>
<head>
<meta charset="utf-8">
<title>宿舍环境统计报告</title>
</head>
<body>
<h1>宿舍环境监测统计报告</h1>
<p>总记录数：{count_total}</p>
<p>平均温度：{avg_temp:.2f} ℃</p>
<p>最高温度：{max_temp:.2f} ℃，最低温度：{min_temp:.2f} ℃</p>
<p>平均湿度：{avg_hum:.2f} %</p>
<p>最高湿度：{max_hum:.2f} %，最低湿度：{min_hum:.2f} %</p>

<h2>需要关注的记录</h2>
{warn_records.to_html(index=False)}

<h2>环境状态统计柱状图</h2>
<img src="chart.png" width="600">

<h2>温湿度趋势折线图</h2>
<img src="trend.png" width="700">
</body>
</html>
"""

with open("report.html","w",encoding="utf-8") as f:
    f.write(html_content)

print("分析完成！已经生成 report.html、chart.png 和 trend.png")