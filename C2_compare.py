# -*- coding: utf-8 -*-
"""
C2：固定规则 + IsolationForest 对照判断（独立执行，结果落盘）
=============================================================
- 训练集：web/dormmate.csv 全部历史数据（只读，绝不回写）
- 待测集：C1_isolation_forest.NEW_SAMPLES（脚本内独立定义，未参与 fit）
- 模型：IsolationForest(n_estimators=100, contamination="auto", random_state=42)
        （与 C1 完全一致，predict=1 接近常态 / -1 与历史明显不同）
- 输出：两种判定结果对照表格 + 「固定规则正常、ML判异常」案例检索
        结果保存到 C2_result.txt（UTF-8），dormmate.csv 全程只读不被修改
- 说明：不计算 Accuracy/F1/混淆矩阵，只保留两组判断结果对比

用法：
    py C2_compare.py
"""

import sys

import numpy as np
from sklearn.ensemble import IsolationForest

from C1_isolation_forest import (DEFAULT_CSV, NEW_SAMPLES, fixed_rule_judge,
                                 load_history, pad_cn)

OUT_PATH = "C2_result.txt"

# 案例补充说明（用于第5节案例检索的逐条解读，键为0基索引）
CASE_NOTE = {
    1: "固定规则边界角点；历史第46行同为(22,40)且被网页标为偏干，该点在历史中属偏干稀疏簇，远离常态密集区",
    2: "固定规则边界角点；其邻域是历史偏湿簇(27~29℃/70~74%)的边缘稀疏区",
    3: "固定规则区间内部；历史中温度23℃时湿度最高仅59%，(23,65)与历史联合分布明显不同，是本次最有代表性的案例",
}


def build_report():
    """生成完整报告文本（同时用于控制台打印与落盘）"""
    lines = []
    w = lines.append

    # [1] 历史训练数据：只读 CSV，待测数据不混入
    X_history = load_history(DEFAULT_CSV)
    if X_history.shape[0] == 0:
        raise SystemExit("[错误] %s 中没有可用的 temperature/humidity 数据" % DEFAULT_CSV)
    w("[1] 历史训练数据：%s，共 %d 条（列：temperature, humidity）" % (DEFAULT_CSV, X_history.shape[0]))
    w("    训练集与待测集严格分离：fit 只接收 CSV 历史数据，待判断样本不参与训练")

    # [2] 模型训练（与 C1 超参数一致）
    model = IsolationForest(n_estimators=100, contamination="auto", random_state=42)
    model.fit(X_history)
    w("[2] 模型：IsolationForest(n_estimators=100, contamination='auto', random_state=42)")
    w("    ML口径：predict=1 接近常态；predict=-1 与历史明显不同（疑似异常）")

    # [3] 待判断数据（独立定义，未参与训练）
    X_new = np.array([[s["temp"], s["hum"]] for s in NEW_SAMPLES], dtype=float)
    rule_results = [fixed_rule_judge(s["temp"], s["hum"]) for s in NEW_SAMPLES]
    preds = model.predict(X_new)
    scores = model.decision_function(X_new)
    w("[3] 待判断数据：%d 条（C1 脚本内独立定义，未放进训练集）" % X_new.shape[0])
    w("")

    # [4] 对照表格
    w("[4] 固定规则 vs ML模型 对照表：")
    header = "序号  温度    湿度    场景              固定规则    ML结果          ML分数"
    w(header)
    w("-" * len(header))
    for i, (s, rule, pred, score) in enumerate(zip(NEW_SAMPLES, rule_results, preds, scores), 1):
        ml_text = "接近常态(1)" if pred == 1 else "明显不同(-1)"
        w("%s  %s  %s  %s  %s  %s  %.3f" % (
            pad_cn(str(i), 4),
            pad_cn("%g℃" % s["temp"], 7),
            pad_cn("%g%%" % s["hum"], 7),
            pad_cn(s["desc"], 16),
            pad_cn(rule, 10),
            pad_cn(ml_text, 14),
            score))

    # [5] 案例检索：固定规则判定正常、ML判定与历史明显不同
    w("")
    w("[5] 案例检索：固定规则判定正常、ML判定与历史明显不同")
    cases = [i for i in range(len(NEW_SAMPLES))
             if rule_results[i] == "正常" and preds[i] == -1]
    if cases:
        w("    找到 %d 条案例：" % len(cases))
        for i in cases:
            s = NEW_SAMPLES[i]
            w("    - 温度 %g℃ 湿度 %g%%（%s）：固定规则=正常，ML=predict -1，score=%.3f"
              % (s["temp"], s["hum"], s["desc"], scores[i]))
            w("      %s" % CASE_NOTE.get(i, ""))
    else:
        w("    未找到此类案例（如实记录）")

    # [6] 补充观察（服务于案例寻找，非评估指标）
    total = anom = 0
    for t in np.arange(22, 28.01, 0.5):
        for h in np.arange(40, 70.01, 0.5):
            total += 1
            if model.predict([[t, h]])[0] == -1:
                anom += 1
    w("")
    w("[6] 补充观察：固定规则正常区间（22~28℃ / 40~70%%）0.5步长网格扫描共 %d 个点，" % total)
    w("    其中 %d 个被 ML 判为 -1，说明 ML 的常态区域（贴近历史密集区）明显窄于固定规则区间。" % anom)

    # [7] 落盘说明
    w("")
    w("[7] 结果已保存到 %s；%s 全程只读，未被修改。" % (OUT_PATH, DEFAULT_CSV))
    return lines


def main():
    # Windows 控制台默认 GBK，重配为 UTF-8 避免中文乱码
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    report = build_report()
    text = "\n".join(report) + "\n"

    print(text)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print("（已写入 %s，共 %d 行）" % (OUT_PATH, len(report)))


if __name__ == "__main__":
    main()
