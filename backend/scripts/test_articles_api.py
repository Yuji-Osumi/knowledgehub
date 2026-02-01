"""
Article API 統合テストスクリプト

以下のシナリオを検証：
1. ユーザー登録（セッション作成）
2. 認証付きで記事作成（201）
3. バリデーションエラー（400）
4. 認証なしでのアクセス（401）
5. 存在しないリソース取得（404）

テスト後は自動的にテストデータをクリーンアップ
"""

import subprocess
import sys
import uuid
from typing import Any

import requests

# テスト対象のAPI ベースURL
API_BASE_URL = "http://localhost:8000/api"

# テスト結果を格納
test_results: list[dict[str, Any]] = []

# テスト用の認証情報
UNIQUE_SUFFIX = str(uuid.uuid4())[:8]
TEST_USER = {
    "email": f"test_articles_{UNIQUE_SUFFIX}@example.com",
    "password": "TestPassword123",
    "display_name": "Test User Articles",
}

# セッション情報
session_cookies = {}


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


def signup_test_user() -> bool:
    """テスト用ユーザーを登録"""
    print("\n[Setup] Registering test user...")
    try:
        payload = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "password_confirm": TEST_USER["password"],
            "display_name": TEST_USER["display_name"],
        }
        response = requests.post(f"{API_BASE_URL}/auth/signup", json=payload, timeout=5)

        if response.status_code == 201:
            # セッションクッキーを保存
            global session_cookies
            session_cookies = response.cookies
            print(f"✓ Test user registered: {TEST_USER['email']}")
            return True
        else:
            print(f"✗ Signup failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Signup error: {e}")
        return False


def test_201_create_article() -> None:
    """201: 正常な記事作成（認証あり）"""
    print("\n[1/4] Testing 201 Created...")
    try:
        payload = {
            "title": f"TEST_201_normal_case_{UNIQUE_SUFFIX}",
            "content": "This is a test article",
            "folder_id": None,
        }
        response = requests.post(
            f"{API_BASE_URL}/articles",
            json=payload,
            cookies=session_cookies,
            timeout=5,
        )
        passed = response.status_code == 201
        log_test("201 Created", 201, response.status_code, passed)
        if passed:
            data = response.json()
            print(f"  Article ID: {data.get('public_id')}")
        elif response.status_code == 401:
            print(f"  Error: Authentication required")
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        log_test("201 Created", 201, 0, False)
        print(f"  Error: {e}")


def test_400_validation_error() -> None:
    """400: バリデーションエラー（必須フィールド省略）"""
    print("\n[2/4] Testing 400 Validation Error...")
    try:
        # title を省略してバリデーションエラーを発生させる
        payload = {
            "content": "This is a test article",
            "folder_id": None,
        }
        response = requests.post(
            f"{API_BASE_URL}/articles",
            json=payload,
            cookies=session_cookies,
            timeout=5,
        )
        passed = response.status_code == 400
        log_test("400 Validation Error", 400, response.status_code, passed)
        if response.status_code in (400, 422):
            error_data = response.json()
            print(f"  Error Code: {error_data.get('error', {}).get('code', 'N/A')}")
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        log_test("400 Validation Error", 400, 0, False)
        print(f"  Error: {e}")


def test_401_unauthorized() -> None:
    """401: 認証なしでのアクセス"""
    print("\n[3/4] Testing 401 Unauthorized...")
    try:
        payload = {
            "title": f"TEST_401_unauthorized_{UNIQUE_SUFFIX}",
            "content": "This is a test article",
            "folder_id": None,
        }
        # セッションクッキーなしで実行
        response = requests.post(
            f"{API_BASE_URL}/articles",
            json=payload,
            timeout=5,
        )
        passed = response.status_code == 401
        log_test("401 Unauthorized", 401, response.status_code, passed)
        if response.status_code == 401:
            error_data = response.json()
            print(f"  Error: {error_data.get('error', {}).get('message', 'N/A')}")
    except Exception as e:
        log_test("401 Unauthorized", 401, 0, False)
        print(f"  Error: {e}")


def test_404_not_found() -> None:
    """404: 存在しないリソース"""
    print("\n[4/4] Testing 404 Not Found...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/articles/00000000-0000-0000-0000-000000000000",
            cookies=session_cookies,
            timeout=5,
        )
        passed = response.status_code == 404
        log_test("404 Not Found", 404, response.status_code, passed)
        if response.status_code == 404:
            error_data = response.json()
            print(f"  Error Code: {error_data.get('error', {}).get('code', 'N/A')}")
    except Exception as e:
        log_test("404 Not Found", 404, 0, False)
        print(f"  Error: {e}")


def cleanup_test_data() -> None:
    """テスト後にテストデータをクリーンアップ"""
    print("\n[Cleanup] Removing test data...")
    try:
        import os

        try:
            import psycopg
        except ImportError:
            # psycopgがない場合はスキップ
            print("⚠ Cleanup skipped (psycopg not available)")
            return

        # DATABASE_URLから接続情報を取得
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://admin_user:password@localhost:5432/knowledgehub_db",
        )
        # postgresql+psycopg:// をpsycopg用に変換
        db_url = db_url.replace("postgresql+psycopg://", "")

        try:
            # psycopg経由で直接接続
            conn = psycopg.connect(db_url)
            cur = conn.cursor()
            cur.execute(f"DELETE FROM articles WHERE title LIKE 'TEST_{UNIQUE_SUFFIX}%';")
            conn.commit()
            cur.close()
            conn.close()
            print("✓ Test articles cleaned up")
        except Exception as db_error:
            # 接続失敗時はスキップ
            print(f"⚠ Cleanup skipped (non-critical): {type(db_error).__name__}")
    except Exception as e:
        print(f"⚠ Cleanup skipped (non-critical): {e}")


def print_summary() -> None:
    """テスト結果サマリー出力"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total = len(test_results)
    passed = sum(1 for result in test_results if result["passed"])
    failed = total - passed

    for result in test_results:
        status = "✓" if result["passed"] else "✗"
        print(f"{status} {result['name']}: {result['expected']} (Got {result['actual']})")

    print("-" * 60)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print("-" * 60)

    # 失敗がある場合は終了コード 1
    if failed > 0:
        print("\n❌ Some tests failed")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")


def main() -> None:
    """メインテスト実行"""
    print("=" * 60)
    print("Article API Integration Test Suite")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print("=" * 60)

    # テスト用ユーザーを登録
    if not signup_test_user():
        print("\n❌ Failed to setup test user. Aborting tests.")
        sys.exit(1)

    try:
        # 各テスト実行
        test_201_create_article()
        test_400_validation_error()
        test_401_unauthorized()
        test_404_not_found()

    finally:
        # テスト完了後にクリーンアップ（失敗した場合も実行）
        cleanup_test_data()

    # 最終結果表示
    print_summary()


if __name__ == "__main__":
    main()
