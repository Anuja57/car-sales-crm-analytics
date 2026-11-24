import { useState } from 'react'
import { analyzeFiles } from './api/client'
import FileSlot             from './components/FileSlot'
import AgentPerformance     from './pages/AgentPerformance'
import CustomerConnectivity from './pages/CustomerConnectivity'
import LeadConversion       from './pages/LeadConversion'
import EdaSummary           from './pages/EdaSummary'

const TABS = ['Agent Performance', 'Customer Connectivity', 'Lead Conversion', 'EDA Summary']

export default function App() {
  const [files,     setFiles]     = useState({ leads: null, calls: null, td: null })
  const [apiKey,    setApiKey]    = useState('')
  const [results,   setResults]   = useState(null)
  const [activeTab, setActiveTab] = useState(0)
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState(null)

  function setFile(key, f) { setFiles(p => ({ ...p, [key]: f })) }

  async function runAnalysis() {
    if (!files.leads || !files.calls || !files.td) return
    setLoading(true)
    setError(null)
    setResults(null)
    try {
      const data = await analyzeFiles(files.leads, files.calls, files.td)
      setResults(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setFiles({ leads: null, calls: null, td: null })
    setResults(null)
    setError(null)
    setActiveTab(0)
  }

  const allUploaded = files.leads && files.calls && files.td

  return (
    <div className="flex h-screen overflow-hidden font-sans">

      {/* Sidebar */}
      <aside className="w-64 shrink-0 bg-[rgb(240,253,244)] border-r border-slate-200
                        flex flex-col overflow-y-auto">
        <div className="px-5 py-5 border-b border-green-200">
          <h1 className="text-base font-bold text-green-900">CRM Analytics AI</h1>
        </div>

        <div className="px-5 py-5 flex-1">
          <p className="text-[10px] font-semibold text-green-700 uppercase tracking-widest mb-3">
            Upload Data Files
          </p>
          <FileSlot label="Leads CSV"
            file={files.leads}
            onSelect={f => setFile('leads', f)}
            onRemove={() => setFile('leads', null)} />
          <FileSlot label="Sales Completed Calls CSV"
            file={files.calls}
            onSelect={f => setFile('calls', f)}
            onRemove={() => setFile('calls', null)} />
          <FileSlot label="Test Drive Details CSV"
            file={files.td}
            onSelect={f => setFile('td', f)}
            onRemove={() => setFile('td', null)} />

          <hr className="border-green-200 my-4" />

          <p className="text-[10px] font-semibold text-green-700 uppercase tracking-widest mb-2">
            AI Insights (Optional)
          </p>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="sk-ant-..."
            className="w-full text-xs border border-green-200 rounded px-3 py-2
                       bg-white text-slate-700 placeholder-slate-400 focus:outline-none
                       focus:border-blue-400"
          />

          <hr className="border-green-200 my-4" />

          <button
            onClick={runAnalysis}
            disabled={!allUploaded || loading}
            className="w-full bg-blue-600 text-white text-sm font-semibold rounded py-2
                       hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed mb-2"
          >
            {loading ? 'Analysing...' : 'Run Analysis'}
          </button>

          <button
            onClick={reset}
            className="w-full border border-green-300 text-green-800 text-sm font-medium
                       rounded py-2 hover:bg-green-100"
          >
            Reset / Clear
          </button>
        </div>

        <div className="px-5 py-4 border-t border-green-200">
          <p className="text-[10px] text-green-600 leading-5">
            <strong>Pipeline stages:</strong><br />
            1. Load &amp; Validate<br />
            2. EDA &amp; Clean<br />
            3. Feature Engineering<br />
            4. ML Analysis<br />
            5. Dashboard Render
          </p>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col overflow-hidden bg-slate-100">

        {/* Header */}
        <header className="bg-[rgb(240,253,244)] border-b border-slate-200 px-8 py-4 shrink-0">
          <h1 className="text-xl font-bold text-green-900 tracking-tight">
            AI-Based CRM Analytics Dashboard
          </h1>
        </header>

        <div className="flex-1 overflow-y-auto px-8 py-6">

          {/* Welcome */}
          {!results && !loading && (
            <div className="bg-white border border-slate-200 rounded p-10 text-center max-w-2xl mx-auto mt-10">
              <h2 className="text-lg font-bold text-blue-700 mb-3">Welcome to CRM Analytics AI</h2>
              <p className="text-sm text-slate-500 mb-6">
                Upload your three CRM CSV files in the sidebar to start the AI-driven analysis pipeline.
              </p>
              <div className="flex justify-center gap-6 flex-wrap">
                {[
                  ['Agent Performance',     'Ranks agents by calls, lead quality & test-drive results',    '#EFF6FF', '#1E40AF'],
                  ['Customer Connectivity', 'Evaluates engagement, reach & call patterns',                 '#F0FDF4', '#166534'],
                  ['Lead Conversion',       'Scores leads & spots highest-potential opportunities',       '#FFF7ED', '#92400E'],
                ].map(([title, desc, bg, color]) => (
                  <div key={title} style={{ background: bg }} className="rounded p-4 w-44 text-left">
                    <p style={{ color }} className="text-xs font-bold mb-1">{title}</p>
                    <p className="text-xs text-slate-500">{desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="flex items-center justify-center h-48">
              <p className="text-slate-500 text-sm animate-pulse">Running analysis pipeline...</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded px-4 py-3 text-sm text-red-700 mb-4">
              {error}
            </div>
          )}

          {/* Results */}
          {results && (
            <>
              {/* Summary strip */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                {[
                  ['Leads Loaded',       results.load_info.leads_rows.toLocaleString()],
                  ['Calls Loaded',       results.load_info.calls_rows.toLocaleString()],
                  ['Test Drive Records', results.load_info.testdrive_rows.toLocaleString()],
                ].map(([label, value]) => (
                  <div key={label}
                       className="bg-white border border-slate-200 rounded px-4 py-3
                                  border-t-[3px] border-t-blue-600">
                    <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">{label}</p>
                    <p className="text-xl font-bold text-slate-800 mt-1">{value}</p>
                  </div>
                ))}
              </div>

              {/* Tabs */}
              <div className="flex border-b border-slate-200 mb-6 bg-white rounded-t">
                {TABS.map((tab, i) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(i)}
                    className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors
                      ${activeTab === i
                        ? 'border-blue-600 text-blue-700'
                        : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {activeTab === 0 && <AgentPerformance     data={results.agent}       apiKey={apiKey} />}
              {activeTab === 1 && <CustomerConnectivity data={results.connectivity} apiKey={apiKey} />}
              {activeTab === 2 && <LeadConversion       data={results.conversion}   apiKey={apiKey} />}
              {activeTab === 3 && <EdaSummary           data={results.eda} />}
            </>
          )}
        </div>
      </main>
    </div>
  )
}
