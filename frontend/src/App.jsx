import ReactMarkdown from 'react-markdown'
import { useState, useEffect, useCallback } from 'react'
import {
  Compass, LayoutDashboard, Map, Heart, Settings,
  Search, Activity, Server, RefreshCw, CheckCircle2,
XCircle, Gauge, Clock3, Bell, MapPin, CalendarDays, ArrowRight,
  Plane, Sparkles, Clock, Menu, Plus, Globe2,
  Wallet, Users
} from 'lucide-react'
const API_BASE = (
  import.meta.env.VITE_API_URL || 'https://novatrip-api-r3sc.onrender.com'
).replace(/\/$/, '');


const destinations = [
  {
    name: 'Bali',
    country: 'Indonesia',
    price: '₹35,000',
    image: 'photo-1537996194471-e657df975ab4',
    tag: 'Tropical Escape'
  },
  {
    name: 'Swiss Alps',
    country: 'Switzerland',
    price: '₹85,000',
    image: 'photo-1531366936337-7c912a4589a7',
    tag: 'Mountain Adventure'
  },
  {
    name: 'Santorini',
    country: 'Greece',
    price: '₹65,000',
    image: 'photo-1533105079780-92b9be482077',
    tag: 'Romantic Getaway'
  },
]

function App() {
  const [activePage, setActivePage] = useState('Dashboard')
  const [destination, setDestination] = useState('')
  const [origin, setOrigin] = useState('')
  const [travelDate, setTravelDate] = useState('')
  const [travellers, setTravellers] = useState('2 Travellers')
  const [message, setMessage] = useState('')
  const [itinerary, setItinerary] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [savedTrips, setSavedTrips] = useState([])
  const [selectedTrip, setSelectedTrip] = useState(null)
  const [tripsLoading, setTripsLoading] = useState(false)
  const [tripsError, setTripsError] = useState('')
  // Monitoring dashboard states
const [monitoring, setMonitoring] = useState(null)
const [monitoringLoading, setMonitoringLoading] = useState(false)
const [monitoringError, setMonitoringError] = useState('')
const [backendOnline, setBackendOnline] = useState(false)
const [databaseHealth, setDatabaseHealth] = useState(null)

  
const handleSearch = async (e) => {
  e.preventDefault()

  if (!destination.trim()) {
    setMessage('Please enter your destination first.')
    return
  }

  setMessage('')
  setItinerary('')
  setIsLoading(true)

  try {
    const response = await fetch(
      `${API_BASE}/api/travel/plan`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_request: `Plan a travel itinerary from ${origin || 'my location'} to ${destination} for ${travellers}. Departure date: ${travelDate || 'flexible'}. Include attractions, activities, travel suggestions and an estimated budget.`,
          origin: origin,
          destination: destination,
          departure_date: travelDate,
          uploaded_text: '',
        }),
      }
    )

    const data = await response.json()

    if (!response.ok) {
      throw new Error(
        data.detail || 'Failed to generate your itinerary.'
      )
    }

    setItinerary(data.itinerary)
    setMessage('Your AI-generated itinerary is ready!')

  } catch (error) {
    console.error('Travel planning error:', error)
    setMessage(error.message || 'Unable to connect to NovaTrip API.')
  } finally {
    setIsLoading(false)
  }
}


const loadSavedTrips = async () => {
  setTripsLoading(true)
  setTripsError('')

  try {
    const response = await fetch(`${API_BASE}/api/trips`)
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Unable to load saved trips.')
    }

    setSavedTrips(data.trips || [])

  } catch (error) {
    console.error('Loading trips failed:', error)
    setTripsError(error.message)
  } finally {
    setTripsLoading(false)
  }
}

const openSavedTrip = async (tripId) => {
  setTripsLoading(true)
  setTripsError('')

  try {
    const response = await fetch(
      `${API_BASE}/api/trips/${tripId}`
    )

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Unable to open this itinerary.')
    }

    setSelectedTrip(data.trip)

  } catch (error) {
    console.error('Opening trip failed:', error)
    setTripsError(error.message)
  } finally {
    setTripsLoading(false)
  }
}



const loadMonitoring = useCallback(async () => {
  setMonitoringLoading(true)
  setMonitoringError('')

  try {
    const [
      metricsResponse,
      healthResponse,
      databaseResponse,
    ] = await Promise.all([
      fetch(`${API_BASE}/api/monitoring/overview`),
      fetch(`${API_BASE}/health`),
      fetch(`${API_BASE}/api/monitoring/database`),
    ])

    setBackendOnline(healthResponse.ok)

    if (!metricsResponse.ok) {
      throw new Error('Unable to retrieve monitoring statistics.')
    }

    if (!databaseResponse.ok) {
      throw new Error('Unable to retrieve database health.')
    }

    const metricsData = await metricsResponse.json()
    const databaseData = await databaseResponse.json()

    setMonitoring(metricsData)
    setDatabaseHealth(databaseData)

  } catch (error) {
    console.error('Monitoring error:', error)
    setMonitoringError(error.message)
    setBackendOnline(false)
    setDatabaseHealth(null)

  } finally {
    setMonitoringLoading(false)
  }
}, [])


useEffect(() => {
  if (activePage !== 'Monitoring') return

  loadMonitoring()

  const interval = setInterval(loadMonitoring, 10000)

  return () => clearInterval(interval)
}, [activePage, loadMonitoring])

const formatUptime = (seconds = 0) => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  return `${days}d ${hours}h ${minutes}m ${secs}s`
}


// Prepare response-time chart data
const chartData = [...(monitoring?.recent_activity || [])].reverse()

const maxResponseTime = Math.max(
  ...chartData.map(item => item.response_time_ms),
  10
)

const chartPoints = chartData.map((item, index) => ({
  x: chartData.length > 1
    ? (index / (chartData.length - 1)) * 100
    : 50,
  y: 100 - (item.response_time_ms / maxResponseTime) * 85,
  time: item.response_time_ms,
}))




  const navigation = [
  { name: 'Dashboard', icon: LayoutDashboard },
  { name: 'Explore', icon: Compass },
  { name: 'My Trips', icon: Map },
  { name: 'Monitoring', icon: Activity },
  { name: 'Saved Places', icon: Heart },
]

  return (
    <div className="min-h-screen bg-[#0b1020] text-white">

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-white/10 bg-[#10172a] px-6 py-7 transition-transform duration-300 lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>

        <div className="mb-12 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-600 shadow-lg shadow-violet-600/30">
            <Compass size={25} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wide">NovaTrip</h1>
            <p className="text-xs text-slate-400">AI Travel Concierge</p>
          </div>
        </div>

        <p className="mb-4 text-xs font-semibold uppercase tracking-[2px] text-slate-500">
          Workspace
        </p>

        <nav className="space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon

            return (
              <button
                key={item.name}
                onClick={() => {
  setActivePage(item.name)
  setSidebarOpen(false)

  if (item.name === 'My Trips') {
    setSelectedTrip(null)
    loadSavedTrips()
  }

  if (item.name === 'Monitoring') {
    loadMonitoring()
  }
}}
                className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm transition ${
                  activePage === item.name
                    ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/20'
                    : 'text-slate-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                <Icon size={19} />
                {item.name}
              </button>
            )
          })}
        </nav>

        <div className="mt-10">
          <p className="mb-4 text-xs font-semibold uppercase tracking-[2px] text-slate-500">
            Preferences
          </p>

          <button
            onClick={() => setActivePage('Settings')}
            className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm ${
              activePage === 'Settings'
                ? 'bg-violet-600 text-white'
                : 'text-slate-400 hover:bg-white/5 hover:text-white'
            }`}
          >
            <Settings size={19} />
            Settings
          </button>
        </div>

        <div className="mt-auto rounded-2xl border border-violet-400/20 bg-gradient-to-br from-violet-600/20 to-blue-600/10 p-4">
          <Sparkles className="mb-3 text-violet-400" size={23} />
          <h3 className="font-semibold">Your AI Travel Buddy</h3>
          <p className="mt-2 text-xs leading-5 text-slate-400">
            Discover destinations and create your next unforgettable journey.
          </p>
          <button
            onClick={() => setActivePage('Explore')}
            className="mt-4 flex items-center gap-2 text-sm font-semibold text-violet-300"
          >
            Explore now <ArrowRight size={15} />
          </button>
        </div>

        <div className="mt-6 flex items-center gap-3 border-t border-white/10 pt-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-blue-500 font-bold">
            J
          </div>
          <div>
            <p className="text-sm font-semibold">Traveler</p>
            <p className="text-xs text-slate-500">Personal account</p>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="min-h-screen lg:ml-64">

        {/* Top navigation */}
        <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-white/10 bg-[#0b1020]/90 px-5 backdrop-blur-xl md:px-10">

          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded-lg p-2 text-slate-300 hover:bg-white/10 lg:hidden"
            >
              <Menu size={23} />
            </button>

            <div>
              <p className="text-xs text-slate-500">Your journey starts here</p>
              <h2 className="text-lg font-semibold">{activePage}</h2>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button className="relative rounded-xl border border-white/10 p-3 text-slate-300 hover:bg-white/5">
              <Bell size={19} />
              <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-violet-500" />
            </button>

            <div className="hidden h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-blue-500 font-bold sm:flex">
              J
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-7xl space-y-10 px-5 py-9 md:px-10">
	
{activePage === 'Monitoring' ? (
  <section className="space-y-7">

    {/* Monitoring Header */}
    <div className="flex flex-wrap items-center justify-between gap-4">
      <div>
        <p className="text-sm font-medium text-violet-400">
          SYSTEM ANALYTICS
        </p>
        <h1 className="mt-1 text-2xl font-bold">
          Monitoring Dashboard
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Real-time performance and API health statistics.
        </p>
      </div>

      <button
        onClick={loadMonitoring}
        disabled={monitoringLoading}
        className="flex items-center gap-2 rounded-xl bg-violet-600 px-5 py-3 text-sm font-semibold hover:bg-violet-500 disabled:opacity-50"
      >
        <RefreshCw
          size={16}
          className={monitoringLoading ? 'animate-spin' : ''}
        />
        Refresh metrics
      </button>
    </div>

    {/* Backend Status */}
    <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-[#121b30] p-5">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-violet-500/10 p-3 text-violet-300">
          <Server size={23} />
        </div>
        <div>
          <h3 className="font-semibold">FastAPI Backend</h3>
          <p className="text-xs text-slate-400">
            {API_BASE}
          </p>
        </div>
      </div>

{/* PostgreSQL Database Status */}
<div className="flex items-center justify-between rounded-2xl border border-white/10 bg-[#121b30] p-5">

  <div className="flex items-center gap-3">
    <div className="rounded-xl bg-blue-500/10 p-3 text-blue-300">
      <Server size={23} />
    </div>

    <div>
      <h3 className="font-semibold">PostgreSQL Database</h3>
      <p className="text-xs text-slate-400">
        Database connection health
      </p>

      {databaseHealth && (
        <p className="mt-1 text-xs text-slate-500">
          Response time: {databaseHealth.response_time_ms} ms
        </p>
      )}
    </div>
  </div>

  <span className={`rounded-full px-3 py-2 text-xs font-semibold ${
    databaseHealth?.connection_status === 'online'
      ? 'bg-emerald-500/10 text-emerald-400'
      : databaseHealth?.connection_status === 'offline'
        ? 'bg-red-500/10 text-red-400'
        : 'bg-slate-500/10 text-slate-400'
  }`}>
    {databaseHealth?.connection_status === 'online'
      ? '● Online'
      : databaseHealth?.connection_status === 'offline'
        ? '● Offline'
        : '● Checking'}
  </span>

</div>



      <span className={`rounded-full px-3 py-2 text-xs font-semibold ${
        backendOnline
          ? 'bg-emerald-500/10 text-emerald-400'
          : 'bg-red-500/10 text-red-400'
      }`}>
        {backendOnline ? '● Online' : '● Offline'}
      </span>
    </div>

    {monitoringError && (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
        {monitoringError}
      </div>
    )}

    {monitoringLoading && !monitoring && (
      <div className="py-12 text-center text-slate-400">
        Loading monitoring statistics...
      </div>
    )}

    {monitoring && (
      <>
        {/* Metric Cards */}
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">

          {[
            {
              title: 'Total Requests',
              value: monitoring.total_requests,
              icon: Activity,
              color: 'text-violet-400',
            },
            {
              title: 'Successful Requests',
              value: monitoring.successful_requests,
              icon: CheckCircle2,
              color: 'text-emerald-400',
            },
            {
              title: 'Failed Requests',
              value: monitoring.failed_requests,
              icon: XCircle,
              color: 'text-red-400',
            },
            {
              title: 'Avg Response Time',
              value: `${monitoring.average_response_time_ms} ms`,
              icon: Gauge,
              color: 'text-blue-400',
            },
          ].map((item) => {
            const Icon = item.icon

            return (
              <div
                key={item.title}
                className="rounded-2xl border border-white/10 bg-[#121b30] p-5"
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm text-slate-400">
                    {item.title}
                  </p>
                  <Icon size={21} className={item.color} />
                </div>

                <h2 className="mt-4 text-3xl font-bold">
                  {item.value}
                </h2>
              </div>
            )
          })}

        </div>

        {/* Uptime and Request Success */}
        <div className="grid gap-5 md:grid-cols-2">

          <div className="rounded-2xl border border-white/10 bg-[#121b30] p-6">
            <div className="flex items-center gap-3">
              <Clock3 className="text-violet-400" size={23} />
              <h3 className="font-semibold">Backend Uptime</h3>
            </div>

            <p className="mt-5 text-3xl font-bold text-violet-300">
              {formatUptime(monitoring.uptime_seconds)}
            </p>

            <p className="mt-2 text-xs text-slate-500">
              Since {new Date(monitoring.started_at).toLocaleString()}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-[#121b30] p-6">
            <div className="flex items-center gap-3">
              <Gauge className="text-emerald-400" size={23} />
              <h3 className="font-semibold">Request Success Rate</h3>
            </div>

            <p className="mt-5 text-3xl font-bold text-emerald-400">
              {monitoring.total_requests > 0
                ? (
                    monitoring.successful_requests /
                    monitoring.total_requests *
                    100
                  ).toFixed(1)
                : '0.0'}%
            </p>

            <p className="mt-2 text-xs text-slate-500">
              Based on recorded HTTP requests
            </p>
          </div>

        </div>


{/* API Response Time Chart */}
<div className="rounded-2xl border border-white/10 bg-[#121b30] p-5">

  <div className="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h3 className="font-semibold">API Performance Analytics</h3>
      <p className="mt-1 text-xs text-slate-400">
        Response time across the latest 20 requests
      </p>
    </div>

    <span className="rounded-lg bg-violet-500/10 px-3 py-2 text-xs text-violet-300">
      Live Monitoring
    </span>
  </div>

  <div className="mt-6">
    {chartPoints.length < 2 ? (
      <p className="py-12 text-center text-sm text-slate-400">
        Waiting for more API requests to generate the chart...
      </p>
    ) : (
      <>
        <div className="flex justify-between text-xs text-slate-500">
          <span>{maxResponseTime.toFixed(1)} ms</span>
          <span>0 ms</span>
        </div>

        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="mt-3 h-48 w-full overflow-visible"
        >
          {[15, 40, 65, 90].map(y => (
            <line
              key={y}
              x1="0"
              y1={y}
              x2="100"
              y2={y}
              stroke="#334155"
              strokeWidth="0.4"
              strokeDasharray="2 2"
            />
          ))}

          <polyline
            points={chartPoints
              .map(point => `${point.x},${point.y}`)
              .join(' ')}
            fill="none"
            stroke="#a78bfa"
            strokeWidth="1.5"
            vectorEffect="non-scaling-stroke"
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          {chartPoints.map((point, index) => (
            <circle
              key={index}
              cx={point.x}
              cy={point.y}
              r="1.5"
              fill="#a78bfa"
            >
              <title>{point.time} ms</title>
            </circle>
          ))}
        </svg>

        <div className="mt-3 flex justify-between text-xs text-slate-500">
          <span>Oldest request</span>
          <span>Latest request</span>
        </div>
      </>
    )}
  </div>

  <div className="mt-5 grid grid-cols-2 gap-4 border-t border-white/10 pt-4">
    <div>
      <p className="text-xs text-slate-400">Fastest request</p>
      <p className="mt-1 text-xl font-bold text-emerald-400">
        {Math.min(
          ...chartData.map(item => item.response_time_ms),
          Infinity
        ).toFixed(2)} ms
      </p>
    </div>

    <div>
      <p className="text-xs text-slate-400">Slowest request</p>
      <p className="mt-1 text-xl font-bold text-violet-300">
        {chartData.length
          ? Math.max(...chartData.map(item => item.response_time_ms)).toFixed(2)
          : '0.00'} ms
      </p>
    </div>
  </div>

</div>


        {/* Recent API Activity */}
        <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#121b30]">

          <div className="flex items-center justify-between border-b border-white/10 p-5">
            <div>
              <h3 className="font-semibold">Recent API Activity</h3>
              <p className="mt-1 text-xs text-slate-400">
                Latest 20 recorded requests
              </p>
            </div>

            <Activity className="text-violet-400" size={22} />
          </div>

          {monitoring.recent_activity.length === 0 ? (
            <p className="p-8 text-center text-sm text-slate-400">
              No API activity recorded yet.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">

                <thead className="bg-white/5 text-xs text-slate-400">
                  <tr>
                    <th className="p-4">Method</th>
                    <th className="p-4">Endpoint</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Response Time</th>
                    <th className="p-4">Timestamp</th>
                  </tr>
                </thead>

                <tbody>
                  {monitoring.recent_activity.map((activity, index) => (
                    <tr
                      key={`${activity.timestamp}-${index}`}
                      className="border-t border-white/5"
                    >
                      <td className="p-4 font-semibold text-violet-300">
                        {activity.method}
                      </td>

                      <td className="p-4 text-slate-300">
                        {activity.path}
                      </td>

                      <td className="p-4">
                        <span className={`rounded-full px-2 py-1 text-xs ${
                          activity.status_code < 400
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : 'bg-red-500/10 text-red-400'
                        }`}>
                          {activity.status_code}
                        </span>
                      </td>

                      <td className="p-4 text-slate-300">
                        {activity.response_time_ms} ms
                      </td>

                      <td className="whitespace-nowrap p-4 text-xs text-slate-500">
                        {new Date(activity.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>

              </table>
            </div>
          )}

        </div>

        <p className="text-center text-xs text-slate-500">
          Metrics refresh automatically every 10 seconds.
        </p>
      </>
    )}

  </section>
) : activePage === 'My Trips' ? (
  <section className="space-y-6">

    <div className="flex flex-wrap items-center justify-between gap-4">
      <div>
        <p className="text-sm font-medium text-violet-400">
          YOUR TRAVEL HISTORY
        </p>
        <h1 className="mt-1 text-2xl font-bold">
          {selectedTrip ? 'Saved Itinerary' : 'My Trips'}
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Your AI-generated travel plans, saved in PostgreSQL.
        </p>
      </div>

      <div className="flex gap-3">
        {selectedTrip && (
          <button
            onClick={() => setSelectedTrip(null)}
            className="rounded-xl border border-white/10 px-4 py-3 text-sm hover:bg-white/5"
          >
            Back to trips
          </button>
        )}

        <button
          onClick={loadSavedTrips}
          disabled={tripsLoading}
          className="rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold hover:bg-violet-500 disabled:opacity-50"
        >
          {tripsLoading ? 'Loading...' : 'Refresh trips'}
        </button>
      </div>
    </div>

    {tripsError && (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
        {tripsError}
      </div>
    )}

    {tripsLoading && (
      <div className="py-12 text-center text-slate-400">
        Loading your travel plans...
      </div>
    )}

    {!tripsLoading && selectedTrip && (
      <article className="rounded-2xl border border-white/10 bg-[#121b30] p-6">

        <div className="mb-5 border-b border-white/10 pb-5">
          <p className="text-xs text-violet-400">
            SAVED TRIP #{selectedTrip.id}
          </p>

          <h2 className="mt-2 text-lg font-bold">
            {selectedTrip.query}
          </h2>

          <p className="mt-2 text-xs text-slate-500">
            Saved on {new Date(selectedTrip.created_at).toLocaleString()}
          </p>
        </div>

        <div className="prose prose-invert max-w-none text-sm leading-7 text-slate-300
          [&_h3]:mt-6 [&_h3]:mb-3 [&_h3]:text-lg [&_h3]:font-bold [&_h3]:text-violet-300
          [&_h2]:mt-6 [&_h2]:mb-3 [&_h2]:text-xl [&_h2]:font-bold
          [&_strong]:text-white [&_li]:my-1
          [&_hr]:my-5 [&_hr]:border-white/10">

          <ReactMarkdown>
            {selectedTrip.response.replace(/\\([*_`])/g, '$1')}
          </ReactMarkdown>

        </div>
      </article>
    )}

    {!tripsLoading && !selectedTrip && !tripsError && (
      <>
        {savedTrips.length === 0 ? (
          <div className="rounded-2xl border border-white/10 bg-[#121b30] p-12 text-center">
            <Map size={40} className="mx-auto text-violet-400" />
            <h3 className="mt-4 text-lg font-bold">No saved trips yet</h3>
            <p className="mt-2 text-sm text-slate-400">
              Generate your first itinerary using NovaTrip.
            </p>
          </div>
        ) : (
          <div className="grid gap-5 md:grid-cols-2">
            {savedTrips.map((trip) => (
              <article
                key={trip.id}
                className="rounded-2xl border border-white/10 bg-[#121b30] p-5 transition hover:border-violet-500/50"
              >
                <div className="flex items-center justify-between">
                  <span className="rounded-full bg-violet-500/10 px-3 py-1 text-xs text-violet-300">
                    Saved Trip #{trip.id}
                  </span>

                  <MapPin size={19} className="text-violet-400" />
                </div>

                <h3 className="mt-5 line-clamp-3 text-base font-semibold leading-7">
                  {trip.query}
                </h3>

                <p className="mt-4 flex items-center gap-2 text-xs text-slate-500">
                  <CalendarDays size={14} />
                  {new Date(trip.created_at).toLocaleDateString()}
                </p>

                <button
                  onClick={() => openSavedTrip(trip.id)}
                  className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 py-3 text-sm font-semibold transition hover:bg-violet-500"
                >
                  View itinerary <ArrowRight size={16} />
                </button>
              </article>
            ))}
          </div>
        )}
      </>
    )}

  </section>
) : (
  <>


          {/* Welcome section */}
          <section className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#27205a] via-[#211c49] to-[#10172a] p-7 md:p-11">

            <div className="absolute -right-20 -top-32 h-80 w-80 rounded-full bg-violet-600/20 blur-3xl" />

            <div className="relative z-10 max-w-2xl">
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-violet-300/20 bg-violet-400/10 px-4 py-2 text-xs text-violet-200">
                <Sparkles size={14} />
                AI-POWERED TRAVEL EXPERIENCE
              </div>

              <h1 className="text-3xl font-bold leading-tight md:text-5xl">
                Explore the world.
                <span className="block text-violet-300">
                  We'll plan the journey.
                </span>
              </h1>

              <p className="mt-5 max-w-lg text-sm leading-7 text-slate-300 md:text-base">
                Tell NovaTrip where you want to go. Your AI travel concierge
                will help you turn your travel dreams into an itinerary.
              </p>

              <button
                onClick={() => document.getElementById('trip-planner')?.scrollIntoView({ behavior: 'smooth' })}
                className="mt-7 flex items-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-bold text-[#17132e] transition hover:bg-violet-100"
              >
                Plan a new trip <ArrowRight size={17} />
              </button>
            </div>

            <Globe2
              className="absolute bottom-8 right-10 hidden text-white/10 md:block"
              size={190}
              strokeWidth={0.7}
            />
          </section>

          {/* Trip planner */}
          <section id="trip-planner">
            <div className="mb-5">
              <p className="text-sm font-medium text-violet-400">LET'S PLAN</p>
              <h2 className="mt-1 text-2xl font-bold">Where do you want to go?</h2>
              <p className="mt-2 text-sm text-slate-400">
                Enter your travel details to get started.
              </p>
            </div>

            <form
              onSubmit={handleSearch}
              className="grid gap-4 rounded-2xl border border-white/10 bg-[#121b30] p-5 md:grid-cols-2 xl:grid-cols-4"
            >
              <div>
                <label className="mb-2 flex items-center gap-2 text-xs text-slate-400">
                  <MapPin size={15} /> Starting point
                </label>
                <input
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value)}
                  placeholder="e.g. Mumbai"
                  className="w-full rounded-xl border border-white/10 bg-[#0b1020] px-4 py-3 text-sm outline-none transition focus:border-violet-500"
                />
              </div>

              <div>
                <label className="mb-2 flex items-center gap-2 text-xs text-slate-400">
                  <Plane size={15} /> Destination
                </label>
                <input
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  placeholder="e.g. Goa"
                  className="w-full rounded-xl border border-white/10 bg-[#0b1020] px-4 py-3 text-sm outline-none transition focus:border-violet-500"
                />
              </div>

              <div>
                <label className="mb-2 flex items-center gap-2 text-xs text-slate-400">
                  <CalendarDays size={15} /> Departure date
                </label>
                <input
                  type="date"
                  value={travelDate}
                  onChange={(e) => setTravelDate(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-[#0b1020] px-4 py-3 text-sm text-slate-300 outline-none focus:border-violet-500"
                />
              </div>

              <div>
                <label className="mb-2 flex items-center gap-2 text-xs text-slate-400">
                  <Users size={15} /> Travellers
                </label>
                <select
                  value={travellers}
                  onChange={(e) => setTravellers(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-[#0b1020] px-4 py-3 text-sm text-slate-300 outline-none focus:border-violet-500"
                >
                  <option>1 Traveller</option>
                  <option>2 Travellers</option>
                  <option>3 Travellers</option>
                  <option>4 Travellers</option>
                  <option>5+ Travellers</option>
                </select>
              </div>

              <div className="md:col-span-2 xl:col-span-4">
                <button
                  type="submit"
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 py-4 text-sm font-bold transition hover:bg-violet-500"
                >
                  <Sparkles size={18} />
                  {isLoading ? (
  <>
    <span className="animate-spin">✦</span>
    Generating your itinerary...
  </>
) : (
  <>
    <Sparkles size={18} />
    Plan my trip with AI
  </>
)}
                </button>

{message && (
  <div className="mt-4 rounded-xl border border-violet-500/30 bg-violet-500/10 p-4 text-sm text-violet-200">
    {message}
  </div>
)}

                {itinerary && (
  <div className="mt-6 rounded-2xl border border-violet-500/30 bg-[#0b1020] p-6">
    <div className="mb-4 flex items-center gap-2 text-violet-300">
      <Sparkles size={20} />
      <h3 className="text-lg font-bold">
        Your AI Travel Itinerary
      </h3>
    </div>

    <div className="prose prose-invert max-w-none text-sm leading-7 text-slate-300
  [&_h3]:mt-6 [&_h3]:mb-3 [&_h3]:text-lg [&_h3]:font-bold [&_h3]:text-violet-300
  [&_h2]:mt-6 [&_h2]:mb-3 [&_h2]:text-xl [&_h2]:font-bold
  [&_strong]:text-white
  [&_li]:my-1
  [&_hr]:my-5 [&_hr]:border-white/10">

  <ReactMarkdown>
    {itinerary.replace(/\\([*_`])/g, '$1')}
  </ReactMarkdown>

</div>
  </div>
)}
              </div>
            </form>
          </section>

          {/* Popular destinations */}
          <section>
            <div className="mb-6 flex items-end justify-between">
              <div>
                <p className="text-sm font-medium text-violet-400">GET INSPIRED</p>
                <h2 className="mt-1 text-2xl font-bold">Popular destinations</h2>
                <p className="mt-2 text-sm text-slate-400">
                  Places worth adding to your bucket list.
                </p>
              </div>

              <button
                onClick={() => setActivePage('Explore')}
                className="hidden items-center gap-2 text-sm text-violet-300 hover:text-white sm:flex"
              >
                Explore all <ArrowRight size={16} />
              </button>
            </div>

            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {destinations.map((place) => (
                <article
                  key={place.name}
                  className="group overflow-hidden rounded-2xl border border-white/10 bg-[#121b30] transition hover:-translate-y-1 hover:border-violet-500/40"
                >
                  <div className="relative h-52 overflow-hidden">
                    <img
                      src={`https://images.unsplash.com/${place.image}?auto=format&fit=crop&w=900&q=85`}
                      alt={place.name}
                      className="h-full w-full object-cover transition duration-500 group-hover:scale-110"
                    />
                    <span className="absolute left-4 top-4 rounded-full bg-black/60 px-3 py-2 text-xs font-medium backdrop-blur">
                      {place.tag}
                    </span>
                    <button
                      onClick={() => setMessage(`${place.name} added to your inspiration list. Choose it in the destination field to plan a trip.`)}
                      className="absolute right-4 top-4 rounded-full bg-black/50 p-2 backdrop-blur hover:bg-violet-600"
                      aria-label={`Save ${place.name}`}
                    >
                      <Heart size={17} />
                    </button>
                  </div>

                  <div className="p-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-bold">{place.name}</h3>
                        <p className="mt-1 flex items-center gap-1 text-xs text-slate-400">
                          <MapPin size={13} /> {place.country}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-slate-500">Estimated from</p>
                        <p className="mt-1 font-bold text-violet-300">{place.price}</p>
                      </div>
                    </div>

                    <button
                      onClick={() => {
                        setDestination(place.name)
                        document.getElementById('trip-planner')?.scrollIntoView({ behavior: 'smooth' })
                      }}
                      className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-3 text-sm font-medium transition hover:border-violet-500 hover:bg-violet-600/10"
                    >
                      Explore destination <ArrowRight size={15} />
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>

          {/* Bottom information */}
          <section className="grid gap-4 pb-8 md:grid-cols-3">
            {[
              { icon: Sparkles, title: 'AI-Powered Planning', desc: 'Personalized travel itineraries.' },
              { icon: Wallet, title: 'Smart Budgeting', desc: 'Plan trips around your budget.' },
              { icon: Clock, title: 'Save Time', desc: 'Keep your travel research organized.' },
            ].map((item) => {
              const Icon = item.icon

              return (
                <div key={item.title} className="flex items-center gap-4 rounded-2xl border border-white/10 bg-[#121b30] p-5">
                  <div className="rounded-xl bg-violet-500/10 p-3 text-violet-300">
                    <Icon size={22} />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold">{item.title}</h3>
                    <p className="mt-1 text-xs text-slate-400">{item.desc}</p>
                  </div>
                </div>
              )
            })}
          </section>

          <footer className="border-t border-white/10 py-6 text-center text-xs text-slate-500">
            © 2026 NovaTrip · Your AI-powered Travel Concierge
          </footer>

	</>
          )}

        </div>
      </main>
    </div>
  )
}

export default App
