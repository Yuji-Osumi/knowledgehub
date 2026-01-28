"""
Article API テストスクリプト

各ステータスコード（201・422・404・500）の挙動を検証
テスト後は自動的にテストデータをクリーンアップ
"""

import subprocess
import sys
from typing import Any

import requests

# テスト対象のAPI ベースURL
API_BASE_URL = "http://localhost:8000/api"

# テスト結果を格納
test_results: list[dict[str, Any]] = []


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


def test_201_create_article() -> None:
    """201: 正常な記事作成"""
    print("\n[1/4] Testing 201 Created...")
    try:
        payload = {
            "title": "TEST_201_normal_case",
            "content": "This is a test article",
            "folder_id": None,
        }
        response = requests.post(f"{API_BASE_URL}/articles", json=payload, timeout=5)
        passed = response.status_code == 201
        log_test("201 Created", 201, response.status_code, passed)
        if passed:
            print(f"  Response: {response.json()}")
    except Exception as e:
        log_test("201 Created", 201, 0, False)
        print(f"  Error: {e}")


def test_422_validation_error() -> None:
    """422: バリデーションエラー（必須フィールド省略）"""
    print("\n[2/4] Testing 422 Validation Error...")
    try:
        # title を省略してバリデーションエラーを発生させる
        payload = {
            "content": "This is a test article",
            "folder_id": None,
        }
        response = requests.post(f"{API_BASE_URL}/articles", json=payload, timeout=5)
        passed = response.status_code == 422
        log_test("422 Validation Error", 422, response.status_code, passed)
        if response.status_code == 422:
            print(f"  Response: {response.json()}")
    except Exception as e:
        log_test("422 Validation Error", 422, 0, False)
        print(f"  Error: {e}")


def test_404_not_found() -> None:
    """404: 存在しないリソース"""
    print("\n[3/4] Testing 404 Not Found...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/articles/00000000-0000-0000-0000-000000000000",
            timeout=5,
        )
        passed = response.status_code == 404
        log_test("404 Not Found", 404, response.status_code, passed)
        if response.status_code == 404:
            print(f"  Response: {response.json()}")
    except Exception as e:
        log_test("404 Not Found", 404, 0, False)
        print(f"  Error: {e}")


def test_500_server_error() -> None:
    """500: サーバーエラー"""
    print("\n[4/4] Testing 500 Server Error...")
    try:
        response = requests.get(f"{API_BASE_URL}/error-test-500", timeout=5)
        passed = response.status_code == 500
        log_test("500 Server Error", 500, response.status_code, passed)
        if response.status_code == 500:
            # 500エラーはJSONではなくスタックトレースの可能性があるため、textで表示
            print(f"  Response (first 200 chars): {response.text[:200]}")
    except Exception as e:
        log_test("500 Server Error", 500, 0, False)
        print(f"  Error: {e}")


def cleanup_test_data() -> None:
    """テスト後にテストデータをクリーンアップ"""
    print("\n[Cleanup] Removing test data...")
    try:
        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "db",
                "psql",
                "-U",
                "admin_user",
                "-d",
                "knowledgehub_db",
                "-c",
                "DELETE FROM articles WHERE title LIKE 'TEST_%';",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✓ Test data cleaned up")
        else:
            print(f"✗ Cleanup failed: {result.stderr}")
    except Exception as e:
        print(f"✗ Cleanup error: {e}")


def print_summary() -> None:
    """テスト結果サマリー出力"""
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    total = len(test_results)
    passed = sum(1 for result in test_results if result["passed"])
    failed = total - passed

    for result in test_results:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"  [{status}] {result['name']}: Expected {result['expected']}, Got {result['actual']}"
        )

    print(f"\nTotal: {total}, Passed: {passed}, Failed: {failed}")
    print("=" * 50)

    # 失敗がある場合は終了コード 1
    if failed > 0:
        sys.exit(1)


def main() -> None:
    """メインテスト実行"""
    print("Starting Article API Test Suite...")
    print(f"API Base URL: {API_BASE_URL}")

    try:
        # 各テスト実行
        test_201_create_article()
        test_422_validation_error()
        test_404_not_found()
        test_500_server_error()

    finally:
        # テスト完了後にクリーンアップ（失敗した場合も実行）
        cleanup_test_data()

    # 最終結果表示
    print_summary()


if __name__ == "__main__":
    main()
