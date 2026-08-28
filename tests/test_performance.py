import time
from concurrent.futures import ThreadPoolExecutor


def test_latest_price_performance(client):
    start = time.time()

    response = client.get("/prices/latest")

    elapsed = time.time() - start

    assert response.status_code in (200, 404)
    assert elapsed < 1.0


def test_history_performance(client):
    start = time.time()

    response = client.get(
        "/prices/history",
        params={
            "source": "tgju",
            "limit": 10,
        },
    )

    elapsed = time.time() - start

    assert response.status_code in (200, 404)
    assert elapsed < 1.0


def test_chart_performance(client):
    start = time.time()

    response = client.get(
        "/prices/chart",
        params={
            "source": "tgju",
            "point_count": 50,
        },
    )

    elapsed = time.time() - start

    assert response.status_code in (200, 404)
    assert elapsed < 1.0


def test_prediction_performance(client):
    start = time.time()

    response = client.get(
        "/prediction/predict"
    )

    elapsed = time.time() - start

    assert response.status_code in (200, 400, 404)
    assert elapsed < 2.0


def test_concurrent_latest_price(client):

    def request():
        start = time.time()

        response = client.get(
            "/prices/latest"
        )

        return response, time.time() - start

    with ThreadPoolExecutor(
        max_workers=10
    ) as executor:

        results = list(
            executor.map(
                lambda _: request(),
                range(10),
            )
        )

    times = [
        result[1]
        for result in results
    ]

    assert all(
        response.status_code in (200, 404)
        for response, _ in results
    )

    assert sum(times) / len(times) < 1.0
    assert max(times) < 2.0