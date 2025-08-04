import plotly.express as px
import plotly.graph_objects as go

# Credit vs Debit - line chart
def plot_monthly_credit_debit_line(df, granularity="M"):
    if df.empty:
        return px.line(title="No data for selected range")

    df = df.copy()
    
    # Group by selected granularity
    df["period"] = df["timestamp"].dt.to_period(granularity).astype(str)

    # Check if 'type' column still has at least one category (important after filter)
    group_cols = ["period"]
    if "type" in df.columns and df["type"].nunique() > 1:
        group_cols.append("type")
    elif "type" in df.columns:
        df["type"] = df["type"].astype(str)
        group_cols.append("type")

    # Group
    summary = df.groupby(group_cols)["amount"].sum().reset_index()

    fig = px.line(
        summary,
        x="period",
        y="amount",
        color="type" if "type" in summary.columns else None,
        markers=True,
        title="Credit vs Debit by Selected Period"
    )
    fig.update_layout(xaxis_title="Period", yaxis_title="Amount")
    return fig

# Spending by category - donut chart
def plot_spending_by_category_pie(df):
    debit_df = df[df["type"] == "debit"]
    if debit_df.empty:
        return px.pie(title="No debit data")
    category_summary = debit_df.groupby("category")["amount"].sum().sort_values(ascending=False).reset_index()
    fig = px.pie(category_summary, names="category", values="amount",
                 title="Spending by Category", hole=0.4)
    fig.update_traces(textinfo="percent+label")
    return fig

# Transactions - table
def create_plotly_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color='lightgray',
            align='left',
            font=dict(size=12, color='black')
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color='white',
            align='left',
            font=dict(size=11)
        )
    )])

    fig.update_layout(title="Transactions Table", height=400)
    return fig
