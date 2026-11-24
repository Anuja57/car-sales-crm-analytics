import { useState } from 'react'

export default function AIInsightPanel({ apiKey, onGenerate, cachedInsight }) {
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    try {
      await onGenerate()
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-6">
      <hr className="border-slate-200 mb-6" />
      <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mb-4">
        AI-Generated Executive Insights
      </h3>

      {!apiKey && (
        <p className="text-sm text-slate-500 bg-slate-50 border border-slate-200 rounded px-4 py-3">
          Enter your Anthropic API key in the sidebar to unlock AI insights.
        </p>
      )}

      {apiKey && !cachedInsight && (
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded
                     hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : 'Generate AI Insights'}
        </button>
      )}

      {error && (
        <p className="text-sm text-red-600 mt-2">{error}</p>
      )}

      {cachedInsight && (
        <div
          className="bg-white border border-slate-200 border-l-[3px] border-l-blue-600
                     rounded p-6 text-sm text-slate-700 leading-7 whitespace-pre-wrap"
        >
          {cachedInsight}
        </div>
      )}
    </div>
  )
}
