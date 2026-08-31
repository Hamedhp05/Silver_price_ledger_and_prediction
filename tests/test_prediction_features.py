import pandas as pd
import pytest
from app.prediction.features import MERGE_TOLERANCE,prepare_features


def create_test_data():
    base_time = pd.Timestamp("2026-08-30 18:00:00")

    rows = []

    for i in range(8):
        time = base_time + pd.Timedelta(
            minutes=i
        )

        rows.extend([
            {
                "source": "tgju",
                "price": 470000 + i * 100,
                "created_at": time,
                "fetched_at": time,
            },
            {
                "source": "silfam",
                "price": 440000 + i * 100,
                "created_at": time + pd.Timedelta(
                    seconds=5
                ),
                "fetched_at": time + pd.Timedelta(
                    seconds=5
                ),
            },
            {
                "source": "noghresea",
                "price": 450000 + i * 100,
                "created_at": time + pd.Timedelta(
                    seconds=10
                ),
                "fetched_at": time + pd.Timedelta(
                    seconds=10
                ),
            },
        ])

    return pd.DataFrame(rows)


def test_prepare_features_merges_sources():
    df = create_test_data()

    result = prepare_features(df)

    assert not result.empty

    assert {
        "tgju",
        "silfam",
        "noghresea",
    }.issubset(result.columns)


def test_prepare_features_calculates_silver_price():
    df = create_test_data()

    result = prepare_features(df)

    first = result.iloc[0]

    expected = (
        first["tgju"]
        + first["silfam"]
        + first["noghresea"]
    ) / 3

    assert first["silver_price"] == expected


def test_prepare_features_calculates_lags():
    df = create_test_data()

    result = prepare_features(df)

    assert result["lag_1"].notna().all()
    assert result["lag_2"].notna().all()
    assert result["lag_3"].notna().all()

    for i in range(1, len(result)):
        assert result.iloc[i]["lag_1"] == (
            result.iloc[i - 1]["silver_price"]
        )

    for i in range(2, len(result)):
        assert result.iloc[i]["lag_2"] == (
            result.iloc[i - 2]["silver_price"]
        )

    for i in range(3, len(result)):
        assert result.iloc[i]["lag_3"] == (
            result.iloc[i - 3]["silver_price"]
        )


def test_prepare_features_calculates_moving_averages():
    df = create_test_data()

    result = prepare_features(df)

    for i in range(2, len(result)):
        expected_ma_3 = (
            result.iloc[i - 2:i + 1]["silver_price"]
            .mean()
        )

        assert result.iloc[i]["ma_3"] == expected_ma_3

    for i in range(4, len(result)):
        expected_ma_5 = (
            result.iloc[i - 4:i + 1]["silver_price"]
            .mean()
        )

        assert result.iloc[i]["ma_5"] == expected_ma_5


def test_prepare_features_calculates_price_change():
    df = create_test_data()

    result = prepare_features(df)

    for i in range(1, len(result)):
        previous = result.iloc[i - 1]["silver_price"]
        current = result.iloc[i]["silver_price"]

        expected = (current - previous) / previous

        assert result.iloc[i]["price_change"] == pytest.approx(
            expected
        )


def test_prepare_features_calculates_next_price():
    df = create_test_data()

    result = prepare_features(df)

    for i in range(len(result) - 1):
        assert result.iloc[i]["next_price"] == (
            result.iloc[i + 1]["silver_price"]
        )


def test_prepare_features_drops_incomplete_rows():
    df = create_test_data()

    result = prepare_features(df)

    assert result["lag_1"].notna().all()
    assert result["lag_2"].notna().all()
    assert result["lag_3"].notna().all()
    assert result["ma_3"].notna().all()
    assert result["ma_5"].notna().all()
    assert result["price_change"].notna().all()
    assert result["next_price"].notna().all()


def test_prepare_features_rejects_source_outside_tolerance():
    df = create_test_data()

    df.loc[
        df["source"] == "silfam",
        "created_at",
    ] += MERGE_TOLERANCE + pd.Timedelta(seconds=1)

    result = prepare_features(df)

    assert "silfam" in result.columns
    assert result["silfam"].isna().all()


def test_prepare_features_handles_missing_source():
    df = create_test_data()

    df = df[
        df["source"] != "noghresea"
    ]

    result = prepare_features(df)

    assert result.empty