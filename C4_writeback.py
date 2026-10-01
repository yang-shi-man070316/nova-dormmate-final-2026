# -*- coding: utf-8 -*-
"""
C4：ML 判断结果回写 DormMate + 保留不理想案例
================================================
- 读 web/dormmate.csv（只读）→ 训练 IsolationForest（与 C1~C3 同超参）
- 对 CSV 每行做「固定规则 + ML」双重判定，回写到 web/dormmate_ml_results.csv
  （新增独立结果文件，供 DormMate 前端使用；dormmate.csv 主数据保持只读不修改）
- 不理想案例（22℃/40%：训练集内的点却被判离群）以文字说明保留在 report.html 的
  「ML 判断不理想案例」章节

用法：
    py C4_writeback.py
"""

import csv
import sys

import numpy as np
from sklearn.ensemble import IsolationForest

from C1_isolation_forest import DEFAULT_CSV, fixed_rule_judge, load_history

OUT_PATH = "web/dormmate_ml_results.csv"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    # 训练（与 C1~C3 同一套超参）
    X_history = load_history(DEFAULT_CSV)
    model = IsolationForest(n_estimators=100, contamination="auto", random_state=42)
    model.fit(X_history)

    # 逐行双重判定并回写
    rows = []
    with open(DEFAULT_CSV, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                t = float(row["temperature"])
                h = float(row["humidity"])
            except (KeyError, ValueError, TypeError):
                continue
            pred = int(model.predict([[t, h]])[0])
            score = round(float(model.decision_function([[t, h]])[0]), 3)
            rows.append([row.get("time", ""), t, h, row.get("status", "").strip(),
                         fixed_rule_judge(t, h), pred, score])

    with open(OUT_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "temperature", "humidity", "csv_status",
                    "rule_status", "ml_prediction", "ml_score"])
        w.writerows(rows)

    print("[C4] 已回写 %d 条双重判定结果到 %s" % (len(rows), OUT_PATH))
    print("[C4] %s 主数据全程只读，未被修改" % DEFAULT_CSV)

    # 保留的不理想案例（正反对照，详见 report.html C4 章节）
    # 案例一：22℃/40%（训练集内第46行却被判离群，ML偏严）
    # 案例二：20℃/44%（固定规则判偏冷，ML却判接近常态，ML偏松）
    for t_case, h_case, tag in [(22, 40, "案例一(ML偏严)"), (20, 44, "案例二(ML偏松)")]:
        case = [r for r in rows if r[1] == t_case and r[2] == h_case]
        if case:
            r = case[0]
            print("[C4] 保留案例 %s：%s 温度 %g℃ 湿度 %g%% | CSV旧状态=%s | "
                  "固定规则=%s | ML=%s score=%s"
                  % (tag, r[0], r[1], r[2], r[3], r[4],
                     "异常(-1)" if r[5] == -1 else "接近常态(1)", r[6]))


if __name__ == "__main__":
    main()
