
import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="Citi Bike Analytics Explorer",
    page_icon="🚲",
    layout="wide"
)

# Load our cleaned dataset
@st.cache_data
def load_data():
    df = pd.read_csv(
    "data/citibike_cleanedfile.zip",
    dtype={
        "Start Station Id": "string",
        "End Station Id": "string"
    }
)
     # Remove any unnamed columns
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    return df

df = load_data()
df["Started At"] = pd.to_datetime(df["Started At"])
df["Hour"] = df["Started At"].dt.hour

# Dashboard header

st.title("🚲 Citi Bike Analytics Explorer: September 2026")


# Dashboard Navigation
st.sidebar.title("🚲 Citi Bike Explorer")

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "Rider Behavior",
        "Station Explorer",
        "Geospatial Analysis",
        "Statistical Insights",
        "Business Insights",
        "Methodology"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "NYC Citi Bike Analytics"
)


st.write(
    "Exploring NYC Citi Bike ridership, station demand, "
    "and mobility patterns."
)

if page == "Overview":
    st.header("Ridership Overview")

    # Key performance indicators
    total_trips = len(df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Trips", f"{total_trips:,}")

    with col2:
        st.metric("Unique Start Stations", df["Start Station Name"].nunique())

    with col3:
        st.metric("Average Trip Duration", f"{df['Trip Duration (Mins)'].mean():.1f} min")

    # Preview the dataset
    st.subheader("Dataset Preview")
    st.dataframe(
    df.drop(columns=["Hour"], errors="ignore").head(10),
    width="stretch"
)


# Ridership patterns throughout the day
if page == "Rider Behavior":

    st.subheader("When Do New Yorkers Ride?")


    # Interactive rider type filter
    rider_filter = st.selectbox(
        "Select Rider Type",
        options=["All Riders", "member", "casual"]
    )

    # Filter the dataset based on selection
    if rider_filter == "All Riders":
        filtered_df = df
    else:
        filtered_df = df[
            df["Member Casual"].str.lower() == rider_filter
        ]


    # Calculate hourly trips by rider type
    hourly_comparison = (
        filtered_df.groupby(["Hour", "Member Casual"])
        .size()
        .reset_index(name="Total Trips")
    )

    # Create interactive comparison chart
    fig_hourly = px.line(
        hourly_comparison,
        x="Hour",
        y="Total Trips",
        color="Member Casual",
        markers=True,
        title="Hourly Ridership by Rider Type",
        labels={
            "Hour": "Hour of Day",
            "Total Trips": "Number of Trips",
            "Member Casual": "Rider Type"
        }
    )

    fig_hourly.update_layout(
        xaxis=dict(
            tickmode="linear",
            dtick=1
        ),
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_hourly,
        width="stretch",
        key="hourly_rider_comparison"
    )

#Rider Behavior: Members vs. Casual Riders

if page == "Rider Behavior":
    st.header("Rider Behavior Analysis")
    st.subheader("Who Uses Citi Bike?")

    # Count trips by rider type
    rider_counts = (
        df["Member Casual"]
        .value_counts()
        .reset_index()
    )

    rider_counts.columns = ["Rider Type", "Total Trips"]

    # Create interactive donut chart
    fig = px.pie(
        rider_counts,
        names="Rider Type",
        values="Total Trips",
        hole=0.55,
        title="Ridership Breakdown: Members vs. Casual Riders"
    )

    fig.update_traces(
        textposition="outside",
        textinfo="label+percent"
    )

    # Average trip duration by rider type
    duration_by_rider = (
        df.groupby("Member Casual")["Trip Duration (Mins)"]
        .mean()
        .reset_index()
    )

    fig_duration = px.bar(
        duration_by_rider,
        x="Member Casual",
        y="Trip Duration (Mins)",
        color="Member Casual",
        text_auto=".1f",
        title="Average Trip Duration by Rider Type",
        labels={
            "Member Casual": "Rider Type",
            "Trip Duration (Mins)": "Average Duration (Minutes)"
        }
    )

    fig_duration.update_layout(showlegend=False)

    # Display both charts side by side
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig, width="stretch", key="rider_breakdown")

    with col2:
        st.plotly_chart(fig_duration, width="stretch", key="trip_duration")

 
 # Station & Network Intelligence
if page == "Overview":
        
    st.header("Station & Network Intelligence")

    st.subheader("Top 10 Busiest Start Stations")

    # Count the number of trips originating at each station
    top_stations = (
        df["Start Station Name"]
        .dropna()
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_stations.columns = ["Station", "Total Starts"]

    # Create interactive horizontal bar chart
    fig_stations = px.bar(
        top_stations,
        x="Total Starts",
        y="Station",
        orientation="h",
        text="Total Starts",
        title="Top 10 Stations by Trip Starts",
        labels={
            "Total Starts": "Number of Trip Starts",
            "Station": "Station Name"
        }
    )

    # Display busiest station at the top
    fig_stations.update_layout(
        yaxis=dict(autorange="reversed"),
        showlegend=False
    )

    st.plotly_chart(
        fig_stations,
        width="stretch",
        key="top_start_stations"
    )

    # Network-Wide Station Flow Analysis
    st.subheader("Network-Wide Station Imbalances")

    # Count departures and arrivals at each station
    network_starts = df["Start Station Name"].value_counts()
    network_ends = df["End Station Name"].value_counts()

    # Combine counts for all stations
    station_flow = pd.DataFrame({
        "Trip Starts": network_starts,
        "Trip Ends": network_ends
    }).fillna(0)

    # Calculate net trip inflow
    station_flow["Net Trip Inflow"] = (
        station_flow["Trip Ends"] - station_flow["Trip Starts"]
    )

    station_flow = station_flow.reset_index()
    station_flow.columns = [
        "Station", "Trip Starts", "Trip Ends", "Net Inflow"
    ]
   
    # Interactive station imbalance filters
    col1, col2 = st.columns([2, 1])

    with col1:
        flow_view = st.radio(
            "Select Flow Type",
            ["Net Inflow", "Net Outflow"],
            horizontal=True
        )

    with col2:
        top_n = st.selectbox(
            "Number of Stations",
            [5, 10, 15, 20],
            index=0
        )

    # Filter stations based on user selection
    if flow_view == "Net Inflow":
        filtered_stations = station_flow.nlargest(
            top_n, "Net Inflow"
        )
        chart_color = "#3579b8"
    else:
        filtered_stations = station_flow.nsmallest(
            top_n, "Net Inflow"
        )
        chart_color = "#d97863"

    # Create interactive horizontal bar chart
    fig_imbalance = px.bar(
        filtered_stations,
        x="Net Inflow",
        y="Station",
        orientation="h",
        text="Net Inflow",
        color_discrete_sequence=[chart_color],
        hover_data={
            "Trip Starts": ":,",
            "Trip Ends": ":,",
            "Net Inflow": ":,"
        },
        title=f"Top {top_n} Stations by {flow_view}",
        labels={
            "Net Inflow": "Net Trip Inflow (Ends - Starts)",
            "Station": "Station Name"
        }
    )

    fig_imbalance.update_traces(
        texttemplate="%{x:+,.0f}",
        textposition="outside"
    )

    fig_imbalance.update_layout(
        yaxis=dict(autorange="reversed"),
        height=max(350, top_n * 38 + 120),
        showlegend=False
    )

    st.plotly_chart(
        fig_imbalance,
        width="stretch",
        key="network_station_imbalance"
    )


    st.caption(
        "Positive values indicate more recorded trip arrivals "
        "than departures. Negative values indicate more departures "
        "than arrivals. Net trip flow does not represent actual "
        "bike inventory or account for operator redistribution."
    )



# Station Explorer
if page == "Station Explorer":
    st.header("Station Explorer")
    st.subheader("Explore Individual Stations")

    station_counts = (
        df["Start Station Name"]
        .dropna()
        .value_counts()
    )

    selected_station = st.selectbox(
        "Search for a Citi Bike Station",
        options=sorted(station_counts.index.tolist())
    )

    total_starts = int(station_counts[selected_station])

    st.metric(
        label=f"Total Trip Starts: {selected_station}",
        value=f"{total_starts:,}"
    )


    # Rider composition at the selected station
    station_df = df[
        df["Start Station Name"] == selected_station
    ]

    station_riders = (
        station_df["Member Casual"]
        .value_counts()
        .reset_index()
    )

    station_riders.columns = ["Rider Type", "Total Trips"]

    fig_station_riders = px.pie(
        station_riders,
        names="Rider Type",
        values="Total Trips",
        hole=0.5,
        title=f"Rider Composition at {selected_station}"
    )

    fig_station_riders.update_traces(
        textinfo="label+percent",
        textposition="outside"
    )

    st.plotly_chart(
        fig_station_riders,
        width="stretch",
        key="station_rider_composition"
    )


    # Hourly demand at the selected station
    station_hourly = (
        station_df.groupby("Hour")
        .size()
        .reset_index(name="Total Trips")
    )

    fig_station_hourly = px.bar(
        station_hourly,
        x="Hour",
        y="Total Trips",
        title=f"Hourly Trip Starts at {selected_station}",
        labels={
            "Hour": "Hour of Day",
            "Total Trips": "Number of Trip Starts"
        }
    )

    fig_station_hourly.update_layout(
        xaxis=dict(
            tickmode="linear",
            dtick=1,
            range=[-0.5, 23.5]
        ),
        showlegend=False
    )

    st.plotly_chart(
        fig_station_hourly,
        width="stretch",
        key="station_hourly_demand"
    )

# Hourly Trip Starts vs. Ends

    st.subheader("Hourly Trip Starts vs. Ends")

    station_starts = df[df["Start Station Name"] == selected_station]
    station_ends = df[df["End Station Name"] == selected_station]

    hourly_starts = station_starts.groupby("Hour").size()

    hourly_ends = (
        station_ends
        .assign(End_Hour=pd.to_datetime(station_ends["Ended At"]).dt.hour)
        .groupby("End_Hour")
        .size()
    )

    hourly_flow = pd.DataFrame({
        "Hour": range(24)
    })

    hourly_flow["Trip Starts"] = hourly_flow["Hour"].map(hourly_starts).fillna(0)
    hourly_flow["Trip Ends"] = hourly_flow["Hour"].map(hourly_ends).fillna(0)

    fig_flow = px.line(
        hourly_flow,
        x="Hour",
        y=["Trip Starts", "Trip Ends"],
        markers=True,
        title=f"Hourly Trip Starts vs. Ends at {selected_station}",
        labels={"value": "Number of Trips", "variable": "Trip Type"}
    )

    fig_flow.update_layout(
        xaxis=dict(dtick=1),
        hovermode="x unified"
    )

    st.plotly_chart(fig_flow, width="stretch")


    # Daily Net Trip Flow
    st.subheader("Daily Net Trip Flow")

    daily_starts = (
        station_starts.assign(
            Date=station_starts["Started At"].dt.date
        )
        .groupby("Date")
        .size()
    )

    daily_ends = (
        station_ends.assign(
            Date=pd.to_datetime(station_ends["Ended At"]).dt.date
        )
        .groupby("Date")
        .size()
    )

    daily_flow = pd.DataFrame({
        "Trip Starts": daily_starts,
        "Trip Ends": daily_ends
    }).fillna(0)

    daily_flow["Net Inflow"] = (
        daily_flow["Trip Ends"] - daily_flow["Trip Starts"]
    )

    daily_flow = daily_flow.reset_index()

    fig_daily_flow = px.bar(
        daily_flow,
        x="Date",
        y="Net Inflow",
        color="Net Inflow",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        title=f"Daily Net Trip Flow at {selected_station}",
        labels={
            "Date": "Date",
            "Net Inflow": "Net Trip Inflow"
        }
    )

    fig_daily_flow.update_layout(
        coloraxis_showscale=False
    )

    st.plotly_chart(
        fig_daily_flow,
        width="stretch",
        key="station_daily_flow"
    )

    # Compare trip starts and ends at the selected station
    total_ends = int(
        (df["End Station Name"] == selected_station).sum()
    )

    net_flow = total_ends - total_starts

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Trip Starts", f"{total_starts:,}")

    with col2:
        st.metric("Trip Ends", f"{total_ends:,}")

    with col3:
        st.metric("Net Trip Inflow", f"{net_flow:+,}")

    if net_flow > 0:
        st.caption(
            "More recorded trips end here than begin here. "
            "This station may warrant further investigation "
            "for potential rebalancing needs."
        )
    elif net_flow < 0:
        st.caption(
            "More recorded trips begin here than end here. "
            "This station may warrant further investigation "
            "for potential bike availability constraints."
        )
    else:
        st.caption(
            "Recorded trip starts and ends are balanced."
        )



# Interactive Geospatial Analysis

if page == "Geospatial Analysis":
    st.header("Geospatial Demand Analysis")

    map_options = {
        "Pickup vs. Drop-off Hotspots": "start_vs_end_heatmap.html",
        "Station Activity Map": "interactive_station_clusters.html",
        "Animated Hourly Heatmap": "hourly_animated_heatmap.html"
    }

    selected_map = st.selectbox(
        "Choose a Map to Explore",
        options=list(map_options.keys())
    )

    st.subheader(selected_map)

    map_descriptions = {
        "Pickup vs. Drop-off Hotspots":
            "Explore the geographic concentration of Citi Bike trip starts "
            "and ends. Use the layer controls to compare pickup and drop-off demand.",

        "Station Activity Map":
            "Explore individual Citi Bike stations across New York City. "
            "Zoom in to reveal station markers and click them to examine trip activity.",

        "Animated Hourly Heatmap":
            "Explore how geographic ridership demand changes throughout the day."
    }

    st.write(map_descriptions[selected_map])

    map_path = Path("maps") / map_options[selected_map]

    if map_path.exists():
        map_html = map_path.read_text(encoding="utf-8")
        components.html(map_html, height=600, scrolling=False)
    else:
        st.error(f"Map file not found: {map_path}")


elif page == "Statistical Insights":
    st.title("Statistical Insights")
    st.caption(
        "Hypothesis testing and statistical modeling of "
        "Citi Bike rider behavior and bike utilization."
    )

    
    # 1. Trip Duration Analysis
    st.header("1. Trip Duration by Rider Type")

    st.write(
        "Do casual riders and members differ in their "
        "average trip duration?"
    )

    duration_summary = (
        df.groupby("Member Casual")["Trip Duration (Mins)"]
        .mean()
        .reset_index()
    )

    duration_summary["Member Casual"] = (
        duration_summary["Member Casual"].str.title()
    )

    fig = px.bar(
        duration_summary,
        x="Member Casual",
        y="Trip Duration (Mins)",
        color="Member Casual",
        text="Trip Duration (Mins)",
        labels={
            "Member Casual": "Rider Type",
            "Trip Duration (Mins)": "Average Trip Duration (Minutes)"
        },
        title="Average Trip Duration by Rider Type"
    )

    fig.update_traces(
        texttemplate="%{text:.2f} min",
        textposition="outside"
    )

    fig.update_layout(
        showlegend=False,
        yaxis_range=[0, 20]
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Mean Difference", "5.37 min")
    col2.metric("95% Confidence Interval", "5.24–5.50 min")
    col3.metric("Cohen's d", "0.33")

    st.markdown(
        """
        **Statistical finding:** Casual trips average approximately
        5.37 minutes longer than member trips (Welch's t-test,
        p < 0.001).

        **Interpretation:** Although the difference is statistically
        significant, Cohen's d = 0.33 indicates a relatively modest
        standardized effect.

        **Business implication:** Differences in trip duration may
        be relevant to rider segmentation, pricing, and fleet
        utilization, but further analysis would be needed before
        making operational recommendations.
        """
    )

    st.divider()

    # 2. Rider Type vs. Time of Day
    st.header("2. Rider Type and Time of Day")

    st.write(
        "Is the time of day a trip begins associated "
        "with rider type?"
    )

    # Create time-of-day categories
    hour = pd.to_datetime(df["Started At"]).dt.hour

    time_period = pd.cut(
        hour,
        bins=[-1, 4, 9, 15, 20, 23],
        labels=["Night", "Morning", "Midday", "Evening", "Late Night"]
    )

    # Combine nighttime periods
    time_period = time_period.astype(str).replace(
        {"Late Night": "Night"}
    )

    time_table = pd.crosstab(
        df["Member Casual"],
        time_period,
        normalize="index"
    ) * 100

    time_table = time_table.reindex(
        columns=["Morning", "Midday", "Evening", "Night"]
    )

    time_chart = time_table.reset_index().melt(
        id_vars="Member Casual",
        var_name="Time of Day",
        value_name="Percentage"
    )

    time_chart["Member Casual"] = (
        time_chart["Member Casual"].str.title()
    )

    fig_time = px.bar(
        time_chart,
        x="Member Casual",
        y="Percentage",
        color="Time of Day",
        barmode="stack",
        text="Percentage",
        category_orders={
            "Time of Day": [
                "Morning", "Midday", "Evening", "Night"
            ]
        },
        labels={
            "Member Casual": "Rider Type",
            "Percentage": "Share of Trips (%)"
        },
        title="Trip Start Time Distribution by Rider Type"
    )

    fig_time.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside"
    )

    fig_time.update_layout(
        yaxis_range=[0, 100]
    )

    st.plotly_chart(fig_time, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Chi-Square Statistic", "7,901.11")
    col2.metric("P-value", "< 0.001")
    col3.metric("Cramér's V", "0.090")

    st.markdown(
        """
        **Statistical finding:** Rider type and trip start
        time are associated (chi-square test, p < 0.001).

        **Interpretation:** The association is weak
        (Cramér's V = 0.090). Members have a higher share
        of morning trips (21.3% vs. 12.9%), while casual
        riders have higher shares during midday and nighttime.

        **Business implication:** These patterns may help
        inform time-specific fleet planning and customer
        segmentation. However, trip purpose cannot be
        determined from start time alone.
        """
    )

    st.divider()

    # 3. Electric-Bike Usage by Rider Type
    st.header("3. Electric-Bike Usage by Rider Type")

    st.write(
        "Does the proportion of electric-bike trips "
        "differ between casual riders and members?"
    )

    bike_usage = pd.crosstab(
        df["Member Casual"],
        df["Rideable Type"],
        normalize="index"
    ) * 100

    bike_chart = bike_usage.reset_index().melt(
        id_vars="Member Casual",
        var_name="Bike Type",
        value_name="Percentage"
    )

    bike_chart["Member Casual"] = (
        bike_chart["Member Casual"].str.title()
    )

    fig_bike = px.bar(
        bike_chart,
        x="Member Casual",
        y="Percentage",
        color="Bike Type",
        barmode="stack",
        text="Percentage",
        category_orders={
            "Bike Type": ["electric bike", "classic bike"]
        },
        labels={
            "Member Casual": "Rider Type",
            "Percentage": "Share of Trips (%)"
        },
        title="Bike Type Distribution by Rider Category"
    )

    fig_bike.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside"
    )

    fig_bike.update_layout(
        yaxis_range=[0, 100]
    )

    st.plotly_chart(fig_bike, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Casual Electric-Bike Share", "77.62%")
    col2.metric("Member Electric-Bike Share", "71.49%")
    col3.metric("Difference", "+6.14 pp")

    st.markdown(
        """
        **Statistical finding:** Casual trips have a
        significantly higher electric-bike share than
        member trips (two-proportion z-test,
        z = 51.07, p < 0.001).

        **Interpretation:** Electric bikes account for
        most trips in both rider categories, but their
        share is approximately 6.14 percentage points
        higher among casual riders.

        **Business implication:** Differences in bike
        utilization could inform fleet allocation and
        customer segmentation. However, observed usage
        does not necessarily establish rider preference,
        since bike availability and pricing may influence
        selection.
        """
    )

    st.divider()

    # 4. Rider Type x Bike Type Interaction
    st.header("4. Rider Type × Bike Type Interaction")

    st.write(
        "Does the relationship between bike type and trip "
        "duration differ between casual riders and members?"
    )

    # Calculate average trip durations for each group
    interaction_data = (
        df.groupby(
            ["Member Casual", "Rideable Type"]
        )["Trip Duration (Mins)"]
        .mean()
        .reset_index()
    )

    interaction_data["Member Casual"] = (
        interaction_data["Member Casual"].str.title()
    )

    interaction_data["Rideable Type"] = (
        interaction_data["Rideable Type"].str.title()
    )

    fig_interaction = px.line(
        interaction_data,
        x="Rideable Type",
        y="Trip Duration (Mins)",
        color="Member Casual",
        markers=True,
        category_orders={
            "Rideable Type": [
                "Classic Bike",
                "Electric Bike"
            ]
        },
        labels={
            "Rideable Type": "Bike Type",
            "Trip Duration (Mins)": "Average Trip Duration (Minutes)",
            "Member Casual": "Rider Type"
        },
        title="Interaction Between Rider Type and Bike Type"
    )

    fig_interaction.update_traces(
        mode="lines+markers+text",
        texttemplate="%{y:.2f} min",
        textposition="top center",
        marker=dict(size=10),
        line=dict(width=3)
    )

    fig_interaction.update_layout(
        yaxis_range=[0, 25]
    )

    st.plotly_chart(
        fig_interaction,
        use_container_width=True
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Original Interaction", "5.10 min")
    col2.metric("Trimmed Interaction", "2.99 min")
    col3.metric("Trimmed 95% CI", "2.86–3.11 min")

    st.markdown(
        """
        **Statistical finding:** The relationship between
        bike type and average trip duration differs
        significantly across rider categories
        (heteroskedasticity-robust regression,
        interaction p < 0.001).

        **Interpretation:** Among casual riders,
        electric-bike trips average approximately
        4.88 minutes shorter than classic-bike trips.
        Among members, electric-bike trips average
        approximately 0.22 minutes longer.

        **Robustness check:** After excluding trips above
        the dataset-wide 99th percentile, the interaction
        coefficient decreased from 5.10 to 2.99 minutes,
        but remained statistically significant
        (95% CI: 2.86–3.11 minutes).

        **Business implication:** Bike utilization patterns
        differ across rider segments. This could inform
        further investigation into trip purpose, pricing,
        and fleet allocation. These associations should
        not be interpreted as causal effects.
        """
    )

    st.divider()



elif page == "Business Insights":
    st.title("Business Insights & Recommendations")

    st.caption(
        "Translating observed ridership patterns and statistical "
        "findings into opportunities for business decision-making."
    )

    st.subheader("Executive Summary")

    st.write(
        "Analysis of 982,319 Citi Bike trips reveals differences "
        "in rider behavior, electric-bike utilization, and "
        "station-level trip flows. These findings highlight "
        "opportunities to investigate customer segmentation, "
        "fleet allocation, and network operations."
    )

    
    st.divider()

    # Recommendation 1: Rider Segmentation
    st.subheader("1. Investigate Rider Segmentation")

    st.markdown(
        """
        **Evidence**

        - Casual trips average **5.37 minutes longer**
          than member trips.
        - Electric bikes account for **77.62% of casual
          trips**, compared with **71.49% of member trips**.
        - Among casual riders, classic-bike trips average
          **4.88 minutes longer** than electric-bike trips.

        **Business Opportunity**

        These patterns suggest potential differences in
        how casual riders and members use Citi Bike.
        Understanding these differences could help identify
        opportunities to improve customer experience,
        membership offerings, and pricing strategies.

        **Recommended Action**

        Conduct additional customer segmentation analysis
        using trip frequency, duration, location, and bike
        type. Where possible, supplement trip-level data
        with customer research to distinguish commuting,
        recreation, and other transportation needs.

        **Validation Needed**

        Before introducing new pricing or membership
        offerings, evaluate customer willingness to pay,
        existing pricing structures, bike availability,
        and the financial implications of proposed changes.
        """
    )

    st.divider()

    # Recommendation 2: Fleet Allocation
    st.subheader("2. Evaluate Fleet Allocation")

    st.markdown(
        """
        **Evidence**

        - Electric bikes account for **77.62% of casual
          trips** and **71.49% of member trips**.
        - Members have a higher proportion of morning
          trips (21.3%) than casual riders (12.9%).
        - Casual riders have relatively higher shares
          of midday and nighttime trips.

        **Business Opportunity**

        Differences in rider behavior suggest that bike
        utilization patterns may vary across locations,
        customer segments, and times of day. Understanding
        these patterns could support more responsive fleet
        planning and improve bike availability.

        **Recommended Action**

        Analyze electric- and classic-bike trip starts
        by station, hour, and rider type to identify
        potential differences in utilization.

        Prioritize locations where observed usage patterns
        suggest a need for further investigation into
        fleet composition and availability.

        **Validation Needed**

        Compare trip activity with real-time bike
        availability, station capacity, rebalancing
        records, and unmet demand before recommending
        changes to fleet allocation.
        """
    )

    st.divider()

    # Recommendation 3: Station Operations
    st.subheader("3. Investigate Station-Level Trip Imbalances")

    st.markdown(
        """
        **Evidence**

        - Station-level analysis reveals substantial
          differences between recorded trip starts and ends.
        - Pier 61 at Chelsea Piers recorded **3,450 trip
          starts** and **8,524 trip ends**, producing a
          net trip inflow of **5,074 trips**.
        - Network-wide analysis identifies other stations
          with substantial recorded trip-flow imbalances.

        **Business Opportunity**

        Persistent differences between trip starts and
        ends may indicate locations worth investigating
        for potential bike redistribution needs.

        Understanding these patterns could support
        operational planning and station availability.

        **Recommended Action**

        Identify stations with substantial net trip
        inflows or outflows and examine their hourly
        and daily patterns.

        Prioritize recurring imbalances for further
        operational investigation rather than relying
        solely on aggregate trip totals.

        **Validation Needed**

        Compare observed trip flows with station capacity,
        bike inventory, rebalancing activity, and real-time
        availability data.

        Because the dataset contains unequal coverage of
        starting and ending station IDs, recorded trip
        imbalances should not be interpreted as confirmed
        bike inventory changes.
        """
    )


# Methodology Page
if page == "Methodology":

    st.title("Data & Methodology")
    st.caption(
        "An overview of the dataset, analytical approach, "
        "statistical techniques, and study limitations."
    )

    # 1. RESEARCH OBJECTIVE
    st.subheader("01 | Research Objective")

    st.write(
        "This project examines NYC Citi Bike ridership patterns "
        "to understand customer behavior, temporal demand, "
        "station-level trip activity, and geographic mobility. "
        "The objective is to translate observed patterns into "
        "evidence-based opportunities for transportation planning, "
        "customer strategy, and network operations."
    )

    st.divider()

    # 2. DATASET OVERVIEW
    st.subheader("02 | Dataset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Original Records", "982,855")

    with col2:
        st.metric("Cleaned Records", f"{len(df):,}")

    with col3:
        st.metric(
            "Records Retained",
            f"{len(df) / 982855 * 100:.2f}%"
        )

    st.write(
        "The dataset contains trip-level records, including "
        "ride timestamps, rider membership category, bicycle "
        "type, trip duration, and station locations."
    )

    st.divider()

    # 3. DATA PREPARATION
    st.subheader("03 | Data Preparation")

    st.write(
        "Data preparation focused on improving the consistency "
        "and reliability of trip-level observations before analysis."
    )

    st.markdown(
        """
        **Preparation steps**

        1. Reviewed missing station information and recovered
           records where reliable information was available.
        2. Removed observations that could not be reliably retained.
        3. Checked for duplicate trip records.
        4. Calculated trip duration in minutes.
        5. Derived temporal variables for hourly and
           time-of-day analysis.
        """
    )

    st.divider()

    # 4. ANALYTICAL FRAMEWORK
    st.subheader("04 | Analytical Framework")

    st.write(
        "The analysis combines exploratory visualization, "
        "statistical inference, and operational investigation."
    )

    tab1, tab2, tab3 = st.tabs(
        ["Behavior & Demand", "Geospatial Analysis", "Statistical Testing"]
    )

    with tab1:
        st.markdown(
            """
            **Descriptive and temporal analysis**

            - Measured overall ridership and average trip duration.
            - Compared member and casual rider activity.
            - Examined hourly and time-of-day trip patterns.
            - Evaluated station-level trip starts and ends.
            """
        )

    with tab2:
        st.markdown(
            """
            **Spatial and operational analysis**

            - Visualized geographic trip activity using
              interactive maps and heatmaps.
            - Explored station-level spatial patterns.
            - Calculated net trip inflow as recorded trip
              ends minus trip starts.
            - Identified stations for further operational
              investigation.
            """
        )

    with tab3:
        st.markdown(
            """
            **Statistical investigations**

            Four hypothesis-driven analyses were conducted
            to evaluate differences and associations
            in rider behavior.

            Expand the methods below for details.
            """
        )

        with st.expander("1. Welch's Independent-Samples T-Test"):
            st.write(
                "Compared mean trip duration between casual "
                "riders and members. Welch's test accommodates "
                "unequal sample sizes and variances. "
                "A 95% confidence interval and Cohen's d "
                "were used to assess precision and effect size."
            )

        with st.expander("2. Chi-Square Test of Independence"):
            st.write(
                "Tested the association between rider type "
                "and four time-of-day categories. "
                "Cramér's V was used to evaluate "
                "the strength of the association."
            )

        with st.expander("3. Two-Proportion Z-Test"):
            st.write(
                "Compared the proportion of electric-bike "
                "trips between casual riders and members."
            )

        with st.expander("4. Two-Way ANOVA & Robust Regression"):
            st.write(
                "Examined the interaction between rider type "
                "and bicycle type in relation to trip duration. "
                "HC3 heteroskedasticity-robust standard errors "
                "were used, followed by a sensitivity analysis "
                "excluding trips above the dataset-wide "
                "99th percentile of duration."
            )

    st.divider()

    # 5. STUDY LIMITATIONS
    st.subheader("05 | Study Limitations")

    st.write(
        "Findings should be interpreted within the constraints "
        "of the available trip-level data."
    )

    with st.expander("Observational Data & Causality"):
        st.write(
            "The analysis identifies associations rather than "
            "causal relationships. Pricing, weather, trip purpose, "
            "route characteristics, and bike availability "
            "were not controlled for."
        )

    with st.expander("Statistical Inference"):
        st.write(
            "Individual riders may contribute multiple trips, "
            "so independence cannot be fully verified. "
            "The large sample size can also produce very small "
            "p-values for modest differences. Effect sizes "
            "and practical significance are therefore important."
        )

    with st.expander("Trip Duration & Outliers"):
        st.write(
            "Trip durations are right-skewed, with some unusually "
            "long observations. A sensitivity analysis excluding "
            "the longest 1% of trips was conducted to assess "
            "the robustness of the interaction model."
        )

    with st.expander("Station Coverage & Net Trip Flow"):
        st.write(
            "The dataset contains unequal numbers of unique "
            "starting and ending station IDs. Net trip inflow "
            "represents recorded trip ends minus starts, "
            "not actual bike inventory changes. Operator-led "
            "rebalancing and station availability are not observed."
        )

    st.info(
        "Interpretation principle: Statistical significance "
        "does not necessarily imply operational importance. "
        "Business recommendations are exploratory and require "
        "validation with additional customer and operational data."
    )
