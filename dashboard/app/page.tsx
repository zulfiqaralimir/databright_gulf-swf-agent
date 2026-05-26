'use client'

import { useState, useEffect, useCallback } from 'react'
import SWFCard from './components/SWFCard'
import IntelCard from './components/IntelCard'
import FilingsTable from './components/FilingsTable'
import type { Filing } from './components/IntelCard'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface SWFSummary {
  swf_name: string
  count: number
  latest_date: string
  swf_emoji: string
  swf_country: string
}

export default function Home() {
  const [filings, setFilings] = useState<Filing[]>([])
  const [summary, setSummary] = useState<SWFSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    try {
      const [filingsRes, summaryRes] = await Promise.all([
        fetch(`${API_URL}/api/filings?limit=20`),
        fetch(`${API_URL}/api/summary`),
      ])

      if (!filingsRes.ok || !summaryRes.ok) throw new Error('API returned non-200')

      const [filingsData, summaryData]: [Filing[], SWFSummary[]] = await Promise.all([
        filingsRes.json(),
        summaryRes.json(),
      ])

      setFilings(filingsData)
      setSummary(summaryData)
      setLastRefresh(new Date())
      setError(null)
    } catch {
      setError('Cannot connect to API. Make sure the FastAPI server is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 60_000)
    return () => clearInterval(interval)
  }, [fetchData])

  const totalFilings = summary.reduce((acc, s) => acc + s.count, 0)

  return (
    <main className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-white">
              🏦 Gulf SWF Filing Intelligence
            </h1>
            <p className="text-gray-500 text-xs mt-0.5">
              SC 13D/13G real-time monitor · Bright Data MCP + Gemini 2.0 Flash
            </p>
          </div>
          <div className="flex items-center gap-3">
            {lastRefresh && (
              <span className="text-gray-600 text-xs hidden sm:block">
                Updated {lastRefresh.toLocaleTimeString()}
              </span>
            )}
            <span
              className={`flex items-center gap-1.5 text-xs px-3 py-1 rounded-full border ${
                error
                  ? 'bg-red-500/10 text-red-400 border-red-500/30'
                  : 'bg-green-500/10 text-green-400 border-green-500/30'
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  error ? 'bg-red-400' : 'bg-green-400 animate-pulse'
                }`}
              />
              {error ? 'API Offline' : 'Live'}
            </span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-10">
        {/* Error Banner */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
            ⚠ {error}
          </div>
        )}

        {/* Stats bar */}
        {!loading && !error && (
          <div className="flex gap-6 text-sm text-gray-400">
            <span>
              <span className="text-white font-semibold">{totalFilings}</span> filings tracked
            </span>
            <span>
              <span className="text-white font-semibold">{summary.length}</span> SWFs monitored
            </span>
            <span>Auto-refreshes every 60s</span>
          </div>
        )}

        {/* SWF Summary Cards */}
        <section>
          <h2 className="text-gray-400 text-xs font-semibold uppercase tracking-widest mb-4">
            Sovereign Wealth Funds
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="bg-gray-800 rounded-lg h-28 animate-pulse" />
              ))
            ) : summary.length > 0 ? (
              summary.map((s) => <SWFCard key={s.swf_name} {...s} />)
            ) : (
              <p className="text-gray-600 text-sm col-span-5">
                No data yet — run the agent to populate.
              </p>
            )}
          </div>
        </section>

        {/* Intelligence Feed */}
        <section>
          <h2 className="text-gray-400 text-xs font-semibold uppercase tracking-widest mb-4">
            Intelligence Feed
          </h2>
          <div className="space-y-3">
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="bg-gray-800 rounded-lg h-24 animate-pulse" />
              ))
            ) : filings.length > 0 ? (
              filings.map((f) => <IntelCard key={f._id} filing={f} />)
            ) : (
              <p className="text-gray-600 text-sm">
                No filings in database yet. Run{' '}
                <code className="bg-gray-800 px-1 rounded">python agent/main.py</code> to start.
              </p>
            )}
          </div>
        </section>

        {/* Full Filings Table */}
        <section>
          <h2 className="text-gray-400 text-xs font-semibold uppercase tracking-widest mb-4">
            All Filings
          </h2>
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            {loading ? (
              <div className="h-40 animate-pulse" />
            ) : (
              <FilingsTable filings={filings} />
            )}
          </div>
        </section>
      </div>

      <footer className="border-t border-gray-800 mt-16 px-6 py-4 text-center text-gray-600 text-xs">
        Gulf SWF Filing Intelligence · Bright Data × lablab.ai Hackathon · Zulfiqar Ali Mir
      </footer>
    </main>
  )
}
