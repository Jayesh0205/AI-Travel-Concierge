
import { useCallback, useEffect, useState } from 'react'
import {
  Users, RefreshCw, ShieldCheck, UserRound,
  ChevronLeft, ChevronRight, AlertCircle, Bookmark,
  Activity
} from 'lucide-react'

const API_BASE = (
  import.meta.env.VITE_API_URL ||
  'https://novatrip-api-r3sc.onrender.com'
).replace(/\/$/, '')

export default function AdminUsers({ getAccessToken }) {
  const [users, setUsers] = useState([])
  const [totalUsers, setTotalUsers] = useState(0)
  const [totalSavedPlaces, setTotalSavedPlaces] = useState(null)
  const [totalRequests, setTotalRequests] = useState(null)
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const limit = 10

  const loadUsers = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const token = await getAccessToken()

      const headers = {
        Authorization: `Bearer ${token}`,
      }

      const [usersResponse, placesResponse, monitoringResponse] =
        await Promise.all([
          fetch(
            `${API_BASE}/api/admin/users?limit=${limit}&offset=${offset}`,
            { headers }
          ),
          fetch(
            `${API_BASE}/api/admin/saved-places?limit=1&offset=0`,
            { headers }
          ),
          fetch(
            `${API_BASE}/api/monitoring/overview`,
            { headers }
          ),
        ])

      const data = await usersResponse.json()

      if (!usersResponse.ok) {
        throw new Error(
          data.detail || 'Unable to load registered users.'
        )
      }

      setUsers(data.users || [])
      setTotalUsers(data.total_users || 0)

      if (placesResponse.ok) {
        const placesData = await placesResponse.json()
        setTotalSavedPlaces(
          placesData.total ??
          placesData.total_places ??
          null
        )
      } else {
        setTotalSavedPlaces(null)
      }

      if (monitoringResponse.ok) {
        const monitoringData = await monitoringResponse.json()
        setTotalRequests(monitoringData.total_requests ?? null)
      } else {
        setTotalRequests(null)
      }

    } catch (err) {
      console.error('Admin dashboard error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [getAccessToken, offset])

  useEffect(() => {
    loadUsers()
  }, [loadUsers])

  const formatDate = (date) =>
    date
      ? new Date(date).toLocaleString()
      : 'Not available'

  const adminCount = users.filter(
    user => user.role === 'admin'
  ).length

  const regularUserCount = users.filter(
    user => user.role !== 'admin'
  ).length

  const statistics = [
    {
      title: 'Total Registered Users',
      value: totalUsers,
      icon: Users,
      color: 'text-violet-400',
      background: 'bg-violet-500/10',
    },
    {
      title: 'Total Saved Places',
      value: totalSavedPlaces ?? '—',
      icon: Bookmark,
      color: 'text-pink-400',
      background: 'bg-pink-500/10',
    },
    {
      title: 'Total API Requests',
      value: totalRequests ?? '—',
      icon: Activity,
      color: 'text-cyan-400',
      background: 'bg-cyan-500/10',
    },
    {
      title: 'Admins on This Page',
      value: adminCount,
      icon: ShieldCheck,
      color: 'text-blue-400',
      background: 'bg-blue-500/10',
    },
    {
      title: 'Users on This Page',
      value: regularUserCount,
      icon: UserRound,
      color: 'text-emerald-400',
      background: 'bg-emerald-500/10',
    },
  ]

  return (
    <section className="space-y-7">

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-violet-400">
            ADMINISTRATION
          </p>
          <h1 className="mt-1 text-2xl font-bold">
            Admin Dashboard
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Manage users and monitor NovaTrip platform activity.
          </p>
        </div>

        <button
          onClick={loadUsers}
          disabled={loading}
          className="flex items-center gap-2 rounded-xl bg-violet-600 px-5 py-3 text-sm font-semibold hover:bg-violet-500 disabled:opacity-50"
        >
          <RefreshCw
            size={16}
            className={loading ? 'animate-spin' : ''}
          />
          Refresh dashboard
        </button>
      </div>

      {/* Dashboard Statistics */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {statistics.map((stat) => {
          const Icon = stat.icon

          return (
            <div
              key={stat.title}
              className="rounded-2xl border border-white/10 bg-[#121b30] p-5 transition hover:border-violet-500/30"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm text-slate-400">
                  {stat.title}
                </p>

                <div className={`rounded-xl p-2 ${stat.background}`}>
                  <Icon size={21} className={stat.color} />
                </div>
              </div>

              <h2 className="mt-4 text-3xl font-bold">
                {loading ? (
                  <span className="inline-block h-8 w-12 animate-pulse rounded bg-white/10" />
                ) : (
                  stat.value
                )}
              </h2>
            </div>
          )
        })}
      </div>

      {error && (
        <div className="flex items-center gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          <AlertCircle size={19} />
          {error}
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#121b30]">

        <div className="flex items-center justify-between border-b border-white/10 p-5">
          <div>
            <h3 className="font-semibold">Registered Accounts</h3>
            <p className="mt-1 text-xs text-slate-400">
              Account details from PostgreSQL
            </p>
          </div>
          <ShieldCheck className="text-violet-400" size={22} />
        </div>

        {loading ? (
          <div className="py-14 text-center text-slate-400">
            Loading registered users...
          </div>
        ) : users.length === 0 ? (
          <div className="py-14 text-center text-slate-400">
            No registered users found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">

              <thead className="bg-white/5 text-xs text-slate-400">
                <tr>
                  <th className="p-4">User</th>
                  <th className="p-4">Email</th>
                  <th className="p-4">Role</th>
                  <th className="p-4">Registered</th>
                </tr>
              </thead>

              <tbody>
                {users.map(user => (
                  <tr
                    key={user.id}
                    className="border-t border-white/5 hover:bg-white/[0.02]"
                  >
                    <td className="p-4">
                      <div className="flex min-w-48 items-center gap-3">
                        <div className="h-10 w-10 shrink-0 overflow-hidden rounded-full bg-violet-600/20">
                          {user.avatar_url ? (
                            <img
                              src={user.avatar_url}
                              alt=""
                              className="h-full w-full object-cover"
                            />
                          ) : (
                            <div className="flex items-center justify-center font-bold text-violet-300">
                              {(user.full_name || user.username || '?')
                                .charAt(0).toUpperCase()}
                            </div>
                          )}
                        </div>

                        <div className="min-w-0">
                          <p className="truncate font-semibold text-white">
                            {user.full_name || user.username}
                          </p>
                          <p className="text-xs text-slate-500">
                            @{user.username}
                          </p>
                        </div>
                      </div>
                    </td>

                    <td className="whitespace-nowrap p-4 text-slate-300">
                      {user.email}
                    </td>

                    <td className="p-4">
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        user.role === 'admin'
                          ? 'bg-violet-500/10 text-violet-300'
                          : 'bg-emerald-500/10 text-emerald-300'
                      }`}>
                        {user.role === 'admin' ? 'Admin' : 'User'}
                      </span>
                    </td>

                    <td className="whitespace-nowrap p-4 text-xs text-slate-400">
                      {formatDate(user.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        )}

        <div className="flex items-center justify-between border-t border-white/10 p-4">
          <p className="text-xs text-slate-400">
            {totalUsers === 0
              ? 'No users'
              : `Showing ${offset + 1}–${offset + users.length} of ${totalUsers}`}
          </p>

          <div className="flex gap-2">
            <button
              onClick={() => setOffset(value => Math.max(0, value - limit))}
              disabled={offset === 0 || loading}
              className="rounded-lg border border-white/10 p-2 hover:bg-white/5 disabled:opacity-30"
            >
              <ChevronLeft size={18} />
            </button>

            <button
              onClick={() => setOffset(value => value + limit)}
              disabled={offset + limit >= totalUsers || loading}
              className="rounded-lg border border-white/10 p-2 hover:bg-white/5 disabled:opacity-30"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>

      </div>
    </section>
  )
}
