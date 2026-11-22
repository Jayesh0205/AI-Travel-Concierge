
import { useCallback, useEffect, useState } from 'react'
import {
  Heart, RefreshCw, MapPin, Trash2, AlertCircle,
  Globe2, Image as ImageIcon, Compass, BookmarkPlus
} from 'lucide-react'

const API_BASE = (
  import.meta.env.VITE_API_URL ||
  'https://novatrip-api-r3sc.onrender.com'
).replace(/\/$/, '')

function PlaceSkeleton() {
  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-[#0c1528]">
      <div className="h-40 animate-pulse bg-white/10" />
      <div className="space-y-3 p-4">
        <div className="h-5 w-2/3 animate-pulse rounded bg-white/10" />
        <div className="h-4 w-1/2 animate-pulse rounded bg-white/10" />
        <div className="h-9 animate-pulse rounded-lg bg-white/10" />
      </div>
    </div>
  )
}

export default function SavedPlaces({ getAccessToken }) {
  const [places, setPlaces] = useState([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [failedImages, setFailedImages] = useState([])

  const loadPlaces = useCallback(async () => {
    setLoading(true)
    setError('')
    setMessage('')

    try {
      const token = await getAccessToken()

      const response = await fetch(
        `${API_BASE}/api/saved-places`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to load saved places.')
      }

      setPlaces(data.places || [])
      setFailedImages([])
    } catch (err) {
      console.error('Saved places error:', err)
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [getAccessToken])

  useEffect(() => {
    loadPlaces()
  }, [loadPlaces])

  const removePlace = async (placeId) => {
    const confirmed = window.confirm(
      'Remove this place from your saved places?'
    )

    if (!confirmed) return

    setDeletingId(placeId)
    setError('')
    setMessage('')

    try {
      const token = await getAccessToken()

      const response = await fetch(
        `${API_BASE}/api/saved-places/${placeId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to remove place.')
      }

      setPlaces(current =>
        current.filter(place => place.id !== placeId)
      )

      setMessage('Place removed successfully.')
    } catch (err) {
      console.error('Remove saved place error:', err)
      setError(err.message || 'Unable to remove place.')
    } finally {
      setDeletingId(null)
    }
  }

  const countriesCount = new Set(
    places.map(place => place.country)
  ).size

  return (
    <section className="space-y-7">

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-violet-400">
            YOUR COLLECTION
          </p>

          <h1 className="mt-1 text-2xl font-bold">
            Saved Places
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Keep your favourite destinations together.
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
            <Heart className="text-pink-400" size={22} />
          </div>

          <h2 className="mt-4 text-3xl font-bold">
            {loading ? '—' : places.length}
          </h2>
        </div>

        <div className="rounded-2xl border border-white/10 bg-[#121b30] p-5">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">
              Countries explored
            </p>
            <Globe2 className="text-blue-400" size={22} />
          </div>

          <h2 className="mt-4 text-3xl font-bold">
            {loading ? '—' : countriesCount}
          </h2>
        </div>
      </div>

      {error && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          <div className="flex items-center gap-3">
            <AlertCircle size={19} />
            {error}
          </div>

          <button
            onClick={loadPlaces}
            disabled={loading}
            className="rounded-lg bg-red-500/20 px-4 py-2 font-semibold hover:bg-red-500/30 disabled:opacity-50"
          >
            Try again
          </button>
        </div>
      )}

      {message && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300">
          {message}
        </div>
      )}

      <div className="rounded-2xl border border-white/10 bg-[#121b30] p-5">

        <div className="mb-5 flex items-center justify-between">
          <div>
            <h3 className="font-semibold">Your Destinations</h3>
            <p className="mt-1 text-xs text-slate-400">
              Saved securely to your account
            </p>
          </div>

          <Heart className="text-pink-400" size={22} />
        </div>

        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <PlaceSkeleton key={index} />
            ))}
          </div>
        ) : error ? (
          <div className="py-8 text-center text-slate-400">
            <AlertCircle size={34} className="mx-auto text-red-400" />
            <p className="mt-3">
              Your saved places could not be loaded.
            </p>
            <p className="mt-1 text-xs">
              Use Try again above to reload your collection.
            </p>
          </div>
        ) : places.length === 0 ? (
          <div className="rounded-xl border border-dashed border-white/10 bg-white/[0.02] px-5 py-12 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-pink-500/10">
              <BookmarkPlus size={32} className="text-pink-400" />
            </div>

            <h3 className="mt-5 text-lg font-semibold text-white">
              Your collection is waiting!
            </h3>

            <p className="mx-auto mt-2 max-w-sm text-sm text-slate-400">
              You haven't saved any destinations yet. Explore NovaTrip
              and bookmark places you'd love to visit.
            </p>

            <div className="mt-5 flex items-center justify-center gap-2 text-sm text-violet-300">
              <Compass size={17} />
              Start exploring destinations
            </div>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {places.map(place => (
              <article
                key={place.id}
                className="overflow-hidden rounded-xl border border-white/10 bg-[#0c1528] transition hover:-translate-y-1 hover:border-violet-500/30"
              >
                <div className="relative h-40 bg-white/5">
                  {place.image_url && !failedImages.includes(place.id) ? (
                    <img
                      src={place.image_url}
                      alt={place.place_name}
                      onError={() => setFailedImages(current =>
                        [...current, place.id]
                      )}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <ImageIcon size={36} className="text-slate-600" />
                    </div>
                  )}

                  <span className="absolute right-3 top-3 rounded-full bg-black/60 p-2">
                    <Heart size={17} className="fill-pink-400 text-pink-400" />
                  </span>
                </div>

                <div className="space-y-3 p-4">
                  <div>
                    <h3 className="font-semibold text-white">
                      {place.place_name}
                    </h3>

                    <p className="mt-1 flex items-center gap-1 text-sm text-slate-400">
                      <MapPin size={14} />
                      {place.country}
                    </p>
                  </div>

                  {place.tag && (
                    <span className="inline-block rounded-full bg-violet-500/10 px-3 py-1 text-xs text-violet-300">
                      {place.tag}
                    </span>
                  )}

                  <button
                    onClick={() => removePlace(place.id)}
                    disabled={deletingId === place.id}
                    className="flex w-full items-center justify-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm font-medium text-red-300 hover:bg-red-500/20 disabled:opacity-50"
                  >
                    <Trash2 size={15} />
                    {deletingId === place.id ? 'Removing...' : 'Remove place'}
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}

      </div>
    </section>
  )
}
