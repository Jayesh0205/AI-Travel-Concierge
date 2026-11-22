
import { useEffect, useState } from 'react'
import {
  UserRound,
  Mail,
  CalendarDays,
  Save,
  RefreshCw,
  Upload,
} from 'lucide-react'
import { supabase } from '../lib/supabase'

const API_BASE = (
  import.meta.env.VITE_API_URL ||
  'https://novatrip-api-r3sc.onrender.com'
).replace(/\/$/, '')

function Profile({ onProfileUpdated }) {
  const [profile, setProfile] = useState(null)
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [uploading, setUploading] = useState(false)

  // Get the current user's Supabase access token.
  const getAccessToken = async () => {
    const {
      data: { session },
      error,
    } = await supabase.auth.getSession()

    if (error) throw error

    if (!session?.access_token) {
      throw new Error('Please sign in again.')
    }

    return session.access_token
  }

  // Load the authenticated user's profile from FastAPI.
  useEffect(() => {
    let cancelled = false

    const loadProfile = async () => {
      setLoading(true)
      setError('')

      try {
        const token = await getAccessToken()

        const response = await fetch(`${API_BASE}/api/profile`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.detail || 'Unable to load profile.')
        }

        if (!cancelled) {
          setProfile(data.profile)
          setFullName(data.profile.full_name || '')
          onProfileUpdated?.(data.profile.full_name || '')
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadProfile()

    return () => {
      cancelled = true
    }
  }, [onProfileUpdated])

  // Upload and save the user's profile picture.
const handleAvatarUpload = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    setError('Please select an image.')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    setError('Image must be smaller than 5 MB.')
    return
  }

  setUploading(true)
  setError('')
  setSuccess('')

  try {
    const {
      data: { session },
    } = await supabase.auth.getSession()

    if (!session?.user) {
      throw new Error('Please sign in again.')
    }

    const token = await getAccessToken()

    const fileName = `${session.user.id}/${Date.now()}-${file.name.replace(/[^a-zA-Z0-9._-]/g, '-')}`

    const { error: uploadError } = await supabase.storage
      .from('avatars')
      .upload(fileName, file, {
        contentType: file.type,
      })

    if (uploadError) throw uploadError

    const { data } = supabase.storage
      .from('avatars')
      .getPublicUrl(fileName)

    const response = await fetch(`${API_BASE}/api/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        avatar_url: data.publicUrl,
      }),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(
        result.detail || 'Unable to save profile picture.'
      )
    }

    setProfile(result.profile)
    setSuccess('Profile picture updated successfully!')
  } catch (err) {
    setError(err.message)
  } finally {
    setUploading(false)
    e.target.value = ''
  }
}

  // Save the updated full name.
  const handleSave = async (e) => {
    e.preventDefault()

    const trimmedName = fullName.trim()

    if (!trimmedName) {
      setError('Please enter your full name.')
      return
    }

    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const token = await getAccessToken()

      const response = await fetch(`${API_BASE}/api/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          full_name: trimmedName,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to update profile.')
      }

      setProfile(data.profile)
      setFullName(data.profile.full_name || '')
      onProfileUpdated?.(data.profile.full_name || '')
      setSuccess('Your profile has been updated successfully!')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-400">
        <RefreshCw className="mx-auto mb-3 animate-spin" size={25} />
        Loading your profile...
      </div>
    )
  }

  if (error && !profile) {
    return (
      <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-red-300">
        {error}
      </div>
    )
  }

  if (!profile) return null

  const initial = (profile.full_name || profile.username || 'U')
    .charAt(0)
    .toUpperCase()

  return (
    <section className="space-y-7">

      {/* Profile heading */}
      <div>
        <p className="text-sm font-medium text-violet-400">
          YOUR ACCOUNT
        </p>

        <h1 className="mt-1 text-2xl font-bold">
          My Profile
        </h1>

        <p className="mt-2 text-sm text-slate-400">
          Manage your personal information and account details.
        </p>
      </div>

      {/* Profile overview */}
      <div className="rounded-2xl border border-white/10 bg-[#121b30] p-7">

        <div className="flex flex-wrap items-center gap-5">

          <div className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-violet-500 to-blue-500 text-3xl font-bold">
            {profile.avatar_url ? (
              <img
                src={profile.avatar_url}
                alt="Profile"
                className="h-full w-full object-cover"
              />
            ) : (
              initial
            )}
          </div>

          <div>
            <h2 className="text-xl font-bold">
              {profile.full_name || profile.username}
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              {profile.email}
            </p>

            <span className="mt-3 inline-block rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400">
              Signed-in account
            </span>

            <label className="mt-5 inline-flex cursor-pointer items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold hover:bg-violet-500">
  <Upload size={16} />

  {uploading ? 'Uploading...' : 'Change Profile Picture'}

  <input
    type="file"
    accept="image/*"
    className="hidden"
    disabled={uploading}
    onChange={handleAvatarUpload}
  />
</label>

          </div>

        </div>
      </div>

      {/* Editable profile form */}
      <form
        onSubmit={handleSave}
        className="rounded-2xl border border-white/10 bg-[#121b30] p-7"
      >

        <h2 className="mb-6 text-lg font-bold">
          Personal Information
        </h2>

        <div className="space-y-5">

          <div>
            <label className="mb-2 block text-sm text-slate-400">
              Full Name
            </label>

            <div className="relative">
              <UserRound
                size={18}
                className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
              />

              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                maxLength={150}
                placeholder="Enter your full name"
                className="w-full rounded-xl border border-white/10 bg-[#0b1020] py-3 pl-12 pr-4 text-sm text-white outline-none focus:border-violet-500"
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-400">
              Username
            </label>

            <input
              type="text"
              value={profile.username}
              readOnly
              className="w-full rounded-xl border border-white/10 bg-[#0b1020] px-4 py-3 text-sm text-slate-400 outline-none"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-400">
              Email Address
            </label>

            <div className="relative">
              <Mail
                size={18}
                className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
              />

              <input
                type="email"
                value={profile.email}
                readOnly
                className="w-full rounded-xl border border-white/10 bg-[#0b1020] py-3 pl-12 pr-4 text-sm text-slate-400 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-400">
              Account Created
            </label>

            <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-[#0b1020] px-4 py-3 text-sm text-slate-400">
              <CalendarDays size={18} />

              {new Date(profile.created_at).toLocaleDateString(
                'en-IN',
                {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric',
                }
              )}
            </div>
          </div>

        </div>

        {/* API error and success messages */}
        {error && (
          <p className="mt-5 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">
            {error}
          </p>
        )}

        {success && (
          <p className="mt-5 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3 text-sm text-emerald-300">
            {success}
          </p>
        )}

        <button
          type="submit"
          disabled={saving}
          className="mt-6 flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-6 py-3 text-sm font-semibold transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Save size={17} />

          {saving ? 'Saving...' : 'Save Changes'}
        </button>

      </form>

    </section>
  )
}

export default Profile
