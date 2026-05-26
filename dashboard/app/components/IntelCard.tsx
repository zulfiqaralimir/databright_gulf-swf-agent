export interface Filing {
  _id: string
  swf_name: string
  swf_emoji: string
  swf_country: string
  company_name: string
  company_ticker: string | null
  filing_type: string
  filing_date: string
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
  action: string
  sector: string
  summary: string
  significance: 'HIGH' | 'MEDIUM' | 'LOW'
  key_insight: string
  ownership_percent: number | null
  filing_url: string
}

const SIGNAL_STYLES = {
  BULLISH: 'bg-green-500/20 text-green-400 border-green-500/30',
  BEARISH: 'bg-red-500/20 text-red-400 border-red-500/30',
  NEUTRAL: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

const SIGNIFICANCE_DOT = {
  HIGH: 'bg-red-400',
  MEDIUM: 'bg-yellow-400',
  LOW: 'bg-gray-500',
}

export default function IntelCard({ filing }: { filing: Filing }) {
  const signalStyle = SIGNAL_STYLES[filing.signal] ?? SIGNAL_STYLES.NEUTRAL
  const dotStyle = SIGNIFICANCE_DOT[filing.significance] ?? SIGNIFICANCE_DOT.LOW

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xl flex-shrink-0">{filing.swf_emoji}</span>
          <div className="min-w-0">
            <p className="text-gray-400 text-xs">{filing.swf_name}</p>
            <h3 className="text-white font-semibold truncate">
              {filing.company_name}
              {filing.company_ticker && (
                <span className="ml-1.5 text-gray-400 font-normal text-sm">
                  ({filing.company_ticker})
                </span>
              )}
            </h3>
          </div>
        </div>
        <div className="flex gap-2 flex-shrink-0 flex-wrap justify-end">
          <span className="text-xs bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded">
            {filing.filing_type}
          </span>
          <span className={`text-xs border px-2 py-0.5 rounded ${signalStyle}`}>
            {filing.signal}
          </span>
        </div>
      </div>

      {filing.key_insight && (
        <p className="mt-3 text-gray-300 text-sm leading-relaxed">{filing.key_insight}</p>
      )}

      <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-2">
          <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${dotStyle}`} />
          <span>{filing.sector}</span>
          {filing.action && <span>• {filing.action.replace('_', ' ')}</span>}
          {filing.ownership_percent != null && (
            <span>• {filing.ownership_percent}% owned</span>
          )}
        </div>
        <span className="flex-shrink-0">{filing.filing_date}</span>
      </div>

      {filing.filing_url && (
        <a
          href={filing.filing_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 inline-block text-xs text-blue-400 hover:text-blue-300 transition-colors"
        >
          View SEC filing →
        </a>
      )}
    </div>
  )
}
