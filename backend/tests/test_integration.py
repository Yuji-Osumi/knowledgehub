"""
統合テスト: API エンドポイント全体の動作検証

【テスト範囲】
1. 認証フロー: signup → login → logout → me
2. 記事CRUD: create → read → update → delete
3. エラーハンドリング: 400/401/404
4. 認可: 他ユーザーの記事操作不可

【実行環境】
- 実DB: PostgreSQL（docker compose内）
- セッション: Redis（docker compose内）
"""

import uuid

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def unique_email(prefix: str = "it") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


# ============================================================================
# フィクスチャ
# ============================================================================


@pytest.fixture(scope="function")
def integration_client():
    """統合テスト用クライアント（実DB/Redis使用）"""
    return TestClient(app)


@pytest.fixture(scope="function")
def setup_user(integration_client):
    """テスト用ユーザーを作成してログイン"""
    email = unique_email("setup")

    # ユーザー作成
    signup_response = integration_client.post(
        "/api/auth/signup",
        json={
            "email": email,
            "password": "Password123",
            "password_confirm": "Password123",
            "display_name": "テストユーザー",
        },
    )
    assert signup_response.status_code == 201

    # ログイン
    login_response = integration_client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "Password123",
        },
    )
    assert login_response.status_code == 200

    return {
        "email": email,
        "password": "Password123",
        "display_name": "テストユーザー",
    }


# ============================================================================
# テストクラス: 認証フロー
# ============================================================================


class TestAuthenticationFlow:
    """認証エンドポイントの統合テスト"""

    def test_signup_success(self, integration_client):
        """【正常系】新規ユーザー登録"""
        email = unique_email("signup")

        response = integration_client.post(
            "/api/auth/signup",
            json={
                "email": email,
                "password": "Password123",
                "password_confirm": "Password123",
                "display_name": "新規ユーザー",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == email
        assert "public_id" in data
        assert integration_client.cookies.get("session_id") is not None

    def test_signup_duplicate_email(self, integration_client):
        """【エラー系】重複メールアドレス"""
        email = unique_email("dup")

        # 1回目: 成功
        response1 = integration_client.post(
            "/api/auth/signup",
            json={
                "email": email,
                "password": "Password123",
                "password_confirm": "Password123",
                "display_name": "ユーザー",
            },
        )
        assert response1.status_code == 201

        # 2回目: 失敗
        response2 = integration_client.post(
            "/api/auth/signup",
            json={
                "email": email,
                "password": "Password123",
                "password_confirm": "Password123",
                "display_name": "ユーザー",
            },
        )
        assert response2.status_code == 400
        assert response2.json()["error"]["code"] == "USER_ALREADY_EXISTS"

    def test_signup_validation_error(self, integration_client):
        """【バリデーション】メールフォーマットエラー"""
        response = integration_client.post(
            "/api/auth/signup",
            json={
                "email": "invalid-email",
                "password": "Password123",
                "password_confirm": "Password123",
                "display_name": "ユーザー",
            },
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_login_success(self, integration_client, setup_user):
        """【正常系】ログイン"""
        response = integration_client.post(
            "/api/auth/login",
            json={
                "email": setup_user["email"],
                "password": "Password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == setup_user["email"]
        assert integration_client.cookies.get("session_id") is not None

    def test_login_unauthorized(self, integration_client):
        """【認証失敗】パスワード間違い"""
        email = unique_email("wrongpw")

        # ユーザー作成
        integration_client.post(
            "/api/auth/signup",
            json={
                "email": email,
                "password": "Password123",
                "password_confirm": "Password123",
                "display_name": "ユーザー",
            },
        )

        # 間違ったパスワードでログイン
        response = integration_client.post(
            "/api/auth/login",
            json={
                "email": email,
                "password": "WrongPassword",
            },
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"

    def test_me_with_session(self, integration_client, setup_user):
        """【正常系】ログイン済みのme取得"""
        # Cookie にセッションが設定されているはず
        response = integration_client.get("/api/auth/me")
        assert response.status_code == 200
        assert response.json()["email"] == setup_user["email"]

    def test_me_without_session(self, integration_client):
        """【認証なし】セッションなしのme取得"""
        response = integration_client.get("/api/auth/me")
        assert response.status_code == 401


# ============================================================================
# テストクラス: 記事CRUD
# ============================================================================


class TestArticleCRUD:
    """記事エンドポイントの統合テスト"""

    def test_create_article_success(self, integration_client, setup_user):
        """【正常系】記事作成"""
        response = integration_client.post(
            "/api/articles",
            json={
                "title": "テスト記事",
                "content": "テスト本文",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "テスト記事"
        assert data["content"] == "テスト本文"
        assert "public_id" in data

    def test_create_article_validation_error(self, integration_client, setup_user):
        """【バリデーション】タイトル空文字列"""
        response = integration_client.post(
            "/api/articles",
            json={
                "title": "",
                "content": "本文",
            },
        )
        assert response.status_code == 400

    def test_get_article_success(self, integration_client, setup_user):
        """【正常系】記事取得"""
        # 記事作成
        create_response = integration_client.post(
            "/api/articles",
            json={
                "title": "テスト記事",
                "content": "本文",
            },
        )
        public_id = create_response.json()["public_id"]

        # 記事取得
        response = integration_client.get(f"/api/articles/{public_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "テスト記事"

    def test_get_article_not_found(self, integration_client, setup_user):
        """【404】存在しない記事"""
        response = integration_client.get(f"/api/articles/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"

    def test_update_article_success(self, integration_client, setup_user):
        """【正常系】記事更新"""
        # 記事作成
        create_response = integration_client.post(
            "/api/articles",
            json={
                "title": "元々のタイトル",
                "content": "元々の本文",
            },
        )
        public_id = create_response.json()["public_id"]

        # 記事更新
        response = integration_client.put(
            f"/api/articles/{public_id}",
            json={
                "title": "新しいタイトル",
                "content": "新しい本文",
            },
        )
        assert response.status_code == 200
        assert response.json()["title"] == "新しいタイトル"

    def test_delete_article_success(self, integration_client, setup_user):
        """【正常系】記事削除"""
        # 記事作成
        create_response = integration_client.post(
            "/api/articles",
            json={
                "title": "削除対象",
                "content": "本文",
            },
        )
        public_id = create_response.json()["public_id"]

        # 記事削除
        response = integration_client.delete(f"/api/articles/{public_id}")
        assert response.status_code == 204

        # 削除確認
        get_response = integration_client.get(f"/api/articles/{public_id}")
        assert get_response.status_code == 404


# ============================================================================
# テストクラス: 認可
# ============================================================================


class TestAuthorization:
    """認可エンドポイントの統合テスト"""

    def test_update_other_user_article_returns_404(self, integration_client, setup_user):
        """【404マスキング】他ユーザーの記事更新"""
        user2_email = unique_email("user2")

        # ユーザー1が記事作成
        create_response = integration_client.post(
            "/api/articles",
            json={
                "title": "ユーザー1の記事",
                "content": "本文",
            },
        )
        public_id = create_response.json()["public_id"]

        # ユーザー2でログイン
        integration_client.post("/api/auth/logout")
        integration_client.post(
            "/api/auth/signup",
            json={
                "email": user2_email,
                "password": "Password123",
                "password_confirm": "Password123",
                "display_name": "ユーザー2",
            },
        )
        integration_client.post(
            "/api/auth/login",
            json={
                "email": user2_email,
                "password": "Password123",
            },
        )

        # ユーザー2がユーザー1の記事を更新しようとする
        response = integration_client.put(
            f"/api/articles/{public_id}",
            json={
                "title": "改変されたタイトル",
                "content": "改変本文",
            },
        )
        # 認可失敗でも404で返却（存在秘匿）
        assert response.status_code == 404

    def test_delete_other_user_article_returns_404(self, integration_client, setup_user):
        """【404マスキング】他ユーザーの記事削除"""
        user3_email = unique_email("user3")

        # ユーザー1が記事作成
        create_response = integration_client.post(
            "/api/articles",
            json={
                "title": "ユーザー1の記事",
                "content": "本文",
            },
        )
        public_id = create_response.json()["public_id"]

        # ユーザー2でログイン
        integration_client.post("/api/auth/logout")
        integration_client.post(
            "/api/auth/signup",
            json={
                "email": user3_email,
                "password": "Password123",
                "password_confirm": "Password123",
                "display_name": "ユーザー3",
            },
        )
        integration_client.post(
            "/api/auth/login",
            json={
                "email": user3_email,
                "password": "Password123",
            },
        )

        # ユーザー2がユーザー1の記事を削除しようとする
        response = integration_client.delete(f"/api/articles/{public_id}")
        # 認可失敗でも404で返却（存在秘匿）
        assert response.status_code == 404


# ============================================================================
# テストクラス: 未認証アクセス
# ============================================================================


class TestUnauthenticatedAccess:
    """認証なしのアクセス制限テスト"""

    def test_create_article_without_auth(self, integration_client):
        """【401】セッションなしで記事作成"""
        response = integration_client.post(
            "/api/articles",
            json={
                "title": "テスト",
                "content": "本文",
            },
        )
        assert response.status_code == 401

    def test_list_articles_without_auth(self, integration_client):
        """【401】セッションなしで記事一覧取得"""
        response = integration_client.get("/api/articles")
        assert response.status_code == 401
