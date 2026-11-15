
import pandas as pd
from scipy import stats
from pathlib import Path

# Load the cleaned Citi Bike dataset
data_path = Path("data/citibike_cleanedfile.zip")

df = pd.read_csv(data_path)

# Confirm the dataset loaded correctly
print("Total trips:", len(df))
print("\nRider types:")
print(df["Member Casual"].value_counts())


# Separate trip durations by rider type
member_duration = df.loc[
    df["Member Casual"] == "member",
    "Trip Duration (Mins)"
].dropna()

casual_duration = df.loc[
    df["Member Casual"] == "casual",
    "Trip Duration (Mins)"
].dropna()

# Calculate descriptive statistics
print("\nTrip Duration Summary:")

print(
    "Members:",
    "N =", len(member_duration),
    "Mean =", round(member_duration.mean(), 2),
    "SD =", round(member_duration.std(), 2)
)

print(
    "Casual:",
    "N =", len(casual_duration),
    "Mean =", round(casual_duration.mean(), 2),
    "SD =", round(casual_duration.std(), 2)
)

# Welch's independent-samples t-test
t_stat, p_value = stats.ttest_ind(
    casual_duration,
    member_duration,
    equal_var=False
)

print("\nWelch's T-Test Results:")
print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.6g}")


# Calculate a 95% confidence interval for the mean difference
mean_difference = casual_duration.mean() - member_duration.mean()

n1 = len(casual_duration)
n2 = len(member_duration)

var1 = casual_duration.var()
var2 = member_duration.var()

standard_error = ((var1 / n1) + (var2 / n2)) ** 0.5

# Welch-Satterthwaite degrees of freedom
df_welch = ((var1 / n1 + var2 / n2) ** 2) / (
    ((var1 / n1) ** 2 / (n1 - 1)) +
    ((var2 / n2) ** 2 / (n2 - 1))
)

critical_t = stats.t.ppf(0.975, df_welch)

lower_bound = mean_difference - critical_t * standard_error
upper_bound = mean_difference + critical_t * standard_error

print("\n95% Confidence Interval:")
print(f"Mean difference: {mean_difference:.2f} minutes")
print(f"Lower bound: {lower_bound:.2f} minutes")
print(f"Upper bound: {upper_bound:.2f} minutes")


# Calculate Cohen's d effect size

pooled_sd = (
    (
        (n1 - 1) * var1 +
        (n2 - 1) * var2
    ) / (n1 + n2 - 2)
) ** 0.5

cohens_d = mean_difference / pooled_sd

print("\nEffect Size:")
print(f"Cohen's d: {cohens_d:.4f}")


# Chi-square analysis: Rider Type vs. Time of Day

df["Started At"] = pd.to_datetime(df["Started At"])
df["Hour"] = df["Started At"].dt.hour

def categorize_time(hour):
    if 5 <= hour < 10:
        return "Morning (5 AM–10 AM)"
    elif 10 <= hour < 16:
        return "Midday (10 AM–4 PM)"
    elif 16 <= hour < 21:
        return "Evening (4 PM–9 PM)"
    else:
        return "Night (9 PM–5 AM)"

df["Time of Day"] = df["Hour"].apply(categorize_time)

# Create a contingency table
contingency_table = pd.crosstab(
    df["Member Casual"],
    df["Time of Day"]
)

print("\nRider Type vs. Time of Day:")
print(contingency_table)


# Chi-square test of independence
chi2, p_value_chi, dof, expected = stats.chi2_contingency(
    contingency_table
)

print("\nChi-Square Test Results:")
print(f"Chi-square statistic: {chi2:.4f}")
print(f"P-value: {p_value_chi:.6g}")
print(f"Degrees of freedom: {dof}")
print(f"Minimum expected frequency: {expected.min():.2f}")


# High-precision chi-square p-value
import mpmath as mp

mp.mp.dps = 100  # Use 100 decimal digits of precision

chi2_precise = mp.mpf(str(chi2))
p_precise = mp.gammainc(
    mp.mpf(dof) / 2,
    chi2_precise / 2,
    mp.inf,
    regularized=True
)

print("\nHigh-Precision P-value:")
print(mp.nstr(p_precise, 15))


# Calculate Cramér's V effect size

n = contingency_table.to_numpy().sum()
rows, cols = contingency_table.shape

cramers_v = (
    chi2 / (n * min(rows - 1, cols - 1))
) ** 0.5

print("\nEffect Size:")
print(f"Cramér's V: {cramers_v:.4f}")



# Bike Type Analysis

print("\nBike Types:")
print(df["Rideable Type"].value_counts(dropna=False))

# Bike type distribution by rider category
bike_table = pd.crosstab(
    df["Member Casual"],
    df["Rideable Type"]
)

print("\nBike Type by Rider Category:")
print(bike_table)

# Percentages within each rider category
bike_percentages = pd.crosstab(
    df["Member Casual"],
    df["Rideable Type"],
    normalize="index"
) * 100

print("\nBike Type Percentages by Rider Category:")
print(bike_percentages.round(2))



# Two-proportion z-test: Electric bike usage by rider type

casual_electric = bike_table.loc["casual", "electric bike"]
member_electric = bike_table.loc["member", "electric bike"]

casual_total = bike_table.loc["casual"].sum()
member_total = bike_table.loc["member"].sum()

p_casual = casual_electric / casual_total
p_member = member_electric / member_total

pooled_p = (
    casual_electric + member_electric
) / (casual_total + member_total)

se = (
    pooled_p * (1 - pooled_p) *
    (1 / casual_total + 1 / member_total)
) ** 0.5

z_stat = (p_casual - p_member) / se

p_z = 2 * stats.norm.sf(abs(z_stat))

print("\nTwo-Proportion Z-Test:")
print(f"Z-statistic: {z_stat:.4f}")
print(f"P-value: {p_z:.6g}")
print(f"Difference: {(p_casual - p_member) * 100:.2f} percentage points")

# Trip duration by rider type and bike type

duration_by_bike = df.groupby(
    ["Member Casual", "Rideable Type"]
)["Trip Duration (Mins)"].agg(
    ["count", "mean", "median", "std"]
)

print("\nTrip Duration by Rider and Bike Type:")
print(duration_by_bike.round(2))

# Two-way ANOVA: Rider Type x Bike Type

import statsmodels.formula.api as smf
import statsmodels.api as sm

model = smf.ols(
    'Q("Trip Duration (Mins)") ~ C(Q("Member Casual")) * C(Q("Rideable Type"))',
    data=df
).fit()

anova_table = sm.stats.anova_lm(model, typ=2)

print("\nTwo-Way ANOVA Results:")
print(anova_table)


# Robust interaction test using HC3 standard errors

robust_model = model.get_robustcov_results(
    cov_type="HC3"
)

print("\nRobust Regression Results:")
print(robust_model.summary().tables[1])


# Check for unusually long trips by rider and bike type

duration_percentiles = df.groupby(
    ["Member Casual", "Rideable Type"]
)["Trip Duration (Mins)"].quantile(
    [0.50, 0.90, 0.95, 0.99]
).unstack()

duration_percentiles.columns = [
    "Median", "90th Percentile",
    "95th Percentile", "99th Percentile"
]

print("\nTrip Duration Percentiles:")
print(duration_percentiles.round(2))

# Sensitivity analysis: Remove trips above the 99th percentile

cutoff = df["Trip Duration (Mins)"].quantile(0.99)

df_trimmed = df[
    df["Trip Duration (Mins)"] <= cutoff
].copy()

trimmed_model = smf.ols(
    'Q("Trip Duration (Mins)") ~ C(Q("Member Casual")) * C(Q("Rideable Type"))',
    data=df_trimmed
).fit(cov_type="HC3")

print("\n99th Percentile Sensitivity Analysis:")
print(f"Duration cutoff: {cutoff:.2f} minutes")
print(f"Trips retained: {len(df_trimmed):,}")

print("\nTrimmed Group Means:")
print(
    df_trimmed.groupby(
        ["Member Casual", "Rideable Type"]
    )["Trip Duration (Mins)"].mean().round(2)
)

print("\nTrimmed Robust Regression:")
print(trimmed_model.summary().tables[1])
