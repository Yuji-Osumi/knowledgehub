/** 共通メタデータ */
export type BaseResource = {
  publicId: string;
  createdAt: string;  // ISO8601: "2025-01-01T00:00:00Z"
  updatedAt: string;
};

/** ユーザー型 */
export type User = BaseResource & {
  email: string;
  displayName: string;
};

/** タグ型 */
export type Tag = BaseResource & {
  name: string;
};

/** 記事型 */
export type Article = BaseResource & {
  title: string;
  content: string;          // Markdown形式
  tags: Tag[];              // 多対多関係を展開済み配列で保持
  isPublished: boolean;
  publishedAt: string;
  folderId: number | null;
};

/** フォルダ型 */
export type Folder = BaseResource & {
  name: string;
  parentId: number | null;
};

/** 認証コンテキスト用 */
export type AuthContext = {
  isAuthenticated: boolean;
  user: User | null;
};
