import { useState } from 'react'
import { supabase } from '../lib/supabase'
import { Compass, Mail, Lock, User, ArrowRight } from 'lucide-react'

export default function Auth() {
  const [isSignup, setIsSignup] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleAuth = async (e) => {
    e.preventDefault()
    setMessage('')
    setError('')

    if (isSignup && !name.trim()) {
      setError('Please enter your name.')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }

    setLoading(true)

    try {
      if (isSignup) {
        const { data, error } = await supabase.auth.signUp({
          email: email.trim(),
          password,
          options: {
            data: {
              full_name: name.trim(),
            },
          },
        })

        if (error) throw error

        if (data.session) {
          setMessage('Account created successfully!')
        } else {
          setMessage(
            'Account created! Please check your email and confirm your address before signing in.'
          )
        }
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        })

        if (error) throw error
      }
    } catch (err) {
      setError(err.message || 'Authentication failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0b1020] px-5 py-10 text-white">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-[#121b30] p-8 shadow-2xl">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-600">
            <Compass size={30} />
          </div>
          <h1 className="text-2xl font-bold">NovaTrip</h1>
          <p className="mt-2 text-sm text-slate-400">
            {isSignup
              ? 'Create your account and start exploring.'
              : 'Welcome back! Sign in to continue.'}
          </p>
        </div>

        <form onSubmit={handleAuth} className="space-y-5">
          {isSignup && (
            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Full name
              </label>
              <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-[#0b1020] px-4">
                <User size={18} className="text-slate-400" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  autoComplete="name"
                  required
                  className="w-full bg-transparent py-3 text-sm outline-none"
                />
              </div>
            </div>
          )}

          <div>
            <label className="mb-2 block text-sm text-slate-300">
              Email address
            </label>
            <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-[#0b1020] px-4">
              <Mail size={18} className="text-slate-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
                className="w-full bg-transparent py-3 text-sm outline-none"
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-300">
              Password
            </label>
            <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-[#0b1020] px-4">
              <Lock size={18} className="text-slate-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 8 characters"
                autoComplete={isSignup ? 'new-password' : 'current-password'}
                minLength={8}
                required
                className="w-full bg-transparent py-3 text-sm outline-none"
              />
            </div>
          </div>

          {error && (
            <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
              {error}
            </div>
          )}

          {message && (
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-300">
              {message}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 py-3.5 text-sm font-bold transition hover:bg-violet-500 disabled:opacity-50"
          >
            {loading
              ? 'Please wait...'
              : isSignup
                ? 'Create account'
                : 'Sign in'}
            {!loading && <ArrowRight size={17} />}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-400">
          {isSignup ? 'Already have an account?' : "Don't have an account?"}
          <button
            type="button"
            onClick={() => {
              setIsSignup(!isSignup)
              setMessage('')
              setError('')
            }}
            className="ml-2 font-semibold text-violet-300 hover:text-violet-200"
          >
            {isSignup ? 'Sign in' : 'Sign up'}
          </button>
        </div>
      </div>
    </div>
  )
}
