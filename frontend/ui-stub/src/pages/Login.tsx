import { useEffect, useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { loginUser } from "@/lib/api"
import { useAuth } from "@/lib/auth"

export default function Login() {
  const [email, setEmail] = useState("user@example.com")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const { isAuthenticated, login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/articles", { replace: true })
    }
  }, [isAuthenticated, navigate])

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    try {
      const user = await loginUser(email, password) // API経由でログイン認証
      login(user)                                    // AuthContextの状態を更新
      navigate("/articles")                          // 成功したら一覧ページへ
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold">ログイン</h1>
        <p className="text-sm text-gray-600">ダミーログインで一覧へ遷移します。</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium">メールアドレス</label>
          <input
            className="w-full rounded border border-gray-300 px-3 py-2"
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="user@example.com"
            disabled={loading}
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">パスワード</label>
          <input
            className="w-full rounded border border-gray-300 px-3 py-2"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="8文字以上を推奨"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          className="w-full rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-60"
          disabled={loading}
        >
          ログイン
        </button>
      </form>

      <div className="text-sm text-blue-700">
        <button
          type="button"
          className="underline"
          onClick={() => navigate("/register")}
          disabled={loading}
        >
          新規ユーザー登録はこちら
        </button>
      </div>

      {loading && <div className="p-4 border border-gray-300 text-sm">読み込み中...</div>}
    </div>
  )
}
