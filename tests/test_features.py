import pytest
import pandas as pd
from app.prediction.features import add_lag
from app.prediction.features import add_moving_average
from app.prediction.features import add_price_change
from app.prediction.features import prepare_features

def test_add_lag():
    result = add_lag(pd.Series([10, 20, 30]), 1)
    assert pd.isna(result.iloc[0])
    assert result.iloc[1:].tolist() == [10, 20]


def test_add_moving_average():
    result = add_moving_average(pd.Series([10, 20, 30]), 3)
    assert result.iloc[2] == 20


def test_add_price_change():
    result = add_price_change(pd.Series([100, 110]))
    assert result.iloc[1] == pytest.approx(0.1)


def test_prepare_features_sorts_and_drops_na():
    df = pd.DataFrame({
        "price": [500, 300, 400, 200, 100, 600],
        "fetched_at": pd.to_datetime([
            "2026-01-01 14:00",
            "2026-01-01 12:00",
            "2026-01-01 13:00",
            "2026-01-01 11:00",
            "2026-01-01 10:00",
            "2026-01-01 15:00"
        ])
    })

    result = prepare_features(df)

    assert result["fetched_at"].is_monotonic_increasing
    assert not result.isna().any().any()