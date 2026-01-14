import type { User, Article, Tag } from '@/types';

/** ダミーユーザー */
export const mockUser: User = {
  publicId: 'uuid-user-001',
  email: 'you@example.com',
  displayName: 'テストユーザー',
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-10T00:00:00Z',
};

/** ダミータグ一覧 */
export const mockTags: Tag[] = [
  {
    publicId: 'uuid-tag-001',
    name: 'Python',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
  },
  {
    publicId: 'uuid-tag-002',
    name: 'FastAPI',
    createdAt: '2025-01-02T00:00:00Z',
    updatedAt: '2025-01-02T00:00:00Z',
  },
  {
    publicId: 'uuid-tag-003',
    name: 'React',
    createdAt: '2025-01-03T00:00:00Z',
    updatedAt: '2025-01-03T00:00:00Z',
  },
  {
    publicId: 'uuid-tag-004',
    name: 'TypeScript',
    createdAt: '2025-01-04T00:00:00Z',
    updatedAt: '2025-01-04T00:00:00Z',
  },
  {
    publicId: 'uuid-tag-005',
    name: 'Docker',
    createdAt: '2025-01-05T00:00:00Z',
    updatedAt: '2025-01-05T00:00:00Z',
  },
  {
    publicId: 'uuid-tag-006',
    name: 'PostgreSQL',
    createdAt: '2025-01-06T00:00:00Z',
    updatedAt: '2025-01-06T00:00:00Z',
  },
];

/** ダミー記事一覧 (10件) */
export const mockArticles: Article[] = [
  {
    publicId: 'uuid-article-001',
    title: 'FastAPI環境構築メモ',
    content: `# FastAPI環境構築

## セットアップ手順
1. Python 3.9以上をインストール
2. 仮想環境を作成
3. FastAPIとuvicornをインストール

\`\`\`bash
pip install fastapi uvicorn
\`\`\`

## 基本的なサーバー起動
\`\`\`bash
uvicorn main:app --reload
\`\`\``,
    tags: [mockTags[0], mockTags[1]], // Python, FastAPI
    isPublished: true,
    publishedAt: '2025-01-01T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-10T12:30:00Z',
  },
  {
    publicId: 'uuid-article-002',
    title: 'React Hooksまとめ',
    content: `# React Hooks完全ガイド

## useStateの使い方
状態管理の基本中の基本。

\`\`\`javascript
const [count, setCount] = useState(0);
\`\`\`

## useEffectでライフサイクル管理
副作用を管理するための重要なHook。`,
    tags: [mockTags[2], mockTags[3]], // React, TypeScript
    isPublished: true,
    publishedAt: '2025-01-05T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-05T00:00:00Z',
    updatedAt: '2025-01-08T15:45:00Z',
  },
  {
    publicId: 'uuid-article-003',
    title: 'Docker入門：コンテナの基礎',
    content: `# Docker完全ガイド

## Dockerとは
アプリケーションを隔離された環境で実行するためのツール。

## イメージとコンテナの違い
- **イメージ**: テンプレート
- **コンテナ**: 実行中のインスタンス

## よく使うコマンド
\`\`\`bash
docker build -t myapp .
docker run -p 8000:8000 myapp
\`\`\``,
    tags: [mockTags[4]], // Docker
    isPublished: true,
    publishedAt: '2025-01-07T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-07T00:00:00Z',
    updatedAt: '2025-01-11T10:00:00Z',
  },
  {
    publicId: 'uuid-article-004',
    title: 'TypeScript型安全性の重要性',
    content: `# TypeScriptで安全なコードを書く

## 型定義の基本
型チェックにより実行時エラーを削減。

\`\`\`typescript
interface User {
  id: number;
  name: string;
  email: string;
}
\`\`\`

## Genericsの活用
再利用可能で型安全なコンポーネント設計。`,
    tags: [mockTags[3]], // TypeScript
    isPublished: false,
    publishedAt: '2025-01-09T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-09T00:00:00Z',
    updatedAt: '2025-01-12T14:20:00Z',
  },
  {
    publicId: 'uuid-article-005',
    title: 'PostgreSQL全文検索の実装',
    content: `# PostgreSQLで全文検索を実装する

## tsvectorの活用
PostgreSQL標準の全文検索機能。

\`\`\`sql
CREATE INDEX idx_search_vector ON articles USING GIN(search_vector);
\`\`\`

## クエリの書き方
\`\`\`sql
SELECT * FROM articles
WHERE search_vector @@ plainto_tsquery('japanese', 'キーワード');
\`\`\``,
    tags: [mockTags[0], mockTags[5]], // Python, PostgreSQL
    isPublished: true,
    publishedAt: '2025-01-06T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-06T00:00:00Z',
    updatedAt: '2025-01-09T09:15:00Z',
  },
  {
    publicId: 'uuid-article-006',
    title: 'TailwindCSSで効率的なスタイリング',
    content: `# TailwindCSSの使い方

## ユーティリティファーストの考え方
CSSを最小限に抑え、HTMLで直接スタイル指定。

## よく使うクラス
- \`flex\`: Flexbox有効化
- \`grid\`: Grid有効化
- \`text-center\`: テキスト中央寄せ
- \`bg-blue-500\`: 背景色指定

## カスタマイズ方法
\`tailwind.config.js\`でテーマをカスタマイズ可能。`,
    tags: [mockTags[3]], // TypeScript
    isPublished: true,
    publishedAt: '2025-01-08T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-08T00:00:00Z',
    updatedAt: '2025-01-08T16:30:00Z',
  },
  {
    publicId: 'uuid-article-007',
    title: 'Viteでモダンなフロントエンド開発',
    content: `# Viteの魅力

## Viteとは
次世代フロントエンドビルドツール。

## 特徴
- 高速な開発サーバー起動
- 即座のホットモジュール置換（HMR）
- ネイティブES Modulesを活用

## セットアップ
\`\`\`bash
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
npm run dev
\`\`\``,
    tags: [mockTags[2], mockTags[3]], // React, TypeScript
    isPublished: true,
    publishedAt: '2025-01-03T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-03T00:00:00Z',
    updatedAt: '2025-01-11T08:20:00Z',
  },
  {
    publicId: 'uuid-article-008',
    title: 'Pythonデータ処理のベストプラクティス',
    content: `# Python データ処理ガイド

## PandasとNumPyの使い分け
データフレーム操作はPandas、数値計算はNumPyが得意。

## よく使うPandas機能
\`\`\`python
import pandas as pd

df = pd.read_csv('data.csv')
filtered = df[df['age'] > 20]
\`\`\`

## パフォーマンス最適化
大規模データセットではNumPyベースの処理を優先。`,
    tags: [mockTags[0]], // Python
    isPublished: true,
    publishedAt: '2025-01-04T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-04T00:00:00Z',
    updatedAt: '2025-01-09T11:30:00Z',
  },
  {
    publicId: 'uuid-article-009',
    title: 'Gitワークフロー：main/dev/featureブランチ',
    content: `# Gitワークフロー設計

## ブランチ戦略
- main：本番環境デプロイ用
- dev：開発環境統合用
- feature/xxx：個別開発ブランチ

## プルリクエストのベストプラクティス
1. featureから dev へ PR
2. コードレビュー実施
3. マージ後、テスト環境へデプロイ

## コミットメッセージ規約
\`\`\`
feat: 新機能
fix: バグ修正
docs: ドキュメント
refactor: リファクタリング
\`\`\``,
    tags: [], // タグなし
    isPublished: true,
    publishedAt: '2025-01-02T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-02T00:00:00Z',
    updatedAt: '2025-01-07T13:00:00Z',
  },
  {
    publicId: 'uuid-article-010',
    title: 'APIテスト戦略：pytest と requests',
    content: `# APIテストの書き方

## pytestの基本
\`\`\`python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_get_articles(client):
    response = client.get('/api/articles')
    assert response.status_code == 200
\`\`\`

## Mock の活用
外部APIに依存しないテストを実装。`,
    tags: [mockTags[0], mockTags[1]], // Python, FastAPI
    isPublished: true,
    publishedAt: '2025-01-09T00:00:00Z',
    folderId: null,
    createdAt: '2025-01-09T00:00:00Z',
    updatedAt: '2025-01-10T14:45:00Z',
  },
];
