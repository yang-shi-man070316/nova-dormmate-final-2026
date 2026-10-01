# -*- coding: utf-8 -*-
"""
C3：生成 ML 辅助判断结果文件（JSON 数据），供 report.html 静态读取展示
=======================================================================
流程（更换新 CSV 数据后重复执行即可刷新页面）：
    1. 替换/更新 web/dormmate.csv
    2. 运行：py C3_generate_report.py
       → 用新历史数据重新训练 IsolationForest（与 C1/C2 同超参），
         重新计算「固定规则 + ML」两种判定，写出 report_data.js
    3. 浏览器刷新 report.html（Ctrl+F5），ML 模块即展示最新结果

口径与数据分离原则（沿用 C2）：
    - 固定规则：script.js 现行阈值（22~28℃ / 40~70%，温度优先）
    - ML：IsolationForest(n_estimators=100, contamination='auto', random_state=42)
          predict=1 接近常态；predict=-1 与历史明显不同
    - 回顾性对照：CSV 每行历史数据做两种判定（模型基于全量历史训练，
      属历史回顾打分，页面已标注）
    - 待测样本对照：C1 的 NEW_SAMPLES 独立定义、未参与 fit，与 C2 一致
不新增后端/数据库/实时服务：report.html 以 <script src="report_data.js"> 方式
加载数据（file:// 双击打开即可），dormmate.csv 全程只读。

用法：
    py C3_generate_report.py
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone

import numpy as np
from sklearn.ensemble import IsolationForest

from C1_isolation_forest import (DEFAULT_CSV, NEW_SAMPLES, fixed_rule_judge,
                                 load_history)
from C2_compare import CASE_NOTE

OUT_PATH = "report_data.js"   # 与 report.html 同目录（仓库根目录）
N_LATEST = 20                 # 页面展示的最新历史条数


def build_payload(csv_path=DEFAULT_CSV):
    """训练 + 双重判定，组装成网页数据（纯 dict，可直接 JSON 序列化）"""
    # [1] 历史训练数据（只读 CSV，待测样本不混入）
    X_history = load_history(csv_path)
    if X_history.shape[0] == 0:
        raise SystemExit("[错误] %s 中没有可用的 temperature/humidity 数据" % csv_path)

    # [2] 训练模型（与 C1/C2 超参数一致）
    model = IsolationForest(n_estimators=100, contamination="auto", random_state=42)
    model.fit(X_history)

    # [3] 回顾性对照：CSV 每行（含原始 status 列）做固定规则 + ML 判定
    history_rows = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                t = float(row["temperature"])
                h = float(row["humidity"])
            except (KeyError, ValueError, TypeError):
                continue
            pred = int(model.predict([[t, h]])[0])
            history_rows.append({
                "time": row.get("time", ""),
                "temperature": t,
                "humidity": h,
                "csv_status": row.get("status", "").strip(),
                "rule": fixed_rule_judge(t, h),
                "ml": pred,
                "ml_score": round(float(model.decision_function([[t, h]])[0]), 3),
            })

    # [4] 待测样本对照：NEW_SAMPLES 独立定义、未参与 fit（与 C2 同口径）
    X_new = np.array([[s["temp"], s["hum"]] for s in NEW_SAMPLES], dtype=float)
    preds = model.predict(X_new)
    scores = model.decision_function(X_new)
    test_rows = []
    for i, s in enumerate(NEW_SAMPLES):
        test_rows.append({
            "temp": s["temp"],
            "hum": s["hum"],
            "desc": s["desc"],
            "rule": fixed_rule_judge(s["temp"], s["hum"]),
            "ml": int(preds[i]),
            "ml_score": round(float(scores[i]), 3),
        })

    # [5] 案例检索：固定规则正常、ML 判异常（与 C2 第5节同口径）
    cases = []
    for i, row in enumerate(test_rows):
        if row["rule"] == "正常" and row["ml"] == -1:
            cases.append({
                "temp": row["temp"],
                "hum": row["hum"],
                "desc": row["desc"],
                "ml_score": row["ml_score"],
                "note": CASE_NOTE.get(i, ""),
            })

    # [6] 补充观察：固定规则正常区间网格扫描（服务于案例解读）
    total = anom = 0
    for t in np.arange(22, 28.01, 0.5):
        for h in np.arange(40, 70.01, 0.5):
            total += 1
            if model.predict([[t, h]])[0] == -1:
                anom += 1

    return {
        "generated_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        "csv": csv_path,
        "model": "IsolationForest(n_estimators=100, contamination='auto', random_state=42)",
        "train_rows": X_history.shape[0],
        "history": history_rows[-N_LATEST:],   # 页面展示最新 N 条（时间正序）
        "test_samples": test_rows,
        "cases": cases,
        "grid": {"total": total, "anomaly": anom},
    }


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="C3 生成 report.html 的 ML 辅助判断数据")
    parser.add_argument("--csv", default=DEFAULT_CSV,
                        help="历史训练数据CSV路径（默认 %s），换新数据后重跑本脚本即可刷新页面" % DEFAULT_CSV)
    args = parser.parse_args()

    payload = build_payload(args.csv)
    body = json.dumps(payload, ensure_ascii=False, indent=2)

    header = (
        "// 由 C3_generate_report.py 自动生成，请勿手改。\n"
        "// 更换 CSV 数据后运行：py C3_generate_report.py，再刷新 report.html。\n"
        "// 生成时间：%s\n" % payload["generated_at"]
    )
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        # 用 window.REPORT_DATA 显式挂载（const 顶层声明不会成为 window 属性，页面取不到）
        f.write(header + "window.REPORT_DATA = " + body + ";\n")

    print("[C3] 训练行数：%d，回顾对照：%d 条，待测样本：%d 条，案例：%d 条"
          % (payload["train_rows"], len(payload["history"]),
             len(payload["test_samples"]), len(payload["cases"])))
    print("[C3] 已写入 %s，浏览器刷新 report.html 即可看到最新结果" % OUT_PATH)
    print("[C3] %s 全程只读，未被修改" % args.csv)


if __name__ == "__main__":
    main()
