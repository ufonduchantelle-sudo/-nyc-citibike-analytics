# NYC Citi Bike Analytics Explorer

### An Interactive Python Dashboard for Ridership, Mobility & Business Insights

An end-to-end exploratory analytics project examining **982,319 NYC Citi Bike trips from September 2026** to uncover patterns in rider behavior, bicycle utilization, station activity, and urban mobility.

Built with Python and Streamlit, the project combines interactive visualizations, geospatial analysis, statistical hypothesis testing, and business recommendations to demonstrate how trip-level data can inform operational and strategic decision-making.

## Project Objectives

- Explore ridership patterns across membership categories, bike types, and times of day.
- Identify geographic concentrations of trip activity and station-level flow imbalances.
- Apply statistical methods to evaluate differences and associations in rider behavior.
- Translate analytical findings into actionable areas for further business investigation.

## Interactive Dashboard

The Streamlit application features seven sections:

1. **Overview:** Key ridership metrics, busiest stations, and network-wide trip flows.
2. **Rider Behavior:** Membership composition, trip durations, and hourly demand.
3. **Station Explorer:** Station-specific rider composition, hourly activity, and daily trip flows.
4. **Geospatial Analysis:** Interactive station maps, pickup/drop-off heatmaps, and animated hourly demand.
5. **Statistical Insights:** Four hypothesis-driven statistical investigations.
6. **Business Insights:** Evidence-based opportunities for customer segmentation, fleet allocation, and station operations.
7. **Methodology:** Data preparation, analytical techniques, and study limitations.

## Key Findings

| Analysis                  | Finding                                                                                                                                                                     |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Trip duration             | Casual trips averaged **5.37 minutes longer** than member trips (95% CI: 5.24–5.50 minutes).                                                                                |
| Time-of-day behavior      | Rider type and trip start time were associated, although the relationship was weak (Cramér's V = 0.090).                                                                    |
| Electric-bike utilization | Electric bikes accounted for **77.62% of casual trips** versus **71.49% of member trips**.                                                                                  |
| Rider × bike interaction  | The relationship between bike type and trip duration differed by rider category. The interaction remained statistically significant after trimming the longest 1% of trips. |

All four statistical investigations produced p-values below 0.001. Findings are interpreted alongside effect sizes, practical significance, and study limitations.

## Business Implications

**Customer Segmentation:** Differences in trip duration and bike utilization suggest opportunities to investigate rider needs, membership offerings, and pricing strategies.

**Fleet Allocation:** Temporal and bike-type utilization patterns may inform further investigation into fleet composition and station availability.

**Station Operations:** Differences between recorded trip starts and ends can help identify stations for additional operational analysis.

These recommendations are exploratory and require validation using additional customer, pricing, availability, and operational data.

## Technical Stack

- **Python:** Data processing, analysis, and application development
- **Pandas:** Data manipulation and aggregation
- **SciPy:** Statistical hypothesis testing
- **Statsmodels:** ANOVA, regression, and heteroskedasticity-robust inference
- **Plotly:** Interactive visualizations
- **Streamlit:** Interactive dashboard development
- **HTML-based geospatial maps:** Spatial exploration and animated demand visualization

## Running the Project Locally

Clone the repository, navigate to the project directory, and install the dependencies:

```bash
pip install -r requirements.txt
```

Launch the interactive dashboard:

```bash
streamlit run app.py
```

Run the statistical analysis separately:

```bash
python analysis.py
```

The project uses a compressed CSV dataset stored in `data/citibike_cleanedfile.zip`.

## Study Limitations

This project uses observational trip-level data and does not establish causal relationships. Individual riders may contribute multiple trips, and rider-level independence cannot be fully verified.

Recorded station trip flows do not represent actual bicycle inventory changes. Pricing, weather, station availability, and operator redistribution were not directly modeled.

Statistical significance should not be interpreted as equivalent to operational importance.

## Future Development

Potential extensions include incorporating weather and station availability data, analyzing repeated patterns across multiple months, and evaluating predictive models for station-level demand.

---

*Developed as an independent business analytics portfolio project.*
