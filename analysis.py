import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col

df = pd.read_csv("nba_rest_analysis.csv")

# Recreate simple regression variables
df["HOME"] = (df["HOME_AWAY"] == "Home").astype(int)

# Main models
model_win = smf.ols("WIN ~ B2B + HOME + TRAVEL_PROXY + B2B:TRAVEL_PROXY + B2B:HOME", data=df).fit(cov_type="HC1")
model_pts = smf.ols("PTS ~ B2B + HOME + TRAVEL_PROXY + B2B:TRAVEL_PROXY + B2B:HOME", data=df).fit(cov_type="HC1")
model_reb = smf.ols("REB ~ B2B + HOME + TRAVEL_PROXY + B2B:TRAVEL_PROXY + B2B:HOME", data=df).fit(cov_type="HC1")
model_ast = smf.ols("AST ~ B2B + HOME + TRAVEL_PROXY + B2B:TRAVEL_PROXY + B2B:HOME", data=df).fit(cov_type="HC1")
model_diff = smf.ols("POINT_DIFF ~ B2B + HOME + TRAVEL_PROXY + B2B:TRAVEL_PROXY + B2B:HOME", data=df).fit(cov_type="HC1")
model_fg = smf.ols("FG_PCT ~ B2B + HOME + TRAVEL_PROXY + B2B:TRAVEL_PROXY + B2B:HOME", data=df).fit(cov_type="HC1")
model_fg3 = smf.ols("FG3_PCT ~ B2B + HOME + TRAVEL_PROXY + B2B:TRAVEL_PROXY + B2B:HOME", data=df).fit(cov_type="HC1")
model_ft = smf.ols("FT_PCT ~ B2B + HOME + TRAVEL_PROXY + B2B:TRAVEL_PROXY + B2B:HOME", data=df).fit(cov_type="HC1")

# Print summaries
print("\n=== WIN ===")
print(model_win.summary())

print("\n=== POINT_DIFF ===")
print(model_diff.summary())

print("\n=== PTS ===")
print(model_pts.summary())

print("\n=== REB ===")
print(model_reb.summary())

print("\n=== AST ===")
print(model_ast.summary())

print("\n=== FG_PCT ===")
print(model_fg.summary())

print("\n=== FG3_PCT ===")
print(model_fg3.summary())

print("\n=== FT_PCT ===")
print(model_ft.summary())

# Clean regression table
table = summary_col(
    [
        model_win, model_diff, model_pts, model_fg, model_fg3, model_ft
    ],
    model_names=[
        "Win Rate", "Point Diff", "Points", "FG%", "3P%", "FT%"
    ],
    stars=True,
    float_format="%0.4f",
    info_dict={
        "N": lambda x: f"{int(x.nobs)}",
        "R2": lambda x: f"{x.rsquared:.3f}"
    }
)

print("\n=== Regression Table ===")
print(table)

# Save a simple coefficient table too
coef_table = pd.DataFrame({
    "Win Rate": model_win.params,
    "Point Diff": model_diff.params,
    "Points": model_pts.params,
    "FG%": model_fg.params,
    "3P%": model_fg3.params,
    "FT%": model_ft.params,
})

coef_table.to_csv("regression_coefficients.csv")
print("\nSaved regression_coefficients.csv") 