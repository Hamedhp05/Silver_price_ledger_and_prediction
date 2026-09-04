import time
from concurrent.futures import ThreadPoolExecutor


def measure_request(client, method, url, **kwargs):
    start = time.perf_counter()
    response = client.request(method, url, **kwargs)
    elapsed = time.perf_counter() - start
    return response, elapsed


def test_latest_price_performance(anon_client):
    response, elapsed = measure_request(anon_client,"GET","/prices/latest")

    assert response.status_code == 200
    assert elapsed < 1.0


def test_history_performance(anon_client):
    response, elapsed = measure_request(anon_client,"GET","/prices/history",
        params={
            "source": "tgju",
            "limit": 10,
        },
    )

    assert response.status_code == 200
    assert elapsed < 1.0


def test_chart_performance(anon_client):
    response, elapsed = measure_request(anon_client,"GET","/prices/chart",
        params={
            "source": "tgju",
            "point_count": 50,
        },
    )

    assert response.status_code == 200
    assert elapsed < 1.0


def test_prediction_performance(anon_client):
    response, elapsed = measure_request(anon_client,"GET","/prediction/predict")

    assert response.status_code in (200, 400)
    assert elapsed < 2.0


def test_concurrent_latest_price(anon_client):

    def request():
        return measure_request(anon_client,"GET","/prices/latest")

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: request(), range(10)))

    times = [elapsed for _, elapsed in results]

    assert all( response.status_code == 200 for response, _ in results)

    assert sum(times) / len(times) < 1.0
    assert max(times) < 2.0