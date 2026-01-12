import { useEffect, useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { getUser } from "@/lib/api"
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
      const user = await getUser()
      login(user)
      navigate("/articles")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold">Login</h1>
        <p className="text-sm text-gray-600">ダミーログインで一覧へ遷移します。</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium">Email</label>
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
          <label className="block text-sm font-medium">Password</label>
          <input
            className="w-full rounded border border-gray-300 px-3 py-2"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="dummy password"
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

      {loading && <div className="p-4 border border-gray-300 text-sm">読み込み中...</div>}
    </div>
  )
}
