import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("nba_rest_analysis.csv")

os.makedirs("figures", exist_ok=True)

sns.set_theme(style="whitegrid", context="talk")

order = ["0 days", "1 day", "2+ days"]

# Main figures for your project
metrics = {
    "WIN": ("Win Rate", (0, 1)),
    "POINT_DIFF": ("Point Differential", None),
    "PTS": ("Points", None),
    "REB": ("Rebounds", None),
    "AST": ("Assists", None),
    "FG_PCT": ("Field Goal %", None),
    "FG3_PCT": ("3PT %", None),
    "FT_PCT": ("Free Throw %", None),
}

for metric, (label, ylim) in metrics.items():
    plt.figure(figsize=(10, 6))

    ax = sns.barplot(
        data=df,
        x="REST_BUCKET",
        y=metric,
        hue="HOME_AWAY",
        order=order,
        errorbar=("ci", 95),
        palette="Set2"
    )

    ax.set_title(f"{label} by Rest Bucket and Home/Away")
    ax.set_xlabel("Rest Bucket")
    ax.set_ylabel(label)

    if ylim is not None:
        ax.set_ylim(*ylim)

    plt.legend(title="Location")
    plt.tight_layout()
    plt.savefig(f"figures/{metric}.png", dpi=300, bbox_inches="tight")
    plt.show()

# One polished combined figure
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("NBA 2024-25 Rest Analysis", fontsize=20)

panels = [
    ("WIN", "Win Rate", (0, 1)),
    ("POINT_DIFF", "Point Differential", None),
    ("FG_PCT", "Field Goal %", None),
    ("FG3_PCT", "3PT %", None),
]

for ax, (metric, label, ylim) in zip(axes.flatten(), panels):
    sns.barplot(
        data=df,
        x="REST_BUCKET",
        y=metric,
        hue="HOME_AWAY",
        order=order,
        errorbar=("ci", 95),
        palette="Set2",
        ax=ax
    )
    ax.set_title(label)
    ax.set_xlabel("")
    ax.set_ylabel(label)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.legend_.remove()

handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, title="Location", loc="upper right")
plt.tight_layout(rect=[0, 0, 0.92, 0.95])
plt.savefig("figures/combined_rest_analysis.png", dpi=300, bbox_inches="tight")
plt.show()