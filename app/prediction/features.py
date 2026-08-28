import pandas as pd


SOURCE_NAMES = ["tgju", "silfam", "noghresea"]
MERGE_TOLERANCE = pd.Timedelta(seconds=50)
FEATURES = [
    "tgju",
    "silfam",
    "noghresea",
    "lag_1",
    "lag_2",
    "lag_3",
    "ma_3",
    "ma_5",
    "price_change",
]


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    sources = {}

    for source in SOURCE_NAMES:
        sources[source] = (
            df[df["source"] == source][["created_at", "price"]]
            .rename(columns={"price": source})
            .sort_values("created_at")
        )

    data = sources["tgju"]
    for source in ["silfam", "noghresea"]:
        data = pd.merge_asof(
            data,
            sources[source],
            on="created_at",
            direction="nearest",
            tolerance=MERGE_TOLERANCE,
        )

    data = data.dropna(subset=SOURCE_NAMES)

    data["silver_price"] = data[SOURCE_NAMES].mean(axis=1)

    data["lag_1"] = data["silver_price"].shift(1)
    data["lag_2"] = data["silver_price"].shift(2)
    data["lag_3"] = data["silver_price"].shift(3)

    data["ma_3"] = data["silver_price"].rolling(3).mean()
    data["ma_5"] = data["silver_price"].rolling(5).mean()

    data["price_change"] = data["silver_price"].pct_change()

    data["next_price"] = data["silver_price"].shift(-1)

    return data.dropna()