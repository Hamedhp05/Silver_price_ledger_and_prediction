import pandas as pd

FEATURES = ["lag_1", "lag_2", "lag_3", "ma_3", "ma_5", "price_change"]

def add_lag(df: pd.Series, window: int) -> pd.Series:
    return df.shift(window)

def add_moving_average(df: pd.Series, window: int) -> pd.Series:
    return df.rolling(window).mean()

def add_price_change(df: pd.Series) -> pd.Series:
    return df.pct_change()

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("fetched_at").copy()

    df["lag_1"] = add_lag(df["price"], 1)
    df["lag_2"] = add_lag(df["price"], 2)
    df["lag_3"] = add_lag(df["price"], 3)
    df["ma_3"] = add_moving_average(df["price"], 3)
    df["ma_5"] = add_moving_average(df["price"], 5)
    df["price_change"] = add_price_change(df["price"])
    df["next_price"] = add_lag(df["price"], -1)

    return df.dropna()

