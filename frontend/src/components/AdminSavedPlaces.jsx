
import { useCallback, useEffect, useState } from 'react'
import {
  Bookmark, RefreshCw, MapPin, Users,
  ChevronLeft, ChevronRight, AlertCircle
} from 'lucide-react'

const API_BASE = (
  import.meta.env.VITE_API_URL ||
  'https://novatrip-api-r3sc.onrender.com'
).replace(/\/$/, '')

export default function AdminSavedPlaces({ getAccessToken }) {
  const [places, setPlaces] = useState([])
  const [totalPlaces, setTotalPlaces] = useState(0)
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const limit = 10

  const loadPlaces = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const token = await getAccessToken()

      const response = await fetch(
        `${API_BASE}/api/admin/saved-places?limit=${limit}&offset=${offset}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load saved places.'
        )
      }

      setPlaces(data.places || [])
      setTotalPlaces(data.total || 0)

    } catch (err) {
      console.error('Admin saved places error:', err)
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }, [getAccessToken, offset])

  useEffect(() => {
    loadPlaces()
  }, [loadPlaces])

  const formatDate = (date) =>
    date
      ? new Date(date).toLocaleString()
      : 'Not available'

  return (
    <section className="space-y-7">

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-violet-400">
            ADMINISTRATION
          </p>
          <h1 className="mt-1 text-2xl font-bold">
            Saved Places Overview
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            See which users have saved destinations on NovaTrip.
          </p>
        </div>

        <button
          onClick={loadPlaces}
          disabled={loading}
          className="flex items-center gap-2 rounded-xl bg-violet-600 px-5 py-3 text-sm font-semibold hover:bg-violet-500 disabled:opacity-50"
        >
          <RefreshCw
            size={16}
            className={loading ? 'animate-spin' : ''}
          />
          Refresh places
        </button>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-[#121b30] p-5">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">
              Total saved places
            </p>
            <Bookmark className="text-violet-400" size={22} />
          </div>

          <h2 className="mt-4 text-3xl font-bold">
            {totalPlaces}
          </h2>
        </div>

        <div className="rounded-2xl border border-white/10 bg-[#121b30] p-5">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">
              Records on this page
            </p>
            <Users className="text-blue-400" size={22} />
          </div>

          <h2 className="mt-4 text-3xl font-bold">
            {places.length}
          </h2>
        </div>
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
            <h3 className="font-semibold">Saved Destination Records</h3>
            <p className="mt-1 text-xs text-slate-400">
              User and destination details from PostgreSQL
            </p>
          </div>

          <MapPin className="text-violet-400" size={22} />
        </div>

        {loading ? (
          <div className="py-14 text-center text-slate-400">
            Loading saved places...
          </div>
        ) : places.length === 0 ? (
          <div className="py-14 text-center text-slate-400">
            No saved places found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">

              <thead className="bg-white/5 text-xs text-slate-400">
                <tr>
                  <th className="p-4">Destination</th>
                  <th className="p-4">Saved by</th>
                  <th className="p-4">Email</th>
                  <th className="p-4">Tag</th>
                  <th className="p-4">Date saved</th>
                </tr>
              </thead>

              <tbody>
                {places.map(place => (
                  <tr
                    key={place.id}
                    className="border-t border-white/5 hover:bg-white/[0.02]"
                  >
                    <td className="p-4">
                      <div className="flex min-w-48 items-center gap-3">
                        <div className="h-12 w-14 shrink-0 overflow-hidden rounded-lg bg-violet-600/20">
                          {place.image_url ? (
                            <img
                              src={place.image_url}
                              alt={place.place_name}
                              className="h-full w-full object-cover"
                              loading="lazy"
                            />
                          ) : (
                            <div className="flex h-full items-center justify-center">
                              <MapPin size={20} className="text-violet-300" />
                            </div>
                          )}
                        </div>

                        <div>
                          <p className="font-semibold text-white">
                            {place.place_name}
                          </p>
                          <p className="text-xs text-slate-400">
                            {place.country}
                          </p>
                        </div>
                      </div>
                    </td>

                    <td className="whitespace-nowrap p-4 font-medium text-slate-200">
                      @{place.username || 'Unknown'}
                    </td>

                    <td className="whitespace-nowrap p-4 text-slate-300">
                      {place.email || 'Not available'}
                    </td>

                    <td className="p-4">
                      <span className="rounded-full bg-violet-500/10 px-3 py-1 text-xs text-violet-300">
                        {place.tag || 'General'}
                      </span>
                    </td>

                    <td className="whitespace-nowrap p-4 text-xs text-slate-400">
                      {formatDate(place.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        )}

        <div className="flex items-center justify-between border-t border-white/10 p-4">
          <p className="text-xs text-slate-400">
            {totalPlaces === 0
              ? 'No saved places'
              : `Showing ${offset + 1}–${offset + places.length} of ${totalPlaces}`}
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
              disabled={offset + limit >= totalPlaces || loading}
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
