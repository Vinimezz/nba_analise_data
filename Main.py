from nba_api.stats.endpoints import leaguegamelog
import pandas as pd

# Pull 2024-25 regular season game logs
gamelog = leaguegamelog.LeagueGameLog(
    season="2024-25",
    season_type_all_star="Regular Season"
)

df = gamelog.get_data_frames()[0]

# Keep the columns you need
df = df[[
    "TEAM_ID", "TEAM_NAME", "GAME_ID", "GAME_DATE",
    "MATCHUP", "WL", "PTS", "REB", "AST"
]].copy()

# Convert date and sort
df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
df = df.sort_values(["TEAM_ID", "GAME_DATE"])

# Calculate rest days since previous game for each team
df["PREV_GAME_DATE"] = df.groupby("TEAM_ID")["GAME_DATE"].shift(1)
df["REST_DAYS"] = (df["GAME_DATE"] - df["PREV_GAME_DATE"]).dt.days - 1

# Bucket rest periods
def rest_bucket(x):
    if pd.isna(x):
        return None
    if x <= 0:
        return "0 days"
    elif x == 1:
        return "1 day"
    else:
        return "2+ days"

df["REST_BUCKET"] = df["REST_DAYS"].apply(rest_bucket)

# Add home/away
df["HOME_AWAY"] = df["MATCHUP"].apply(lambda x: "Home" if "vs." in x else "Away")

# Add win/loss as numeric
df["WIN"] = df["WL"].apply(lambda x: 1 if x == "W" else 0)

# Drop first games with no rest bucket
df_clean = df.dropna(subset=["REST_BUCKET"]).copy()

# Summary by rest bucket
summary = (
    df_clean.groupby("REST_BUCKET")[["WIN", "PTS", "REB", "AST"]]
    .mean()
    .sort_index()
)

print("Summary by rest bucket:")
print(summary)

# Summary by rest bucket + home/away
summary_home_away = (
    df_clean.groupby(["REST_BUCKET", "HOME_AWAY"])[["WIN", "PTS", "REB", "AST"]]
    .mean()
)

print("\nSummary by rest bucket and home/away:")
print(summary_home_away)

# Optional: counts
print("\nGame counts by rest bucket:")
print(df_clean["REST_BUCKET"].value_counts())