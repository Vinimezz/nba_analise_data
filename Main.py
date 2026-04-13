from nba_api.stats.endpoints import leaguegamelog
import pandas as pd

# Pull 2024-25 regular season game logs
gamelog = leaguegamelog.LeagueGameLog(
    season="2024-25",
    season_type_all_star="Regular Season"
)

df = gamelog.get_data_frames()[0]

# Keep the stats you want to analyze
df = df[[
    "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_NAME", "GAME_ID", "GAME_DATE",
    "MATCHUP", "WL", "PTS", "REB", "AST",
    "FG_PCT", "FG3_PCT", "FT_PCT"
]].copy()

# Dates and sorting
df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
df = df.sort_values(["TEAM_ID", "GAME_DATE"]).reset_index(drop=True)

# Home or away
df["HOME_AWAY"] = df["MATCHUP"].apply(lambda x: "Home" if "vs." in x else "Away")

# Opponent abbreviation from matchup string
# Examples:
# "LAL vs. BOS" -> BOS
# "LAL @ BOS"   -> BOS
df["OPP_ABBREVIATION"] = df["MATCHUP"].str.split().str[-1]

# Metro-area groups so same-city teams are treated as the same location
METRO_GROUP = {
    "ATL": "Atlanta",
    "BOS": "Boston",
    "BKN": "New York",
    "CHA": "Charlotte",
    "CHI": "Chicago",
    "CLE": "Cleveland",
    "DAL": "Dallas",
    "DEN": "Denver",
    "DET": "Detroit",
    "GSW": "Bay Area",
    "HOU": "Houston",
    "IND": "Indianapolis",
    "LAC": "Los Angeles",
    "LAL": "Los Angeles",
    "MEM": "Memphis",
    "MIA": "Miami",
    "MIL": "Milwaukee",
    "MIN": "Minneapolis",
    "NOP": "New Orleans",
    "NYK": "New York",
    "OKC": "Oklahoma City",
    "ORL": "Orlando",
    "PHI": "Philadelphia",
    "PHX": "Phoenix",
    "POR": "Portland",
    "SAC": "Sacramento",
    "SAS": "San Antonio",
    "TOR": "Toronto",
    "UTA": "Salt Lake City",
    "WAS": "Washington",
}

# Current venue group:
# - home game -> team's metro group
# - away game -> opponent's metro group
df["CURRENT_VENUE_GROUP"] = df.apply(
    lambda r: METRO_GROUP.get(r["TEAM_ABBREVIATION"], r["TEAM_ABBREVIATION"])
    if r["HOME_AWAY"] == "Home"
    else METRO_GROUP.get(r["OPP_ABBREVIATION"], r["OPP_ABBREVIATION"]),
    axis=1
)

# Previous game venue group
df["PREV_GAME_DATE"] = df.groupby("TEAM_ID")["GAME_DATE"].shift(1)
df["PREV_VENUE_GROUP"] = df.groupby("TEAM_ID")["CURRENT_VENUE_GROUP"].shift(1)

# Rest days
df["REST_DAYS"] = (df["GAME_DATE"] - df["PREV_GAME_DATE"]).dt.days - 1

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

# Win dummy
df["WIN"] = df["WL"].apply(lambda x: 1 if x == "W" else 0)

# Back-to-back dummy
df["B2B"] = (df["REST_DAYS"] == 0).astype(int)

# Travel proxy:
# 1 = venue group changed from previous game
# 0 = same metro area as previous game
# This fixes cases like Lakers -> Clippers in Los Angeles
df["TRAVEL_PROXY"] = (
    df["PREV_VENUE_GROUP"].notna() &
    (df["CURRENT_VENUE_GROUP"] != df["PREV_VENUE_GROUP"])
).astype(int)

# Opponent points and point differential
df["OPP_PTS"] = df.groupby("GAME_ID")["PTS"].transform(lambda s: s.sum() - s)
df["POINT_DIFF"] = df["PTS"] - df["OPP_PTS"]

# Drop first games of each team where rest cannot be computed
df_clean = df.dropna(subset=["REST_BUCKET"]).copy()

# Save cleaned dataset
df_clean.to_csv("nba_rest_analysis.csv", index=False)

print("Saved nba_rest_analysis.csv")
print("\nTravel proxy check:")
print(df_clean["TRAVEL_PROXY"].value_counts())