"""
pytest 共通フィクスチャ定義

全テストで使用するセットアップとテスト環境を提供するモジュール。

【テスト環境の構成】
1. Redis モック: アプリケーション起動時の Redis 接続エラーを回避
2. テスト用 DB: SQLite in-memory で本番 DB に依存しない独立環境
3. FastAPI TestClient: HTTP リクエストを模擬してエンドポイントをテスト

【Redis モック戦略】
Redis に見立てたモックを sys.modules に事前登録することで、
app.main import 時にモックが使用される。これにより:
- Redis がなくてもテストが実行できる
- 各テストが独立し、セッション状態が共有されない
- CI 環境で外部依存を排除できる

【フィクスチャの依存関係】
db_session → client
  ↑
  └─ client が db_session を使用して DB をオーバーライド

【テスト実行の流れ】
1. pytest がこのファイルを読み込む
2. Redis モック → sys.modules に登録
3. app.main をインポート（モック Redis で起動）
4. 各テスト関数で client / db_session を注入
5. テスト終了時にテーブル自動削除
"""

import sys
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


# ============================================================================
# pytest カスタムオプション定義
# ============================================================================
def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="統合テストを実行する（実DB・実Redis使用）",
    )


# ============================================================================
# テスト設定定数
# ============================================================================
# Redis モック用定数
REDIS_MOCK_SESSION_ID = "test-session-id"
REDIS_MOCK_USER_ID = "12345678-1234-1234-1234-123456789abc"

# テスト用DB設定
TEST_DATABASE_URL = "sqlite:///:memory:"
TEST_DB_ECHO = False
TEST_DB_CHECK_SAME_THREAD = False

# ============================================================================
# Redis接続をモックしてからインポート（unit test 向け）
# ============================================================================
# pytest_configure より先にモックを設定する必要があるため sys.argv を直接参照する
# （pytest_addoption/pytest_configure の呼び出しは conftest.py の import より後になる）
IS_INTEGRATION = "--integration" in sys.argv

if not IS_INTEGRATION:
    mock_redis_manager_module = MagicMock()
    mock_redis_manager_instance = MagicMock()
    mock_redis_manager_instance.create_session.return_value = REDIS_MOCK_SESSION_ID
    mock_redis_manager_instance.is_session_valid.return_value = True
    mock_redis_manager_instance.get_user_id_from_session.return_value = REDIS_MOCK_USER_ID
    mock_redis_manager_instance.delete_session.return_value = True
    mock_redis_manager_module.redis_manager = mock_redis_manager_instance

    # sys.modules にモックを登録（app.main インポートの前に！）
    sys.modules["app.core.redis_manager"] = mock_redis_manager_module

# モック登録後にインポート
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

# ============================================================================
# テスト用DBエンジン設定
# ============================================================================
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": TEST_DB_CHECK_SAME_THREAD},
    echo=TEST_DB_ECHO,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    テスト用DBセッションを提供するフィクスチャ

    テスト同士の影響を完全に排除するため、次のテストは真っ白な DB から開始される。

    【動作】
    1. テスト関数実行前: SQLAlchemy モデルから全テーブルを SQLite に作成
    2. テスト関数実行中: DB セッションを提供して SQL クエリを実行
    3. テスト関数実行後: DB セッションを閉じてテーブルを完全削除

    【特徴】
    - SQLite in-memory: 本番 PostgreSQL に依存しない（テスト高速化）
    - scope="function": 各テスト関数ごとに独立した DB インスタンス
    - Base.metadata.create_all/drop_all: Alembic migration なしで自動スキーマ生成
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    FastAPI TestClientを提供するフィクスチャ

    本番 DB を使わず、テスト用 DB でエンドポイントを検証する。
    dependency_overrides を使用して、app.core.dependencies.get_db をオーバーライド。
    Redis セッション、パスワード検証なども含めて end-to-end テスト可能。

    【動作】
    1. テスト関数に db_session が注入される
    2. FastAPI dependency_overrides で get_db を差し替え
       (本番: PostgreSQL → テスト: SQLite in-memory)
    3. HTTP リクエスト → FastAPI が差し替えられた get_db を使用
       → テスト用 DB に接続
    4. テスト終了時に覆い被せを解除（dependency_overrides.clear()）
    """

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_redis():
    """
    Redisのモックを提供するフィクスチャ

    Redis を外部依存から解放し、セッション管理のテストを独立させる。
    注: 現在は conftest.py のモジュール読み込み時に自動モック化しているため、
    このフィクスチャのデフォルト使用頻度は低い。
    ただし、Redis 動作の詳細なテスト（セッション期限切れなど）を
    するときには明示的に mock_redis を指定可能。

    【モック内容】
    - create_session: REDIS_MOCK_SESSION_ID を返す
    - is_session_valid: 常に True（セッション有効）
    - get_user_id_from_session: REDIS_MOCK_USER_ID を返す
    - delete_session: 常に True（削除成功）

    【使用例】
    def test_logout_invalidates_session(client, mock_redis):
        # ログイン
        response = client.post("/api/auth/login", ...)

        # ログアウト
        response = client.post("/api/auth/logout")
        assert response.status_code == 200

        # Redis モックから delete_session が呼ばれたことをアサート
        assert mock_redis.delete_session.called
    """
    mock = MagicMock()
    mock.create_session.return_value = REDIS_MOCK_SESSION_ID
    mock.is_session_valid.return_value = True
    mock.get_user_id_from_session.return_value = REDIS_MOCK_USER_ID
    mock.delete_session.return_value = True

    with patch("app.core.redis_manager.redis_manager", mock):
        yield mock
