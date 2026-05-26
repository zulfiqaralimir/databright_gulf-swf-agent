interface SWFCardProps {
  swf_name: string
  count: number
  latest_date: string
  swf_emoji: string
  swf_country: string
}

export default function SWFCard({ swf_name, count, latest_date, swf_emoji, swf_country }: SWFCardProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-2xl">{swf_emoji}</span>
        <div>
          <h3 className="font-bold text-white text-sm leading-tight">{swf_name}</h3>
          <p className="text-gray-400 text-xs">{swf_country}</p>
        </div>
      </div>
      <p className="text-3xl font-bold text-blue-400">{count}</p>
      <p className="text-gray-500 text-xs mt-1">filings tracked</p>
      {latest_date && (
        <p className="text-gray-600 text-xs mt-2 truncate">Latest: {latest_date}</p>
      )}
    </div>
  )
}
