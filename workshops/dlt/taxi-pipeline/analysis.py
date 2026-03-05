import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import dlt
    import ibis
    import altair as alt

    return alt, dlt, ibis, mo


@app.cell
def _(dlt):
    pipeline = dlt.attach("taxi_pipeline")
    dataset = pipeline.dataset()
    con = dataset.ibis()
    return con, dataset, pipeline


@app.cell
def _(mo):
    mo.md(r"""
    # NYC Yellow Taxi — Trip Analysis

    10,000 trip records loaded via dlt from the DE Zoomcamp API into DuckDB.
    """)
    return


# ── Homework Q1: Date range ──


@app.cell
def _(con, mo):
    rides = con.table("rides")
    min_date = rides.trip_pickup_date_time.min().execute()
    max_date = rides.trip_pickup_date_time.max().execute()
    total_rows = rides.count().execute()

    mo.md(f"""
    ## Q1: Date Range

    | Metric | Value |
    |--------|-------|
    | **Earliest pickup** | {min_date} |
    | **Latest pickup** | {max_date} |
    | **Total trips** | {total_rows:,} |
    """)
    return


# ── Homework Q2: Credit card proportion ──


@app.cell
def _(alt, con):
    rides_q2 = con.table("rides")
    payment_counts = (
        rides_q2
        .group_by("payment_type")
        .agg(count=rides_q2.payment_type.count())
        .order_by(rides_q2.payment_type.count().desc())
    )
    payment_df = payment_counts.to_pandas()

    payment_chart = (
        alt.Chart(payment_df)
        .mark_arc(innerRadius=50)
        .encode(
            theta=alt.Theta("count:Q"),
            color=alt.Color(
                "payment_type:N",
                title="Payment Type",
                scale=alt.Scale(scheme="tableau10"),
            ),
            tooltip=["payment_type", "count"],
        )
        .properties(
            title="Trips by Payment Type",
            width=400,
            height=400,
        )
    )
    payment_chart
    return


@app.cell
def _(con, mo):
    rides_pct = con.table("rides")
    total = rides_pct.count().execute()
    credit = rides_pct.filter(rides_pct.payment_type == "Credit").count().execute()
    pct = round(100.0 * credit / total, 2)

    mo.md(f"""
    ## Q2: Credit Card Proportion

    **{pct}%** of trips paid by credit card ({credit:,} out of {total:,})
    """)
    return


# ── Homework Q3: Total tips ──


@app.cell
def _(con, mo):
    rides_tips = con.table("rides")
    total_tips = rides_tips.tip_amt.sum().execute()

    mo.md(f"""
    ## Q3: Total Tips

    **${total_tips:,.2f}** generated in tips across all trips
    """)
    return


# ── Trips per day ──


@app.cell
def _(mo):
    mo.md(r"""
    ## Trips Per Day

    Daily trip volume across the dataset period.
    """)
    return


@app.cell
def _(alt, con):
    rides_daily = con.table("rides")
    daily = (
        rides_daily
        .mutate(trip_date=rides_daily.trip_pickup_date_time.date())
        .group_by("trip_date")
        .agg(trips=rides_daily.trip_pickup_date_time.count())
        .order_by("trip_date")
    )
    daily_df = daily.to_pandas()

    daily_chart = (
        alt.Chart(daily_df)
        .mark_line(point=True, color="#2563eb")
        .encode(
            x=alt.X("trip_date:T", title="Date"),
            y=alt.Y("trips:Q", title="Number of Trips"),
            tooltip=["trip_date:T", "trips"],
        )
        .properties(
            title="Daily Trip Volume",
            width=700,
            height=350,
        )
    )
    daily_chart
    return


# ── Fare distribution ──


@app.cell
def _(mo):
    mo.md(r"""
    ## Fare Distribution

    Histogram of fare amounts (excluding outliers above $100).
    """)
    return


@app.cell
def _(alt, con):
    rides_fare = con.table("rides")
    fare_df = (
        rides_fare
        .filter(rides_fare.fare_amt.between(0, 100))
        .select("fare_amt")
        .to_pandas()
    )

    fare_chart = (
        alt.Chart(fare_df)
        .mark_bar(color="#10b981")
        .encode(
            x=alt.X("fare_amt:Q", bin=alt.Bin(maxbins=40), title="Fare ($)"),
            y=alt.Y("count()", title="Number of Trips"),
        )
        .properties(
            title="Fare Amount Distribution",
            width=700,
            height=350,
        )
    )
    fare_chart
    return


# ── Top vendors ──


@app.cell
def _(alt, con):
    rides_vendor = con.table("rides")
    vendor_counts = (
        rides_vendor
        .group_by("vendor_name")
        .agg(
            trips=rides_vendor.vendor_name.count(),
            avg_fare=rides_vendor.fare_amt.mean(),
            avg_tip=rides_vendor.tip_amt.mean(),
        )
    )
    vendor_df = vendor_counts.to_pandas()

    vendor_chart = (
        alt.Chart(vendor_df)
        .mark_bar(color="#f97316")
        .encode(
            x=alt.X("trips:Q", title="Number of Trips"),
            y=alt.Y("vendor_name:N", sort="-x", title="Vendor"),
            tooltip=["vendor_name", "trips", "avg_fare", "avg_tip"],
        )
        .properties(
            title="Trips by Vendor",
            width=600,
            height=200,
        )
    )
    vendor_chart
    return


# ── Trip distance vs fare scatter ──


@app.cell
def _(mo):
    mo.md(r"""
    ## Trip Distance vs Fare

    Sampled scatter plot — does distance correlate with fare?
    """)
    return


@app.cell
def _(alt, con):
    rides_scatter = con.table("rides")
    scatter_df = (
        rides_scatter
        .filter(
            (rides_scatter.trip_distance > 0)
            & (rides_scatter.trip_distance < 30)
            & (rides_scatter.fare_amt > 0)
            & (rides_scatter.fare_amt < 100)
        )
        .select("trip_distance", "fare_amt", "payment_type")
        .limit(2000)
        .to_pandas()
    )

    scatter_chart = (
        alt.Chart(scatter_df)
        .mark_circle(size=20, opacity=0.5)
        .encode(
            x=alt.X("trip_distance:Q", title="Distance (miles)"),
            y=alt.Y("fare_amt:Q", title="Fare ($)"),
            color=alt.Color("payment_type:N", title="Payment"),
            tooltip=["trip_distance", "fare_amt", "payment_type"],
        )
        .properties(
            title="Trip Distance vs Fare Amount",
            width=700,
            height=400,
        )
    )
    scatter_chart
    return


# ── Summary ──


@app.cell
def _(con, mo):
    r = con.table("rides")
    summary_total = r.count().execute()
    summary_avg_fare = round(r.fare_amt.mean().execute(), 2)
    summary_avg_dist = round(r.trip_distance.mean().execute(), 2)
    summary_avg_tip = round(r.tip_amt.mean().execute(), 2)
    summary_total_rev = round(r.total_amt.sum().execute(), 2)

    mo.md(f"""
    ## Summary

    | Metric | Value |
    |--------|-------|
    | **Total Trips** | {summary_total:,} |
    | **Total Revenue** | ${summary_total_rev:,.2f} |
    | **Avg Fare** | ${summary_avg_fare} |
    | **Avg Distance** | {summary_avg_dist} miles |
    | **Avg Tip** | ${summary_avg_tip} |
    """)
    return


if __name__ == "__main__":
    app.run()
