import type { Article, User } from '@/types';
import { mockArticles, mockUser, mockTags } from './mockData';

/**
 * ユーザー情報を取得
 * @returns Promise<User>
 */
export const getUser = async (): Promise<User> => {
  // 実APIの遅延を模擬
  await new Promise(resolve => setTimeout(resolve, 100));
  return mockUser;
};

/**
 * 記事一覧を取得する
 * - デフォルトは公開記事のみ
 * - publishedAt の新しい順にソート
 */
export const getArticles = async (options?: {
  includeUnpublished?: boolean;
}): Promise<Article[]> => {
  const { includeUnpublished = false } = options ?? {};

  // 実APIの遅延を模擬
  await new Promise(resolve => setTimeout(resolve, 150));

  // 公開状態でフィルタ
  const articles = includeUnpublished
    ? mockArticles
    : mockArticles.filter(article => article.isPublished);

  // 投稿日降順（新しい順）
  return articles
    .slice()
    .sort(
      (a, b) =>
        new Date(b.publishedAt).getTime() -
        new Date(a.publishedAt).getTime()
    );
};

/**
 * 記事IDで単一記事を取得する
 * - publicId で検索
 * - 見つからなければ null
 */
export const getArticleById = async (publicId: string): Promise<Article | null> => {
  // 実APIの遅延を模擬
  await new Promise(resolve => setTimeout(resolve, 100));

  const article = mockArticles.find(article => article.publicId === publicId);
  return article ?? null;
};

/**
 * タグ名から記事を取得する（複数件）
 */
export const getArticlesByTag = async (tagName: string): Promise<Article[]> => {
  // 実APIの遅延を模擬
  await new Promise(resolve => setTimeout(resolve, 150));

  return mockArticles.filter(article =>
    article.tags.some(tag => tag.name === tagName)
  );
};

/**
 * すべてのタグを取得
 */
export const getTags = async () => {
  // 実APIの遅延を模擬
  await new Promise(resolve => setTimeout(resolve, 100));

  return mockTags;
};

/**
 * タグIDからタグを取得
 */
export const getTagById = async (publicId: string) => {
  // 実APIの遅延を模擬
  await new Promise(resolve => setTimeout(resolve, 100));

  return mockTags.find(tag => tag.publicId === publicId) ?? null;
};

/**
 * 記事を削除する（スタブ）
 * - 永続化は行わず、ログ出力のみ
 */
export const deleteArticle = async (publicId: string): Promise<void> => {
  await new Promise(resolve => setTimeout(resolve, 200));
  console.log('Delete (stub):', publicId);
};

/**
 * 記事を保存する（新規作成・更新）
 * - 実APIを想定して Promise を返却
 * - 現在は mockArticles を変更せず、ログ出力のみ
 */
export const saveArticle = async (article: Article): Promise<Article> => {
  // 実APIの遅延を模擬
  await new Promise(resolve => setTimeout(resolve, 500));

  // TODO: スタブなのでデータは永続化しない。必要ならここで配列を更新
  // 例: 既存更新 or 追加（publicId で判定）
  // 今回は画面遷移確認用のためログ出力のみに留める
  console.log('Saved (stub):', article);
  return article;
};

/**
 * ログイン（認証）APIスタブ
 * - メール・パスワードで認証し、ユーザー情報を返却
 * - 現在はmockUserを固定で返却（認証チェックなし）
 */
export const loginUser = async (email: string, password: string): Promise<User> => {
  await new Promise(resolve => setTimeout(resolve, 200));

  // TODO: 実装時はバックエンドで認証し、トークン発行
  console.log('Login (stub):', { email, password });
  return mockUser;
};

/**
 * ログアウトAPIスタブ
 * - サーバー側でセッション/トークンを無効化する想定
 * - 現在は遅延のみでログ出力
 */
export const logoutUser = async (): Promise<void> => {
  await new Promise(resolve => setTimeout(resolve, 100));
  console.log('Logout (stub)');
};

/**
 * 新規ユーザーを登録する（スタブ）
 * - 入力値を元にユーザーを作成して返却するだけで、永続化はしない
 */
export const registerUser = async (params: {
  displayName: string;
  email: string;
  password: string;
}): Promise<User> => {
  await new Promise(resolve => setTimeout(resolve, 300));

  const now = new Date().toISOString();
  return {
    publicId: `uuid-user-${Date.now()}`,
    displayName: params.displayName || '新規ユーザー',
    email: params.email || 'newuser@example.com',
    createdAt: now,
    updatedAt: now,
  };
};
