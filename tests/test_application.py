import pytest
import requests

from pyronaut.test import MicronautTest, micronaut_test_fixture


@pytest.fixture
def my_context(request):
    fixture = micronaut_test_fixture(
        request,
        MicronautTest(environments=["test"], transactional=False),
    )
    yield fixture
    fixture.stop()


@pytest.fixture
def client(my_context):
    return requests.with_context(my_context)


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Sentiment Analysis with VADER and Pyronaut" in response.text


def test_positive_review(client):
    response = client.post(
        "/api/reviews/analyze",
        json={"text": "I love this coffee grinder. It works perfectly!"},
    )

    assert response.status_code == 200
    analysis = response.json()
    assert analysis["label"] == "positive"
    assert analysis["compound"] >= 0.05
    assert analysis["positive"] > analysis["negative"]


def test_negative_review(client):
    response = client.post(
        "/api/reviews/analyze",
        json={"text": "This robot vacuum is terrible and completely useless."},
    )

    assert response.status_code == 200
    analysis = response.json()
    assert analysis["label"] == "negative"
    assert analysis["compound"] <= -0.05
    assert analysis["negative"] > analysis["positive"]


def test_blank_review_is_rejected(client):
    response = client.post(
        "/api/reviews/analyze",
        json={"text": ""},
    )

    assert response.status_code == 400, (
        f"expected 400, got {response.status_code}: {response.text}"
    )
