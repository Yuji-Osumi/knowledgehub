"""
Redis セッション管理
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional

import redis

from app.core.config import settings
from app.core.logging import logger


class RedisSessionManager:
    """Redis を使用したセッション管理クラス"""

    def __init__(self, redis_url: str):
        """
        Redis コネクション初期化

        Args:
            redis_url: Redis 接続 URL（例: redis://redis:6379/0）

        Raises:
            redis.ConnectionError: Redis 接続失敗時
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # 接続確認
            self.redis_client.ping()
            logger.info("✓ Redis 接続成功")
        except redis.ConnectionError as e:
            logger.error(f"✗ Redis 接続失敗: {e}")
            raise

    def create_session(self, user_id: str, ttl_hours: int = 24) -> str:
        """
        セッションを作成して Redis に保存

        Args:
            user_id: ユーザー ID（UUID）
            ttl_hours: セッション有効期限（時間単位、デフォルト: 24）

        Returns:
            生成されたセッション ID

        Raises:
            redis.ConnectionError: Redis 接続失敗時
        """
        session_id = uuid.uuid4().hex
        exp_timestamp = int((datetime.utcnow() + timedelta(hours=ttl_hours)).timestamp())

        session_data = {
            "user_id": user_id,
            "exp_timestamp": exp_timestamp,
        }

        try:
            # Redis に保存（TTL 付き）
            ttl_seconds = ttl_hours * 3600
            self.redis_client.setex(
                f"session:{session_id}",
                ttl_seconds,
                json.dumps(session_data),
            )
            logger.debug(f"セッション作成: session_id={session_id}, user_id={user_id}")
            return session_id
        except redis.ConnectionError as e:
            logger.error(f"セッション作成失敗: {e}")
            raise

    def get_session(self, session_id: str) -> Optional[dict]:
        """
        セッション ID からセッションデータを取得

        Args:
            session_id: セッション ID

        Returns:
            セッションデータ（user_id, exp_timestamp）または None（セッション未検出）

        Raises:
            redis.ConnectionError: Redis 接続失敗時
        """
        try:
            session_data = self.redis_client.get(f"session:{session_id}")
            if session_data is None:
                return None
            return json.loads(session_data)
        except redis.ConnectionError as e:
            logger.error(f"セッション取得失敗: {e}")
            raise

    def delete_session(self, session_id: str) -> bool:
        """
        セッションを削除（ログアウト時に使用）

        Args:
            session_id: セッション ID

        Returns:
            True: 削除成功、False: セッション未検出

        Raises:
            redis.ConnectionError: Redis 接続失敗時
        """
        try:
            result = self.redis_client.delete(f"session:{session_id}")
            logger.debug(f"セッション削除: session_id={session_id}")
            return result > 0
        except redis.ConnectionError as e:
            logger.error(f"セッション削除失敗: {e}")
            raise

    def is_session_valid(self, session_id: str) -> bool:
        """
        セッションの有効性を確認

        Args:
            session_id: セッション ID

        Returns:
            True: セッション有効、False: 期限切れまたは未検出

        Raises:
            redis.ConnectionError: Redis 接続失敗時
        """
        try:
            session_data = self.get_session(session_id)
            if session_data is None:
                return False

            exp_timestamp = session_data.get("exp_timestamp")
            current_timestamp = int(datetime.utcnow().timestamp())

            return current_timestamp < exp_timestamp
        except redis.ConnectionError as e:
            logger.error(f"セッション有効性確認失敗: {e}")
            raise


# グローバル インスタンス
redis_manager = RedisSessionManager(settings.REDIS_URL)
