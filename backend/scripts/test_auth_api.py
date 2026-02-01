"""
認証フロー統合テストスクリプト

以下のフローを検証：
1. ユーザー登録（signup）
2. ログイン（login）
3. 認証状態で API 利用（articles）
4. ログアウト（logout）
5. 認証エラーハンドリング（400, 401）

テスト後は自動的にテストデータをクリーンアップ
"""

import subprocess
import sys
import time
import uuid
from typing import Any

import requests

# テスト対象のAPI ベースURL
API_BASE_URL = "http://localhost:8000/api"

# テスト結果を格納
test_results: list[dict[str, Any]] = []

# テスト用の認証情報（ユニークメールアドレスを使用）
UNIQUE_SUFFIX = str(uuid.uuid4())[:8]
TEST_USER = {
    "email": f"test_auth_{UNIQUE_SUFFIX}@example.com",
    "password": "TestPassword123",
    "display_name": "Test User",
}


def log_test(test_name: str, expected_status: int, actual_status: int, passed: bool) -> None:
    """テスト結果をログ出力"""
    status_symbol = "✓" if passed else "✗"
    test_results.append(
        {
            "name": test_name,
            "expected": expected_status,
            "actual": actual_status,
            "passed": passed,
        }
    )
    print(f"{status_symbol} {test_name}: Expected {expected_status}, Got {actual_status}")


def test_1_signup_success() -> str | None:
    """1. Signup 成功（201）"""
    print("\n[1/10] Testing Signup Success (201)...")
    try:
        payload = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "password_confirm": TEST_USER["password"],
            "display_name": TEST_USER["display_name"],
        }
        response = requests.post(f"{API_BASE_URL}/auth/signup", json=payload, timeout=5)
        passed = response.status_code == 201
        log_test("Signup Success", 201, response.status_code, passed)
        if not passed:
            print(f"  Response: {response.text}")
        if passed:
            data = response.json()
            print(f"  User created: {data.get('email')}")
            return response.cookies.get("session_id")
        return None
    except Exception as e:
        log_test("Signup Success", 201, 0, False)
        print(f"  Error: {e}")
        return None


def test_2_signup_duplicate_email() -> None:
    """2. 重複メールで Signup（400）"""
    print("\n[2/10] Testing Signup with Duplicate Email (400)...")
    try:
        payload = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "password_confirm": TEST_USER["password"],
            "display_name": TEST_USER["display_name"],
        }
        response = requests.post(f"{API_BASE_URL}/auth/signup", json=payload, timeout=5)
        passed = response.status_code == 400
        log_test("Signup Duplicate Email", 400, response.status_code, passed)
        if response.status_code >= 400:
            print(f"  Error: {response.json()}")
    except Exception as e:
        log_test("Signup Duplicate Email", 400, 0, False)
        print(f"  Error: {e}")


def test_3_login_success(session_id: str | None) -> str | None:
    """3. Login 成功（200）"""
    print("\n[3/10] Testing Login Success (200)...")
    try:
        payload = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
        }
        cookies = {"session_id": session_id} if session_id else {}
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=payload,
            cookies=cookies,
            timeout=5,
        )
        passed = response.status_code == 200
        log_test("Login Success", 200, response.status_code, passed)
        if passed:
            data = response.json()
            print(f"  Logged in as: {data.get('email')}")
            return response.cookies.get("session_id")
        return None
    except Exception as e:
        log_test("Login Success", 200, 0, False)
        print(f"  Error: {e}")
        return None


def test_4_login_invalid_credentials() -> None:
    """4. 無効な認証情報でログイン（401）"""
    print("\n[4/10] Testing Login with Invalid Credentials (401)...")
    try:
        payload = {
            "email": TEST_USER["email"],
            "password": "WrongPassword123",
        }
        response = requests.post(f"{API_BASE_URL}/auth/login", json=payload, timeout=5)
        passed = response.status_code == 401
        log_test("Login Invalid Credentials", 401, response.status_code, passed)
        if response.status_code >= 400:
            print(f"  Error: {response.json()}")
    except Exception as e:
        log_test("Login Invalid Credentials", 401, 0, False)
        print(f"  Error: {e}")


def test_5_get_me_with_auth(session_id: str | None) -> None:
    """5. 認証状態で /auth/me を取得（200）"""
    print("\n[5/10] Testing GET /auth/me with Auth (200)...")
    try:
        cookies = {"session_id": session_id} if session_id else {}
        response = requests.get(f"{API_BASE_URL}/auth/me", cookies=cookies, timeout=5)
        passed = response.status_code == 200
        log_test("GET /auth/me (Authenticated)", 200, response.status_code, passed)
        if passed:
            data = response.json()
            print(f"  User info: {data.get('email')}")
    except Exception as e:
        log_test("GET /auth/me (Authenticated)", 200, 0, False)
        print(f"  Error: {e}")


def test_6_get_me_without_auth() -> None:
    """6. 認証なしで /auth/me を取得（401）"""
    print("\n[6/10] Testing GET /auth/me without Auth (401)...")
    try:
        response = requests.get(f"{API_BASE_URL}/auth/me", timeout=5)
        passed = response.status_code == 401
        log_test("GET /auth/me (Unauthenticated)", 401, response.status_code, passed)
        if response.status_code >= 400:
            print(f"  Error: {response.json()}")
    except Exception as e:
        log_test("GET /auth/me (Unauthenticated)", 401, 0, False)
        print(f"  Error: {e}")


def test_7_create_article_with_auth(session_id: str | None) -> None:
    """7. 認証状態で記事作成（201）"""
    print("\n[7/10] Testing POST /articles with Auth (201)...")
    try:
        payload = {
            "title": "Test Article from Auth Flow",
            "content": "This article was created by authenticated user",
            "folder_id": None,
        }
        cookies = {"session_id": session_id} if session_id else {}
        response = requests.post(
            f"{API_BASE_URL}/articles",
            json=payload,
            cookies=cookies,
            timeout=5,
        )
        passed = response.status_code == 201
        log_test("POST /articles (Authenticated)", 201, response.status_code, passed)
        if passed:
            data = response.json()
            print(f"  Article created: {data.get('public_id')}")
    except Exception as e:
        log_test("POST /articles (Authenticated)", 201, 0, False)
        print(f"  Error: {e}")


def test_8_create_article_without_auth() -> None:
    """8. 認証なしで記事作成（401）"""
    print("\n[8/10] Testing POST /articles without Auth (401)...")
    try:
        payload = {
            "title": "Unauthorized Article",
            "content": "This should fail",
            "folder_id": None,
        }
        response = requests.post(f"{API_BASE_URL}/articles", json=payload, timeout=5)
        passed = response.status_code == 401
        log_test("POST /articles (Unauthenticated)", 401, response.status_code, passed)
        if response.status_code >= 400:
            print(f"  Error: {response.json()}")
    except Exception as e:
        log_test("POST /articles (Unauthenticated)", 401, 0, False)
        print(f"  Error: {e}")


def test_9_logout_success(session_id: str | None) -> None:
    """9. ログアウト成功（204）"""
    print("\n[9/10] Testing Logout Success (204)...")
    try:
        cookies = {"session_id": session_id} if session_id else {}
        response = requests.post(f"{API_BASE_URL}/auth/logout", cookies=cookies, timeout=5)
        passed = response.status_code == 204
        log_test("Logout Success", 204, response.status_code, passed)
        if passed:
            print(f"  Cookie cleared: session_id removed")
    except Exception as e:
        log_test("Logout Success", 204, 0, False)
        print(f"  Error: {e}")


def test_10_get_me_after_logout() -> None:
    """10. ログアウト後に /auth/me を取得（401）"""
    print("\n[10/10] Testing GET /auth/me after Logout (401)...")
    try:
        response = requests.get(f"{API_BASE_URL}/auth/me", timeout=5)
        passed = response.status_code == 401
        log_test("GET /auth/me (After Logout)", 401, response.status_code, passed)
        if response.status_code >= 400:
            print(f"  Error: {response.json()}")
    except Exception as e:
        log_test("GET /auth/me (After Logout)", 401, 0, False)
        print(f"  Error: {e}")


def print_summary() -> None:
    """テスト結果のサマリーを出力"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total = len(test_results)
    passed = sum(1 for t in test_results if t["passed"])
    failed = total - passed

    for result in test_results:
        status = "✓" if result["passed"] else "✗"
        print(f"{status} {result['name']}: {result['expected']} (Got {result['actual']})")

    print("\n" + "-" * 60)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print("-" * 60)

    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


def cleanup_test_user() -> None:
    """テスト用ユーザーをクリーンアップ（スキップ - ユニークメール使用）"""
    pass


def main() -> int:
    """メイン処理"""
    print("=" * 60)
    print("Authentication Flow Integration Tests")
    print("=" * 60)
    print(f"Target API: {API_BASE_URL}")
    print(f"Test User: {TEST_USER['email']}")
    print("=" * 60)

    # テスト実行（フロー順）
    session_id = test_1_signup_success()
    test_2_signup_duplicate_email()
    new_session_id = test_3_login_success(session_id)
    test_4_login_invalid_credentials()
    test_5_get_me_with_auth(new_session_id)
    test_6_get_me_without_auth()
    test_7_create_article_with_auth(new_session_id)
    test_8_create_article_without_auth()
    test_9_logout_success(new_session_id)
    test_10_get_me_after_logout()

    # サマリー出力
    return print_summary()


if __name__ == "__main__":
    sys.exit(main())
