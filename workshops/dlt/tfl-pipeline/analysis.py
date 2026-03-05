import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import altair as alt
    import dlt
    import ibis
    import marimo as mo

    return alt, dlt, ibis, mo


@app.cell
def _(dlt):
    pipeline = dlt.attach("tfl_rest")
    dataset = pipeline.dataset()
    con = dataset.ibis()
    return (con,)


@app.cell
def _(mo):
    mo.md(r"""
    # Transport for London — Data Explorer

    Data loaded via dlt from the TfL Unified API into DuckDB.
    """)
    return


@app.cell
def _(con, mo):
    tables = sorted(con.list_tables())
    table_list = "\n".join(f"- `{t}`" for t in tables if not t.startswith("_dlt"))
    mo.md(f"""
    ## Available Tables

    {table_list}
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Bike Points by Area

    There are ~800 Santander Cycles docking stations across London.
    Which areas have the most?
    """)
    return


@app.cell
def _(alt, con, ibis):
    bike = con.table("bike_point")
    borough_counts = (
        bike.mutate(area=bike.common_name.split(",")[-1].strip())
        .group_by("area")
        .agg(stations=bike.id.count())
        .order_by(ibis.desc("stations"))
        .limit(15)
    )
    borough_df = borough_counts.to_pandas()

    borough_chart = (
        alt.Chart(borough_df)
        .mark_bar(color="#e11d48")
        .encode(
            x=alt.X("stations:Q", title="Number of Docking Stations"),
            y=alt.Y("area:N", sort="-x", title="Area"),
            tooltip=["area", "stations"],
        )
        .properties(
            title="Top 15 Areas by Bike Docking Stations",
            width=600,
            height=400,
        )
    )
    borough_chart
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Docking Station Capacity

    Each bike point has `additional_properties` — dlt normalised these into a child table.
    We can extract `NbDocks` (total capacity) per station.
    """)
    return


@app.cell
def _(alt, con, ibis):
    props = con.table("bike_point__additional_properties")
    docks = (
        props.filter(props.key == "NbDocks")
        .mutate(capacity=props.value.cast("int64"))
        .order_by(ibis.desc("capacity"))
        .limit(20)
        .select("_dlt_parent_id", "capacity")
    )
    docks_df = docks.to_pandas()

    docks_chart = (
        alt.Chart(docks_df)
        .mark_bar(color="#2563eb")
        .encode(
            x=alt.X("capacity:Q", title="Total Docks"),
            y=alt.Y("_dlt_parent_id:N", sort="-x", title="Station ID"),
            tooltip=["_dlt_parent_id", "capacity"],
        )
        .properties(
            title="Top 20 Largest Docking Stations",
            width=600,
            height=400,
        )
    )
    docks_chart
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Major Roads — Current Status

    Overview of TfL-managed strategic roads (A2, A4, A40, etc.)
    """)
    return


@app.cell
def _(con, mo):
    roads = con.table("road")
    roads_df = roads.select(
        "display_name", "status_severity", "status_severity_description"
    ).to_pandas()
    mo.ui.table(roads_df, label="Road Status")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Accident Statistics (2019)

    50,626 accident records from TfL, with nested casualties and vehicles tables.
    """)
    return


@app.cell
def _(alt, con):
    accidents = con.table("accident_stats")
    severity_counts = accidents.group_by("severity").agg(
        count=accidents.severity.count()
    )
    severity_df = severity_counts.to_pandas()

    severity_chart = (
        alt.Chart(severity_df)
        .mark_arc(innerRadius=50)
        .encode(
            theta=alt.Theta("count:Q"),
            color=alt.Color(
                "severity:N",
                title="Severity",
                scale=alt.Scale(
                    domain=["Fatal", "Serious", "Slight"],
                    range=["#dc2626", "#f97316", "#facc15"],
                ),
            ),
            tooltip=["severity", "count"],
        )
        .properties(
            title="Accidents by Severity (2019)",
            width=400,
            height=400,
        )
    )
    severity_chart
    return


@app.cell
def _(alt, con):
    casualties = con.table("accident_stats__casualties")
    by_mode = (
        casualties.group_by("mode")
        .agg(total=casualties.mode.count())
        .order_by(casualties.mode.count().desc())
        .limit(10)
    )
    mode_df = by_mode.to_pandas()

    mode_chart = (
        alt.Chart(mode_df)
        .mark_bar(color="#7c3aed")
        .encode(
            x=alt.X("total:Q", title="Casualties"),
            y=alt.Y("mode:N", sort="-x", title="Transport Mode"),
            tooltip=["mode", "total"],
        )
        .properties(
            title="Top 10 Casualty Modes (2019)",
            width=600,
            height=350,
        )
    )
    mode_chart
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Tube Line Status (Live Snapshot)

    Status of Victoria, Circle, Central, and Northern lines at time of data load.
    """)
    return


@app.cell
def _(con, mo):
    line_status = con.table("line_status")
    statuses = con.table("line_status__line_statuses")

    status_df = (
        line_status.join(statuses, line_status._dlt_id == statuses._dlt_parent_id)
        .select("name", "mode_name", "status_severity_description")
        .to_pandas()
    )
    mo.ui.table(status_df, label="Line Status")
    return


@app.cell
def _(con, mo):
    total_bike_points = con.table("bike_point").count().to_pandas()
    total_accidents = con.table("accident_stats").count().to_pandas()
    total_casualties = con.table("accident_stats__casualties").count().to_pandas()
    total_roads = con.table("road").count().to_pandas()
    total_routes = con.table("line_route").count().to_pandas()

    mo.md(f"""
    ## Summary

    | Metric | Value |
    |--------|-------|
    | **Bike Docking Stations** | {total_bike_points:,} |
    | **Accidents (2019)** | {total_accidents:,} |
    | **Casualties (2019)** | {total_casualties:,} |
    | **Strategic Roads** | {total_roads:,} |
    | **Line Routes** | {total_routes:,} |
    """)
    return


if __name__ == "__main__":
    app.run()
