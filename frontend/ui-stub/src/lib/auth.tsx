import { createContext, useContext, useMemo, useState, type ReactNode } from "react"
import type { AuthContext as AuthState, User } from "@/types"

/**
 * 認証状態（データ）と、その状態を操作する関数をまとめた型定義
 */
export type AuthValue = AuthState & {
  login: (user: User) => void
  logout: () => void
}

/**
 * アプリケーション全体に認証状態を提供するプロバイダーコンポーネント
 * App.tsx で全体を包むように使用する
 */
const AuthContext = createContext<AuthValue | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [auth, setAuth] = useState<AuthState>({ isAuthenticated: false, user: null })

  const login = (user: User) => setAuth({ isAuthenticated: true, user })
  const logout = () => setAuth({ isAuthenticated: false, user: null })

  const value = useMemo(() => ({ ...auth, login, logout }), [auth])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * 各コンポーネントから認証情報にアクセスするためのカスタムフック
 * @returns {AuthValue} ログイン状態と操作関数
 * @throws {Error} AuthProvider の外側で使用された場合にエラーを投げる
 */
export const useAuth = (): AuthValue => {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error("AuthProvider is missing")
  }
  return ctx
}
