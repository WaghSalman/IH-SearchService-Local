import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.join(os.path.dirname(__file__), '../ih_search_service'))
import pytest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from ih_search_service.app import app


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


@patch('model.influencer.Influencer.search_by_id')
def test_search_by_id_success(mock_search_by_id, client):
    mock_search_by_id.return_value = [
        MagicMock(to_dict=lambda: {"id": "123", "name": "John Doe"})]
    response = client.get('/searchById?influencer_id=123')
    assert response.status_code == 200
    assert response.json == {'success': True,
                             'data': [{"id": "123", "name": "John Doe"}]}


def test_search_by_id_no_id(client):
    response = client.get('/searchById')
    assert response.status_code == 400
    assert response.json == {'success': False,
                             'error': 'No influencer_id parameter provided'}


@patch('model.influencer.Influencer.search_by_name')
def test_search_by_name_success(mock_search_by_name, client):
    mock_search_by_name.return_value = [
        MagicMock(to_dict=lambda: {"id": "123", "name": "John Doe"})]
    response = client.get('/searchByName?name=John Doe')
    assert response.status_code == 200
    assert response.json == {'success': True,
                             'data': [{"id": "123", "name": "John Doe"}]}


def test_search_by_name_no_name(client):
    response = client.get('/searchByName')
    assert response.status_code == 400
    assert response.json == {'success': False,
                             'error': 'No name parameter provided'}


@patch('model.influencer.Influencer.search_by_location')
def test_search_by_location_success(mock_search_by_location, client):
    mock_search_by_location.return_value = [MagicMock(
        to_dict=lambda: {"id": "123", "name": "John Doe", "location": "New York"})]
    response = client.get('/searchByLocation?location=New York')
    assert response.status_code == 200
    assert response.json == {'success': True, 'data': [
        {"id": "123", "name": "John Doe", "location": "New York"}]}


def test_search_by_location_no_location(client):
    response = client.get('/searchByLocation')
    assert response.status_code == 400
    assert response.json == {'success': False,
                             'error': 'No location parameter provided'}


@patch('model.influencer.Influencer.search_by_platform')
def test_search_by_platform_success(mock_search_by_platform, client):
    mock_search_by_platform.return_value = [MagicMock(
        to_dict=lambda: {"id": "123", "name": "John Doe", "platforms": ["INSTAGRAM"]})]
    with patch('enums.platform.Platform', **{"__getitem__": lambda self, key: key}):
        response = client.get('/searchByPlatform?platform=INSTAGRAM')
    assert response.status_code == 200
    assert response.json == {'success': True, 'data': [
        {"id": "123", "name": "John Doe", "platforms": ["INSTAGRAM"]}]}


def test_search_by_platform_no_platform(client):
    response = client.get('/searchByPlatform')
    assert response.status_code == 400
    assert response.json == {'success': False,
                             'error': 'No platform parameter provided'}


def test_search_by_platform_invalid_platform(client):
    with patch('enums.platform.Platform', **{"__getitem__": lambda self, key: (_ for _ in ()).throw(KeyError)}):
        response = client.get('/searchByPlatform?platform=INVALID')
    assert response.status_code == 400
    assert response.json['success'] is False


@patch('model.influencer.Influencer.search_by_category')
def test_search_by_category_success(mock_search_by_category, client):
    mock_search_by_category.return_value = [
        MagicMock(to_dict=lambda: {"id": "123", "category": "FASHION"})]
    with patch('enums.category.Category', **{"__getitem__": lambda self, key: key}):
        response = client.get('/searchByCategory?category=FASHION')
    assert response.status_code == 200
    assert response.json['success'] is True


def test_search_by_category_no_category(client):
    response = client.get('/searchByCategory')
    assert response.status_code == 400
    assert response.json == {'success': False,
                             'error': 'No category parameter provided'}


def test_search_by_category_invalid_category(client):
    with patch('enums.category.Category', **{"__getitem__": lambda self, key: (_ for _ in ()).throw(KeyError)}):
        response = client.get('/searchByCategory?category=INVALID')
    assert response.status_code == 400
    assert response.json['success'] is False


@patch('model.influencer.Influencer.search_by_gender')
def test_search_by_gender_success(mock_search_by_gender, client):
    mock_search_by_gender.return_value = [
        MagicMock(to_dict=lambda: {"id": "123", "gender": "MALE"})]
    with patch('enums.gender.Gender', **{"__getitem__": lambda self, key: key}):
        response = client.get('/searchByGender?gender=MALE')
    assert response.status_code == 200
    assert response.json['success'] is True


def test_search_by_gender_no_gender(client):
    response = client.get('/searchByGender')
    assert response.status_code == 400
    assert response.json == {'success': False,
                             'error': 'No gender parameter provided'}


def test_search_by_gender_invalid_gender(client):
    with patch('enums.gender.Gender', **{"__getitem__": lambda self, key: (_ for _ in ()).throw(KeyError)}):
        response = client.get('/searchByGender?gender=INVALID')
    assert response.status_code == 400
    assert response.json['success'] is False


@patch('model.metrics.Metrics.search_by_engagement_rate')
def test_search_by_engagement_rate_success(mock_search_by_engagement_rate, client):
    mock_search_by_engagement_rate.return_value = [
        MagicMock(to_dict=lambda: {"id": "f27ebf1a-9230-4503-8185-2fb913293eb5", "engagement_rate": 2.5, "total_followers": 1000, "total_followers_str": "1k"})]
    with patch('enums.platform.Platform', **{"__getitem__": lambda self, key: key}):
        response = client.get(
            '/searchByEngagementRate?min_engagement_rate=1.0&max_engagement_rate=3.0&platform=INSTAGRAM')
    assert response.status_code == 200
    assert response.json['success'] is True


def test_search_by_engagement_rate_no_platform(client):
    response = client.get('/searchByEngagementRate?min_engagement_rate=1.0')
    assert response.status_code == 400
    assert response.json['success'] is False


def test_search_by_engagement_rate_no_min(client):
    with patch('enums.platform.Platform', **{"__getitem__": lambda self, key: key}):
        response = client.get('/searchByEngagementRate?platform=INSTAGRAM')
    assert response.status_code == 400
    assert response.json['success'] is False


@patch('model.metrics.Metrics.search_by_followers_count')
def test_search_by_followers_count_success(mock_search_by_followers_count, client):
    mock_search_by_followers_count.return_value = [
        MagicMock(to_dict=lambda: {"id": "4a9d813d-1dd0-4762-af3a-96986e10ffe0", "total_followers": 10000, "total_followers_str": "10k"})]
    with patch('enums.platform.Platform', **{"__getitem__": lambda self, key: key}):
        response = client.get(
            '/searchByFollowersCount?min_followers=1000&max_followers=20000&platform=INSTAGRAM')
    assert response.status_code == 200
    assert response.json['success'] is True


def test_search_by_followers_count_no_platform(client):
    response = client.get('/searchByFollowersCount?min_followers=1000')
    assert response.status_code == 400
    assert response.json['success'] is False


def test_search_by_followers_count_no_min(client):
    with patch('enums.platform.Platform', **{"__getitem__": lambda self, key: key}):
        response = client.get('/searchByFollowersCount?platform=INSTAGRAM')
    assert response.status_code == 400
    assert response.json['success'] is False


def test_search_by_metrics_missing_json(client):
    response = client.post('/search_by_metrics',
                           data="notjson", content_type='application/json')
    assert response.status_code == 500
    assert response.json['success'] is False


def test_search_influencers_invalid_platform(client):
    response = client.get('/searchInfluencers?platform=INVALID')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['data'] == []


@patch('model.influencer.Influencer.search_by_name')
def test_search_by_name_with_db_cursor(mock_search_by_name, client):
    # Simulate DB-backed method returning (iterable, last_key)
    items = [MagicMock(to_dict=lambda: {"id": "1"}), MagicMock(to_dict=lambda: {"id": "2"})]
    last_key = {'last': 'key'}
    mock_search_by_name.return_value = (items, last_key)

    response = client.get('/searchByName?name=John&limit=1')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'next_token' in response.json


@patch('model.posts.Post.get_posts_by_influencer_id')
def test_posts_by_influencer_with_db_cursor(mock_get_posts, client):
    posts = [
        SimpleNamespace(
            post_id='p1',
            influencer_id='123',
            platform='INSTAGRAM',
            title='t1',
            url='u1',
            created_at=datetime.utcnow(),
            post_created_at=datetime.utcnow(),
        ),
        SimpleNamespace(
            post_id='p2',
            influencer_id='123',
            platform='INSTAGRAM',
            title='t2',
            url='u2',
            created_at=datetime.utcnow(),
            post_created_at=datetime.utcnow(),
        ),
    ]
    last_key = {'cursor': 'abc'}
    mock_get_posts.return_value = (posts, last_key)

    response = client.get('/posts/search/influencer?influencer_id=123&limit=1')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'next_token' in response.json
