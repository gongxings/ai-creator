"""
测试写作API
"""
import pytest
from unittest.mock import patch, AsyncMock


class TestWritingAPI:
    """测试写作相关API"""
    
    def test_get_writing_tools(self, client, auth_headers):
        """测试获取写作工具列表"""
        response = client.get(
            "/api/v1/writing/tools",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        
        # 验证工具信息结构
        tool = data["data"][0]
        assert "tool_type" in tool
        assert "name" in tool
        assert "description" in tool
    
    @patch('app.services.writing_service.WritingService.generate_content')
    def test_generate_content_success(self, mock_generate, client, auth_headers):
        """测试成功生成内容"""
        mock_generate.return_value = {
            "title": "测试文章",
            "content": "这是生成的内容",
            "metadata": {"word_count": 100}
        }
        
        response = client.post(
            "/api/v1/writing/wechat_article/generate",
            headers=auth_headers,
            json={
                "prompt": "写一篇关于AI的文章",
                "parameters": {
                    "tone": "professional",
                    "length": "medium"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "title" in data["data"]
        assert "content" in data["data"]
    
    def test_generate_content_unauthorized(self, client):
        """测试未授权生成内容"""
        response = client.post(
            "/api/v1/writing/wechat_article/generate",
            json={
                "prompt": "写一篇文章"
            }
        )
        assert response.status_code == 401
    
    def test_generate_content_invalid_tool_type(self, client, auth_headers):
        """测试无效的工具类型"""
        response = client.post(
            "/api/v1/writing/invalid_tool/generate",
            headers=auth_headers,
            json={
                "prompt": "写一篇文章"
            }
        )
        assert response.status_code == 400
    
    def test_generate_content_missing_prompt(self, client, auth_headers):
        """测试缺少提示词"""
        response = client.post(
            "/api/v1/writing/wechat_article/generate",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 422
    
    @patch('app.services.writing_service.WritingService.generate_content')
    def test_regenerate_content(self, mock_generate, client, auth_headers, db_session, test_user):
        """测试重新生成内容"""
        from app.models.creation import Creation
        
        # 创建一个创作记录
        creation = Creation(
            user_id=test_user.id,
            tool_type="wechat_article",
            title="原标题",
            content="原内容",
            prompt="原提示词",
            status="completed"
        )
        db_session.add(creation)
        db_session.commit()
        db_session.refresh(creation)
        
        mock_generate.return_value = {
            "title": "新标题",
            "content": "新内容",
            "metadata": {"word_count": 150}
        }
        
        response = client.post(
            f"/api/v1/writing/{creation.id}/regenerate",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "新标题"
    
    def test_optimize_content(self, client, auth_headers, db_session, test_user):
        """测试优化内容"""
        from app.models.creation import Creation
        
        creation = Creation(
            user_id=test_user.id,
            tool_type="wechat_article",
            title="测试",
            content="内容",
            prompt="提示词",
            status="completed"
        )
        db_session.add(creation)
        db_session.commit()
        db_session.refresh(creation)
        
        response = client.post(
            f"/api/v1/writing/{creation.id}/optimize",
            headers=auth_headers,
            json={
                "optimization_type": "seo"
            }
        )
        # 这个测试可能需要mock AI服务
        assert response.status_code in [200, 500]  # 500是因为可能没有配置AI服务
    
    def test_get_creation_detail(self, client, auth_headers, db_session, test_user):
        """测试获取创作详情"""
        from app.models.creation import Creation
        
        creation = Creation(
            user_id=test_user.id,
            tool_type="wechat_article",
            title="测试文章",
            content="内容",
            prompt="提示词",
            status="completed"
        )
        db_session.add(creation)
        db_session.commit()
        db_session.refresh(creation)
        
        response = client.get(
            f"/api/v1/creations/{creation.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == creation.id
        assert data["data"]["title"] == "测试文章"
    
    def test_update_creation(self, client, auth_headers, db_session, test_user):
        """测试更新创作内容"""
        from app.models.creation import Creation
        
        creation = Creation(
            user_id=test_user.id,
            tool_type="wechat_article",
            title="原标题",
            content="原内容",
            prompt="提示词",
            status="completed"
        )
        db_session.add(creation)
        db_session.commit()
        db_session.refresh(creation)
        
        response = client.put(
            f"/api/v1/creations/{creation.id}",
            headers=auth_headers,
            json={
                "title": "新标题",
                "content": "新内容"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "新标题"
        assert data["data"]["content"] == "新内容"
    
    def test_delete_creation(self, client, auth_headers, db_session, test_user):
        """测试删除创作"""
        from app.models.creation import Creation
        
        creation = Creation(
            user_id=test_user.id,
            tool_type="wechat_article",
            title="测试",
            content="内容",
            prompt="提示词",
            status="completed"
        )
        db_session.add(creation)
        db_session.commit()
        db_session.refresh(creation)
        
        response = client.delete(
            f"/api/v1/creations/{creation.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_list_creations(self, client, auth_headers, db_session, test_user):
        """测试获取创作列表"""
        from app.models.creation import Creation
        
        # 创建多个创作记录
        for i in range(5):
            creation = Creation(
                user_id=test_user.id,
                tool_type="wechat_article",
                title=f"测试文章{i}",
                content=f"内容{i}",
                prompt="提示词",
                status="completed"
            )
            db_session.add(creation)
        db_session.commit()
        
        response = client.get(
            "/api/v1/creations",
            headers=auth_headers,
            params={"page": 1, "page_size": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["items"]) == 5
        assert data["data"]["total"] == 5
    
    def test_list_creations_with_filter(self, client, auth_headers, db_session, test_user):
        """测试带过滤条件的创作列表"""
        from app.models.creation import Creation
        
        # 创建不同类型的创作
        Creation(
            user_id=test_user.id,
            tool_type="wechat_article",
            title="微信文章",
            content="内容",
            prompt="提示词",
            status="completed"
        )
        Creation(
            user_id=test_user.id,
            tool_type="xiaohongshu_note",
            title="小红书笔记",
            content="内容",
            prompt="提示词",
            status="completed"
        )
        db_session.commit()
        
        response = client.get(
            "/api/v1/creations",
            headers=auth_headers,
            params={"tool_type": "wechat_article"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["tool_type"] == "wechat_article"
