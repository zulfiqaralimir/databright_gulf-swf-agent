import type { Filing } from './IntelCard'

export default function FilingsTable({ filings }: { filings: Filing[] }) {
  if (!filings.length) {
    return (
      <div className="text-center text-gray-500 py-10 text-sm">
        No filings yet. Run <code className="bg-gray-700 px-1 rounded">python agent/main.py</code> to start monitoring.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-gray-400 text-xs uppercase tracking-wider border-b border-gray-700">
            <th className="text-left py-3 px-4">SWF</th>
            <th className="text-left py-3 px-4">Company</th>
            <th className="text-left py-3 px-4">Type</th>
            <th className="text-left py-3 px-4">Signal</th>
            <th className="text-right py-3 px-4">Ownership</th>
            <th className="text-right py-3 px-4">Date</th>
            <th className="text-right py-3 px-4">Filing</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-700/50">
          {filings.map((f) => (
            <tr key={f._id} className="hover:bg-gray-700/30 transition-colors">
              <td className="py-3 px-4 whitespace-nowrap">
                <span className="mr-1.5">{f.swf_emoji}</span>
                <span className="text-gray-300 text-xs">{f.swf_name}</span>
              </td>
              <td className="py-3 px-4">
                <span className="text-white font-medium">{f.company_name}</span>
                {f.company_ticker && (
                  <span className="ml-1 text-gray-400 text-xs">({f.company_ticker})</span>
                )}
              </td>
              <td className="py-3 px-4 whitespace-nowrap">
                <span className="bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded text-xs">
                  {f.filing_type}
                </span>
              </td>
              <td className="py-3 px-4 whitespace-nowrap">
                <span className={`px-2 py-0.5 rounded text-xs ${
                  f.signal === 'BULLISH'
                    ? 'bg-green-500/20 text-green-400'
                    : f.signal === 'BEARISH'
                    ? 'bg-red-500/20 text-red-400'
                    : 'bg-gray-500/20 text-gray-400'
                }`}>
                  {f.signal}
                </span>
              </td>
              <td className="py-3 px-4 text-right text-gray-300 whitespace-nowrap">
                {f.ownership_percent != null ? `${f.ownership_percent}%` : '—'}
              </td>
              <td className="py-3 px-4 text-right text-gray-400 whitespace-nowrap text-xs">
                {f.filing_date ?? '—'}
              </td>
              <td className="py-3 px-4 text-right whitespace-nowrap">
                {f.filing_url ? (
                  <a
                    href={f.filing_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 text-xs transition-colors"
                  >
                    View →
                  </a>
                ) : (
                  <span className="text-gray-600 text-xs">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
