import pytest
from fastapi.testclient import TestClient

from app.models import AIModel
from app.services.api_key_service import APIKeyService


@pytest.fixture
def test_ai_model(db_session, test_user):
    model = AIModel(
        user_id=test_user.id,
        name='GPT-4',
        provider='openai',
        model_name='gpt-4',
        api_key='sk-test-key',
        is_active=True,
    )
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)
    return model


class TestModelEndpoints:
    def test_get_available_models(self, client: TestClient, auth_headers, test_ai_model):
        response = client.get('/api/v1/ai/models/available', headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'models' in data['data']
        assert len(data['data']['models']) >= 1
        assert all(m['source_type'] == 'api_key' for m in data['data']['models'])


class TestAPIKeyEndpoints:
    def test_create_api_key(self, client: TestClient, auth_headers):
        response = client.post(
            '/api/v1/api-keys',
            headers=auth_headers,
            json={'key_name': 'test-key', 'expires_days': 30, 'rate_limit': 60},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['api_key'].startswith('sk-')

    def test_list_api_keys(self, client: TestClient, auth_headers, db_session, test_user):
        APIKeyService.create_api_key(db=db_session, user_id=test_user.id, key_name='test-key', expires_days=30)
        response = client.get('/api/v1/api-keys', headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']['api_keys']) >= 1


class TestOpenAPIProxy:
    def test_list_models_without_auth(self, client: TestClient):
        assert client.get('/v1/models').status_code == 401

    def test_list_models_with_api_key(self, client: TestClient, db_session, test_user, test_ai_model):
        result = APIKeyService.create_api_key(db=db_session, user_id=test_user.id, key_name='test-key')
        response = client.get('/v1/models', headers={'Authorization': f"Bearer {result['api_key']}"})
        assert response.status_code == 200
        data = response.json()
        assert data['object'] == 'list'
        assert isinstance(data['data'], list)

    def test_chat_completions_without_auth(self, client: TestClient):
        response = client.post('/v1/chat/completions', json={'model': 'ai_model_1', 'messages': [{'role': 'user', 'content': 'hi'}]})
        assert response.status_code == 401
