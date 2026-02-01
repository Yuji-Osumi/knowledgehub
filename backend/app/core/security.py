"""
パスワードおよび認証セキュリティ関連のユーティリティ
"""

import re

import bcrypt


def hash_password(password: str) -> str:
    """
    平文パスワードをハッシュ化する

    Args:
        password: 平文パスワード

    Returns:
        ハッシュ化されたパスワード（str）
    """
    # パスワードが72バイトを超える場合はハッシュ化する
    if len(password.encode("utf-8")) > 72:
        password = password[:72]

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    平文パスワードとハッシュ化されたパスワードを検証する

    Args:
        plain_password: 平文パスワード（ユーザー入力）
        hashed_password: ハッシュ化されたパスワード（DB保存値）

    Returns:
        True: パスワード一致、False: 不一致
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    パスワード強度を検証する

    MVP 要件:
    - 最小 8 文字
    - 大文字を最低 1 文字含む
    - 小文字を最低 1 文字含む
    - 数字を最低 1 文字含む

    Args:
        password: 検証対象パスワード

    Returns:
        (is_valid, message) のタプル
        - is_valid: True なら合格、False なら不合格
        - message: 不合格時のエラーメッセージ
    """
    if len(password) < 8:
        return False, "パスワードは最小 8 文字以上である必要があります"

    if not re.search(r"[A-Z]", password):
        return False, "パスワードに大文字を最低 1 文字含める必要があります"

    if not re.search(r"[a-z]", password):
        return False, "パスワードに小文字を最低 1 文字含める必要があります"

    if not re.search(r"\d", password):
        return False, "パスワードに数字を最低 1 文字含める必要があります"

    return True, ""
