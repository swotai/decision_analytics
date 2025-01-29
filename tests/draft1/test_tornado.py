def test_tornado_chart():
    # Use the sample dataframe from simulation (similar to sandbox_funnel.py)
    df = pd.DataFrame(
        {
            "total_sales_swing": [10, 20, 30],
            "total_sales_swing_squared": [50, 60, 70],
            "actual_high": [25, 35, 45],
            "actual_low": [5, 15, 25],
        }
    )

    fig = plot_tornado(df=df, kpi="total_sales")
    assert isinstance(fig, go.Figure)
