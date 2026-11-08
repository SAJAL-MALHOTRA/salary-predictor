"""
generate_evaluation_plots.py -- Generate publication-grade diagnostic plots
for model evaluation, calibration, residual distributions, and segment error analysis.

Outputs saved to salary-predictor/assets/:
- calibration_plot.png: Actual vs Predicted scatter with y=x reference line
- residual_distribution.png: Distribution of residuals (y - y_hat) with KDE
- segment_error_analysis.png: Segment-level MAE by Role Family and Seniority Level
- model_evaluation_dashboard.png: Combined 2x2 executive diagnostic dashboard
"""

from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# Set high-DPI style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#cbd5e1",
    "axes.linewidth": 1.2,
    "grid.color": "#f1f5f9",
    "grid.linestyle": "--",
    "grid.alpha": 0.8,
    "figure.titlesize": 16,
    "figure.titleweight": "bold",
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "bold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

print("Loading dataset and generating 5-fold out-of-fold predictions...")
df = pd.read_csv(BASE_DIR / "salary_data.csv")

CATEGORICAL_COLS = ["Company", "Job_Title", "Industry", "Role_Family", "Seniority_Level"]
NUMERIC_COLS = ["Rating", "Avg_Exp"]
TARGET = "Avg_Salary_LPA"

X = df[CATEGORICAL_COLS + NUMERIC_COLS]
y = df[TARGET]

# Build fresh CV pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False, min_frequency=2), CATEGORICAL_COLS),
    ],
    remainder="passthrough",
)

rf_reg = RandomForestRegressor(n_estimators=150, max_depth=22, min_samples_split=3, min_samples_leaf=2, random_state=42, n_jobs=-1)
hgb_reg = HistGradientBoostingRegressor(max_iter=200, max_leaf_nodes=31, min_samples_leaf=3, random_state=42)
voting_reg = VotingRegressor(estimators=[("rf", rf_reg), ("hgb", hgb_reg)])
pipeline = Pipeline([("preprocessor", preprocessor), ("regressor", voting_reg)])

kf = KFold(n_splits=5, shuffle=True, random_state=42)
y_pred_oof = cross_val_predict(pipeline, X, y, cv=kf)
y_pred_oof = np.maximum(y_pred_oof, 0.0)

residuals = y - y_pred_oof
abs_errors = np.abs(residuals)

r2_cv = r2_score(y, y_pred_oof)
mae_cv = mean_absolute_error(y, y_pred_oof)
rmse_cv = root_mean_squared_error(y, y_pred_oof)

df_analysis = df.copy()
df_analysis["y_pred"] = y_pred_oof
df_analysis["residual"] = residuals
df_analysis["abs_error"] = abs_errors

# ═══════════════════════════════════════════════════════════════════════════════
# PLOT 1: CALIBRATION SCATTER PLOT (Actual vs. Predicted)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Calibration Plot...")
fig, ax = plt.subplots(figsize=(8, 7), dpi=300)

max_val = max(y.max(), y_pred_oof.max()) + 5

# Ideal reference line
ax.plot([0, max_val], [0, max_val], color="#dc2626", linestyle="--", linewidth=2.0, label="Perfect Calibration (y = x)")

# +/- 20% error corridor
x_line = np.linspace(0, max_val, 100)
ax.fill_between(x_line, x_line * 0.8, x_line * 1.2, color="#e0e7ff", alpha=0.4, label="±20% Acceptable Tolerance")

# Scatter points colored by Seniority Level
seniority_order = ["Entry / Junior", "Mid-Level", "Senior / Lead", "Manager / Lead", "Executive / Director"]
palette = {"Entry / Junior": "#10b981", "Mid-Level": "#3b82f6", "Senior / Lead": "#6366f1", "Manager / Lead": "#f59e0b", "Executive / Director": "#ec4899"}

for sen in seniority_order:
    sub = df_analysis[df_analysis["Seniority_Level"] == sen]
    ax.scatter(sub["Avg_Salary_LPA"], sub["y_pred"], label=sen, color=palette.get(sen, "#64748b"), alpha=0.65, edgecolors="white", linewidths=0.5, s=45)

ax.set_xlim(0, 65)
ax.set_ylim(0, 65)
ax.set_xlabel("Actual Reported Salary (LPA)", fontweight="bold")
ax.set_ylabel("Out-of-Fold Predicted Salary (LPA)", fontweight="bold")
ax.set_title("Model Calibration: Actual vs. Out-of-Fold Predicted Salary (5-Fold CV)", pad=15)

# Metrics box
metrics_box = f"5-Fold CV Metrics:\nR² = {r2_cv:.4f}\nMAE = {mae_cv:.2f} LPA\nRMSE = {rmse_cv:.2f} LPA\nN = {len(df)} samples"
ax.text(0.04, 0.72, metrics_box, transform=ax.transAxes, fontsize=10, verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#ffffff", edgecolor="#cbd5e1", alpha=0.95))

ax.legend(loc="lower right", frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", fontsize=9)
plt.tight_layout()
calib_path = ASSETS_DIR / "calibration_plot.png"
plt.savefig(calib_path, dpi=300)
plt.close()
print(f"Saved -> {calib_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# PLOT 2: RESIDUAL DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Residual Distribution Plot...")
fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

sns.histplot(residuals, bins=40, kde=True, color="#4f46e5", edgecolor="#ffffff", alpha=0.6, ax=ax)
ax.axvline(0, color="#dc2626", linestyle="--", linewidth=1.8, label=f"Zero Bias (Mean Residual: {residuals.mean():+.2f} LPA)")
ax.axvline(residuals.median(), color="#059669", linestyle=":", linewidth=1.8, label=f"Median Residual ({residuals.median():+.2f} LPA)")

p25, p75 = np.percentile(residuals, [25, 75])
ax.axvspan(p25, p75, color="#fef3c7", alpha=0.3, label=f"Interquartile Range ({p25:.1f} to {p75:.1f} LPA)")

ax.set_xlim(-25, 25)
ax.set_xlabel("Prediction Residual: Actual - Predicted (LPA)", fontweight="bold")
ax.set_ylabel("Frequency (Count)", fontweight="bold")
ax.set_title("Residual Error Distribution (5-Fold Cross-Validation)", pad=15)
ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", fontsize=9)

plt.tight_layout()
resid_path = ASSETS_DIR / "residual_distribution.png"
plt.savefig(resid_path, dpi=300)
plt.close()
print(f"Saved -> {resid_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# PLOT 3: SEGMENT-LEVEL ERROR ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Segment-Level Error Analysis Plot...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=300, gridspec_kw={"width_ratios": [1.4, 1.0]})

# 1. By Role Family
rf_agg = df_analysis.groupby("Role_Family").agg(
    mae=("abs_error", "mean"),
    count=("abs_error", "count")
).sort_values("mae", ascending=True)

y_pos = np.arange(len(rf_agg))
bars = ax1.barh(y_pos, rf_agg["mae"], color="#6366f1", edgecolor="none", height=0.65, alpha=0.85)

# Color high-error bars differently
for i, bar in enumerate(bars):
    if rf_agg["mae"].iloc[i] > 6.0:
        bar.set_color("#f43f5e")
    elif rf_agg["mae"].iloc[i] < 3.0:
        bar.set_color("#10b981")

ax1.set_yticks(y_pos)
ax1.set_yticklabels(rf_agg.index, fontsize=9.5)
ax1.set_xlabel("Mean Absolute Error (LPA)", fontweight="bold")
ax1.set_title("MAE by Canonical Role Family", pad=12)

# Add value & count labels
for i, v in enumerate(rf_agg["mae"]):
    n_samples = rf_agg["count"].iloc[i]
    ax1.text(v + 0.2, i, f"{v:.2f}L  (n={n_samples})", va="center", fontsize=8.5, color="#1e293b", fontweight="600")

ax1.set_xlim(0, max(rf_agg["mae"]) + 2.5)

# 2. By Seniority Level
sen_agg = df_analysis.groupby("Seniority_Level").agg(
    mae=("abs_error", "mean"),
    median_sal=("Avg_Salary_LPA", "median"),
    count=("abs_error", "count")
).reindex(seniority_order)

y_pos_sen = np.arange(len(sen_agg))
bars_sen = ax2.bar(y_pos_sen, sen_agg["mae"], color=["#10b981", "#3b82f6", "#6366f1", "#f59e0b", "#ec4899"], edgecolor="none", width=0.55, alpha=0.85)

ax2.set_xticks(y_pos_sen)
ax2.set_xticklabels(seniority_order, rotation=20, ha="right", fontsize=9.5)
ax2.set_ylabel("Mean Absolute Error (LPA)", fontweight="bold")
ax2.set_title("MAE by Seniority Level (Error Scales with Seniority)", pad=12)

for bar, v, n in zip(bars_sen, sen_agg["mae"], sen_agg["count"]):
    ax2.text(bar.get_x() + bar.get_width()/2, v + 0.2, f"{v:.2f}L\n(n={n})", ha="center", va="bottom", fontsize=8.5, fontweight="600")

ax2.set_ylim(0, max(sen_agg["mae"]) + 2.0)

plt.tight_layout()
segment_path = ASSETS_DIR / "segment_error_analysis.png"
plt.savefig(segment_path, dpi=300)
plt.close()
print(f"Saved -> {segment_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# PLOT 4: COMBINED 2x2 EXECUTIVE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Combined 2x2 Executive Diagnostic Dashboard...")
fig = plt.figure(figsize=(16, 13), dpi=300)
gs = fig.add_gridspec(2, 2, hspace=0.28, wspace=0.24)

# Top Left: Actual vs Predicted
ax_top_left = fig.add_subplot(gs[0, 0])
ax_top_left.plot([0, 65], [0, 65], color="#dc2626", linestyle="--", linewidth=1.8, label="Ideal Calibration (y=x)")
ax_top_left.fill_between(x_line, x_line * 0.8, x_line * 1.2, color="#e0e7ff", alpha=0.35, label="±20% Tolerance")
for sen in seniority_order:
    sub = df_analysis[df_analysis["Seniority_Level"] == sen]
    ax_top_left.scatter(sub["Avg_Salary_LPA"], sub["y_pred"], label=sen, color=palette.get(sen), alpha=0.6, s=35, edgecolors="none")
ax_top_left.set_xlim(0, 60)
ax_top_left.set_ylim(0, 60)
ax_top_left.set_xlabel("Actual Salary (LPA)")
ax_top_left.set_ylabel("OOF Predicted Salary (LPA)")
ax_top_left.set_title("A. Calibration: Actual vs. Out-of-Fold Predicted")
ax_top_left.text(0.04, 0.72, f"5-Fold CV:\nR² = {r2_cv:.4f}\nMAE = {mae_cv:.2f} LPA\nRMSE = {rmse_cv:.2f} LPA",
                 transform=ax_top_left.transAxes, fontsize=8.5, bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff", edgecolor="#cbd5e1"))
ax_top_left.legend(loc="lower right", fontsize=8, frameon=True)

# Top Right: Residual Distribution
ax_top_right = fig.add_subplot(gs[0, 1])
sns.histplot(residuals, bins=35, kde=True, color="#4f46e5", edgecolor="#ffffff", alpha=0.6, ax=ax_top_right)
ax_top_right.axvline(0, color="#dc2626", linestyle="--", linewidth=1.5, label=f"Zero Bias (Mean: {residuals.mean():+.2f}L)")
ax_top_right.axvline(residuals.median(), color="#059669", linestyle=":", linewidth=1.5, label=f"Median ({residuals.median():+.2f}L)")
ax_top_right.set_xlim(-22, 22)
ax_top_right.set_xlabel("Residual: Actual - Predicted (LPA)")
ax_top_right.set_ylabel("Count")
ax_top_right.set_title("B. Residual Distribution (Unbiased Gaussian Curve)")
ax_top_right.legend(loc="upper right", fontsize=8.5, frameon=True)

# Bottom Left: Role Family Error
ax_bot_left = fig.add_subplot(gs[1, 0])
y_pos = np.arange(len(rf_agg))
b_bars = ax_bot_left.barh(y_pos, rf_agg["mae"], color="#6366f1", height=0.65, alpha=0.85)
for i, bar in enumerate(b_bars):
    if rf_agg["mae"].iloc[i] > 6.0:
        bar.set_color("#f43f5e")
    elif rf_agg["mae"].iloc[i] < 3.0:
        bar.set_color("#10b981")
ax_bot_left.set_yticks(y_pos)
ax_bot_left.set_yticklabels(rf_agg.index, fontsize=8.5)
ax_bot_left.set_xlabel("Mean Absolute Error (LPA)")
ax_bot_left.set_title("C. Segment Error by Role Family (MAE)")
for i, v in enumerate(rf_agg["mae"]):
    n_s = rf_agg["count"].iloc[i]
    ax_bot_left.text(v + 0.2, i, f"{v:.1f}L (n={n_s})", va="center", fontsize=7.5, color="#1e293b")
ax_bot_left.set_xlim(0, max(rf_agg["mae"]) + 2.5)

# Bottom Right: Salary Bracket Error
ax_bot_right = fig.add_subplot(gs[1, 1])
salary_bins = [0, 5, 10, 15, 25, 60]
salary_labels = ["0-5 LPA", "5-10 LPA", "10-15 LPA", "15-25 LPA", "25+ LPA"]
df_analysis["bracket"] = pd.cut(df_analysis["Avg_Salary_LPA"], bins=salary_bins, labels=salary_labels, include_lowest=True)
b_agg = df_analysis.groupby("bracket", observed=True).agg(mae=("abs_error", "mean"), count=("abs_error", "count"))
b_pos = np.arange(len(b_agg))
bars_b = ax_bot_right.bar(b_pos, b_agg["mae"], color=["#10b981", "#3b82f6", "#6366f1", "#f59e0b", "#f43f5e"], width=0.55, alpha=0.85)
ax_bot_right.set_xticks(b_pos)
ax_bot_right.set_xticklabels(salary_labels, rotation=15, ha="right", fontsize=9)
ax_bot_right.set_ylabel("Mean Absolute Error (LPA)")
ax_bot_right.set_title("D. MAE by Salary Tier (Tail Error Amplification)")
for bar, v, n in zip(bars_b, b_agg["mae"], b_agg["count"]):
    ax_bot_right.text(bar.get_x() + bar.get_width()/2, v + 0.3, f"{v:.2f}L\n(n={n})", ha="center", va="bottom", fontsize=8, fontweight="600")
ax_bot_right.set_ylim(0, max(b_agg["mae"]) + 3.0)

fig.suptitle("India Salary Predictor — Model Evaluation & Diagnostic Dashboard (5-Fold CV)", fontsize=15, y=0.99)
plt.tight_layout()
dashboard_path = ASSETS_DIR / "model_evaluation_dashboard.png"
plt.savefig(dashboard_path, dpi=300)
plt.close()
print(f"Saved -> {dashboard_path}")

print("All diagnostic plots generated successfully!")
