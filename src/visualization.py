import plotly.graph_objects as go


def plot_summary(df, per_month: bool = False):
    """
    Interactive Plotly summary chart.

    Args:
        df (pd.DataFrame): summary output from summary()
        per_month (bool): affects labeling
    """

    x_col = df.columns[0]
    x = df[x_col].astype(str)

    fig = go.Figure()

    # ----------------------------
    # ORDERS
    # ----------------------------
    fig.add_trace(go.Scatter(
        x=x,
        y=df["Orders"],
        mode="lines+markers",
        name="Orders"
    ))

    # ----------------------------
    # CARDS
    # ----------------------------
    fig.add_trace(go.Scatter(
        x=x,
        y=df["Cards"],
        mode="lines+markers",
        name="Cards"
    ))

    # ----------------------------
    # COST
    # ----------------------------
    fig.add_trace(go.Scatter(
        x=x,
        y=df["Cost"],
        mode="lines+markers",
        name="Cost",
        yaxis="y2"
    ))

    # ----------------------------
    # LAYOUT (dual axis for clarity)
    # ----------------------------
    fig.update_layout(
        title="Purchase Summary (Interactive)",
        xaxis_title="Month" if per_month else "Year",
        yaxis=dict(title="Orders / Cards"),
        yaxis2=dict(
            title="Cost",
            overlaying="y",
            side="right"
        ),
        hovermode="x unified",
        legend=dict(x=0, y=1),
        template="plotly_white"
    )

    fig.show()