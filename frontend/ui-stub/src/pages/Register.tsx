import { useEffect, useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "@/lib/auth"
import { registerUser } from "@/lib/api"

export default function Register() {
  const [displayName, setDisplayName] = useState("")
  const [email, setEmail] = useState("")
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
      // スタブAPI呼び出し（永続化なし）
      const newUser = await registerUser({
        displayName,
        email,
        password,
      })
      login(newUser)
      navigate("/articles")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold">ユーザー登録</h1>
        <p className="text-sm text-gray-600">ユーザー名・メール・パスワードを入力してください。</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium">ユーザー名</label>
          <input
            className="w-full rounded border border-gray-300 px-3 py-2"
            value={displayName}
            onChange={e => setDisplayName(e.target.value)}
            placeholder="山田 太郎"
            disabled={loading}
          />
        </div>

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
          登録してログイン
        </button>
      </form>

      <div className="text-sm text-blue-700">
        <button
          type="button"
          className="underline"
          onClick={() => navigate("/login")}
          disabled={loading}
        >
          ログイン画面に戻る
        </button>
      </div>

      {loading && <div className="p-4 border border-gray-300 text-sm">読み込み中...</div>}
    </div>
  )
}
