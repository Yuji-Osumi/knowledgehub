.PHONY: help \
				up up-log down restart logs ps build \
        backend db psql migrate revision \
				health1 health2 health3 health4 health5 health-all\
				lint\
				test-auth test-articles test-all \
				test-unit-host test-unit-host-verbose test-unit-container test-integration-container\
				front front-install front-build

HOST_PYTHON := ../.venv/bin/python

# =========================
# 基本操作
# =========================

help:
	@echo "=====================Usage=====================:"
	@echo "docker:"
	@echo "  make up        - コンテナ起動"
	@echo "  make up-log    - コンテナ起動（ログあり）"
	@echo "  make down      - コンテナ停止"
	@echo "  make restart   - 再起動"
	@echo "  make ps        - 起動状態確認"
	@echo "  make logs      - ログ表示"
	@echo ""
	@echo "DB / Migration:"
	@echo "  make psql             - DB(psql)接続"
	@echo "  make migrate          - alembic upgrade head"
	@echo "  make revision msg=\"\"  - alembic revision (手動)"
	@echo ""
	@echo "health check:"
	@echo "  health-all     - API一括チェック"
	@echo "  article-api-test  - Article API テスト（201・422・404・500）"
	@echo ""
	@echo "テスト:"
	@echo "  test-auth        - 認証 API テスト (スクリプト)"
	@echo "  test-articles    - 記事 API テスト (スクリプト)"
	@echo "  test-all         - 全テスト実行 (スクリプト)"
	@echo "  test-unit-host         - pytest 単体テスト実行 (host)"
	@echo "  test-unit-host-verbose - pytest 単体テスト実行 (host, 詳細)"
	@echo "  test-unit-container    - pytest 単体テスト実行 (Docker backend内)"
	@echo "  test-integration-container - pytest 統合テスト実行 (Docker backend内)"
	@echo ""
	@echo "静的解析 (Linter):"
	@echo "  lint           - ruff checkとmypyを実施"
	@echo ""
	@echo "frontend起動:"
	@echo "  front              - dev環境を起動"
	@echo "  front-install      - 初回やパッケージ追加時に使用"
	@echo "  front-build        - ビルド用"
	@echo ""

# =========================
# Docker Compose 操作
# =========================

up:
	docker compose up -d

# ログを画面に出しながら起動
up-log:
	docker compose up

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d

build:
	docker compose up -d --build

ps:
	docker compose ps

logs:
	docker compose logs -f

# =========================
# DB / Alembic
# =========================

backend:
	docker compose exec backend bash

db:
	docker compose exec db bash

# 直接SQLを操作できる状態にする \dtでテーブルを確認　docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB>
psql:
	docker compose exec db psql -U admin_user -d knowledgehub_db

# データベースの構成を最新化
migrate:
	docker compose exec backend alembic upgrade head

# マイグレーションファイルを作成 例）make revision msg="add user table"
revision:
ifndef msg
	$(error 引数 msg が指定されていません。 例: make revision msg="add_user_table")
endif
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

# =========================
# ヘルスチェック
# =========================

# すべてのヘルスチェックを順番に実行
health-all: health1 health2 health3 health4 health5

health1:
	@echo "--- [1/5] Basic Health Check ---"
	curl -s http://localhost:8000/api/health
	@echo ""

health2:
	@echo "--- [2/5] Client Error Test (404) ---"
	curl -s -w "\nStatus Code: %{http_code}\n" http://localhost:8000/api/error-test 2>/dev/null || true
	@echo ""

health3:
	@echo "--- [3/5] Server Error Test (500) ---"
	curl -s -w "\nStatus Code: %{http_code}\n" http://localhost:8000/api/error-test-500 2>/dev/null || true
	@echo ""

health4:
	@echo "--- [4/5] Database Connection Check ---"
	curl -s http://localhost:8000/api/db-check
	@echo ""

health5:
	@echo "--- [5/5] Authentication Endpoint Check ---"
	curl -s http://localhost:8000/api/auth/me
	@echo ""

# =========================
# テスト
# =========================

# 認証 API テスト
test-auth:
	@echo "--- Running Auth API Tests ---"
	python backend/scripts/test_auth_api.py

# 記事 API テスト
test-articles:
	@echo "--- Running Article API Tests ---"
	python backend/scripts/test_articles_api.py

# 全テスト実行
test-all: test-auth test-articles
	@echo "✅ All tests passed!"

# pytest 単体テスト実行（host）
test-unit-host:
	@echo "--- Running pytest Unit Tests (host) ---"
	cd backend && $(HOST_PYTHON) -m pytest tests/ -v --ignore=tests/test_integration.py

# pytest 単体テスト実行（host, 詳細版・短いトレースバック）
test-unit-host-verbose:
	@echo "--- Running pytest Unit Tests (host verbose) ---"
	cd backend && $(HOST_PYTHON) -m pytest tests/ -v --tb=short --ignore=tests/test_integration.py

# pytest 単体テスト実行（Docker backend内）
test-unit-container:
	@echo "--- Running pytest Unit Tests in backend container ---"
	docker compose exec backend sh -c "python -m pytest tests/ -v --ignore=tests/test_integration.py"

# pytest 統合テスト実行（Docker backend内）
test-integration-container:
	@echo "--- Running pytest Integration Tests (container) ---"
	docker compose exec backend sh -c "python -m pytest tests/test_integration.py --integration -v"

# =========================
# 静的解析 (Linter)
# =========================

# 静的解析・文法チェックと静的型チェックを実施
lint:
	@echo "--- [1/2] Ruff Check ---"
	ruff check backend/app
	@echo "--- [2/2] mypy Check ---"
	mypy backend/app --config-file backend/pyproject.toml

# =========================
# フロントエンド関連
# =========================

# dev環境を起動
front:
	cd frontend/ui-stub && npm run dev

# 初回やパッケージ追加時に使用
front-install:
	cd frontend/ui-stub && npm install

# ビルド用
front-build:
	cd frontend/ui-stub && npm run build
