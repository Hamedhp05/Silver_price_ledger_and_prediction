import pandas as pd
from app.prediction.features import prepare_features


def test_prepare_features():

    base_time = pd.Timestamp(
        "2026-08-28 18:00:00"
    )

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

    df = pd.DataFrame(rows)

    result = prepare_features(df)

    assert not result.empty
    assert "lag_1" in result.columns
    assert "ma_3" in result.columns
    assert "ma_5" in result.columns
    assert "price_change" in result.columns
    assert "next_price" in result.columns


def test_prepare_features_rejects_unmatched_sources():
    df = pd.DataFrame([
        {
            "source": "tgju",
            "price": 470000,
            "created_at": pd.Timestamp(
                "2026-08-28 18:00:00"
            ),
            "fetched_at": pd.Timestamp(
                "2026-08-28 18:00:00"
            ),
        },
        {
            "source": "silfam",
            "price": 440000,
            "created_at": pd.Timestamp(
                "2026-08-28 18:05:00"
            ),
            "fetched_at": pd.Timestamp(
                "2026-08-28 18:05:00"
            ),
        },
    ])

    result = prepare_features(df)

    assert result.empty