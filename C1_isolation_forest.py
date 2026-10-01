# -*- coding: utf-8 -*-
"""
C1 + C2：固定规则 + IsolationForest 对照判断
=============================================
历史数据来源：dorm-a 模拟宿舍的温湿度历史记录（默认 web/dormmate.csv）
模型：sklearn.ensemble.IsolationForest
      n_estimators=100, contamination="auto", random_state=42

判断方式：
    【固定规则】与DormMate网页（A2.html checkRecover）阈值一致：
                正常区间 温度22~28℃、湿度40~70%RH
                temp>28 → 偏热；temp<22 → 偏冷；hum>70 → 偏湿；hum<40 → 偏干
    【ML模型】  model.predict(X_new) 返回 1  = 接近常态（正常数据）
                                     -1 = 与历史明显不同（疑似异常数据）
    每条测试数据同时输出两种结果，并自动检索
    「固定规则判定正常、ML判定异常」的对照案例（找不到则如实打印说明）。

用法：
    py C1_isolation_forest.py                      # 用默认历史CSV训练并预测
    py C1_isolation_forest.py --csv 新的历史.csv   # 更换新CSV文件重新训练后预测

重要约定：
    训练数据（X_history）与待判断数据（X_new）严格分离——
    X_new 在脚本下方单独定义，绝不拼入训练集参与 fit。
"""

import argparse
import csv
import unicodedata

import numpy as np
from sklearn.ensemble import IsolationForest

# ----------------------------- 训练数据 -----------------------------
# 历史训练数据文件（dorm-a 模拟宿舍的历史温湿度记录）
DEFAULT_CSV = "web/dormmate.csv"


def load_history(csv_path):
    """读取历史CSV，提取 temperature、humidity 两列作为训练数据 X_history"""
    X_history = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                temp = float(row["temperature"])
                hum = float(row["humidity"])
            except (KeyError, ValueError, TypeError):
                continue  # 跳过字段缺失或非数字的行
            X_history.append([temp, hum])
    return np.array(X_history)


# ----------------------------- 固定规则判断 -----------------------------
def fixed_rule_judge(temp, hum):
    """DormMate网页配套的固定阈值判断（与A2.html checkRecover口径一致）
    正常区间：温度22~28℃，湿度40~70%RH
    返回：正常 / 偏热 / 偏冷 / 偏湿 / 偏干（温度异常优先于湿度异常）"""
    if temp > 28:
        return "偏热"
    if temp < 22:
        return "偏冷"
    if hum > 70:
        return "偏湿"
    if hum < 40:
        return "偏干"
    return "正常"


def pad_cn(text, width):
    """按显示宽度补齐：中文/全角字符按2列计算，保证控制台表格对齐"""
    w = sum(2 if unicodedata.east_asian_width(ch) in "FW" else 1 for ch in text)
    return text + " " * max(0, width - w)


# ----------------------------- 待判断数据 -----------------------------
# 单独定义的多组新数据（模拟新收到的宿舍温湿度报文），严禁放入训练集
# 每条：[温度(℃), 湿度(%)] + 场景说明；覆盖正常、边界、偏热、偏湿等场景，
# 用于观察固定规则与ML模型两种判断的差异
NEW_SAMPLES = [
    {"temp": 25, "hum": 55, "desc": "常温常湿"},
    {"temp": 22, "hum": 40, "desc": "正常区间边界下限"},
    {"temp": 28, "hum": 70, "desc": "正常区间边界上限"},
    {"temp": 23, "hum": 65, "desc": "区间内偏高湿"},
    {"temp": 30, "hum": 50, "desc": "偏热"},
    {"temp": 26, "hum": 85, "desc": "偏湿"},
    {"temp": 12, "hum": 15, "desc": "偏冷偏干"},
    {"temp": 25, "hum": 30, "desc": "偏干"},
]


def main():
    parser = argparse.ArgumentParser(description="C1 IsolationForest 温湿度异常检测")
    parser.add_argument("--csv", default=DEFAULT_CSV,
                        help="历史训练数据CSV路径（默认 %s）" % DEFAULT_CSV)
    args = parser.parse_args()

    # [1] 读取历史训练数据（只含CSV中的 temperature、humidity 两列）
    X_history = load_history(args.csv)
    if X_history.shape[0] == 0:
        print("[错误] %s 中没有可用的 temperature/humidity 数据" % args.csv)
        return
    print("[1] 历史训练数据：%s，共 %d 条（列：temperature, humidity）"
          % (args.csv, X_history.shape[0]))

    # [2] 用历史数据训练 IsolationForest（fit 只接收 X_history）
    model = IsolationForest(n_estimators=100, contamination="auto", random_state=42)
    model.fit(X_history)
    print("[2] 模型训练完成：IsolationForest(n_estimators=100, contamination='auto', random_state=42)")

    # [3] 组装待判断新数据（独立定义，未参与训练，与训练集严格分离）
    X_new = np.array([[s["temp"], s["hum"]] for s in NEW_SAMPLES], dtype=float)
    print("[3] 待判断数据：%d 条（脚本内单独定义，未放进训练集）" % X_new.shape[0])

    # [4] 两种方式同时判断：固定规则 + ML模型
    rule_results = [fixed_rule_judge(s["temp"], s["hum"]) for s in NEW_SAMPLES]
    preds = model.predict(X_new)              # ML：1 = 接近常态，-1 = 与历史明显不同
    scores = model.decision_function(X_new)

    # 控制台对照表格（中文按显示宽度对齐）
    print("[4] 固定规则 vs ML模型 对照表：")
    header = "序号  温度    湿度    场景              固定规则    ML结果          ML分数"
    print(header)
    print("-" * len(header))
    for i, (s, rule, pred, score) in enumerate(zip(NEW_SAMPLES, rule_results, preds, scores), 1):
        ml_text = "接近常态(1)" if pred == 1 else "明显不同(-1)"
        print("%s  %s  %s  %s  %s  %s  %.3f" % (
            pad_cn(str(i), 4),
            pad_cn("%g℃" % s["temp"], 7),
            pad_cn("%g%%" % s["hum"], 7),
            pad_cn(s["desc"], 16),
            pad_cn(rule, 10),
            pad_cn(ml_text, 14),
            score))

    # [5] 对照结论：检索「固定规则判定正常、ML判定异常」的案例
    mismatch_idx = [i for i, (rule, pred) in enumerate(zip(rule_results, preds))
                    if rule == "正常" and pred == -1]
    if mismatch_idx:
        print("[5] 对照发现：找到 %d 条「固定规则判定正常、ML判定异常」的案例：" % len(mismatch_idx))
        for i in mismatch_idx:
            s = NEW_SAMPLES[i]
            print("    - 温度 %g℃ 湿度 %g%%（%s）：固定规则=%s，ML=predict -1（与历史明显不同）"
                  % (s["temp"], s["hum"], s["desc"], rule_results[i]))
    else:
        # 如实记录：未找到该案例，并给出数据层面的原因参考
        print("[5] 对照发现：未找到「固定规则判定正常、ML判定异常」的案例（如实记录）")
        print("    本次测试数据中，所有固定规则判为正常的样本，ML模型也都判为接近常态。")
        if len(X_history) < 20:
            print("    原因参考：历史训练数据仅 %d 条，样本太少，IsolationForest 难以形成有效的异常边界。" % len(X_history))


if __name__ == "__main__":
    main()
