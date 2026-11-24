import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer,
} from 'recharts'
import KPICard        from '../components/KPICard'
import ChartCard      from '../components/ChartCard'
import AIInsightPanel from '../components/AIInsightPanel'
import { getAgentInsights } from '../api/client'

const TIER_COLORS = { High: '#16A34A', Medium: '#D97706', Low: '#DC2626' }

export default function AgentPerformance({ data, apiKey }) {
  const [insight, setInsight] = useState(null)
  const metrics = data.metrics

  const topAgent   = metrics[0]
  const avgScore   = (metrics.reduce((s, m) => s + m.composite_score, 0) / metrics.length).toFixed(1)
  const highCount  = metrics.filter(m => m.tier === 'High').length
  const totalCalls = metrics.reduce((s, m) => s + m.total_calls, 0)
  const tierDist   = metrics.reduce((acc, m) => { acc[m.tier] = (acc[m.tier] || 0) + 1; return acc }, {})
  const tierData   = Object.entries(tierDist).map(([name, value]) => ({ name, value }))

  const ltData = metrics.map(m => ({
    name: m.agent_name,
    Hot:  m.hot_leads,
    Warm: m.warm_leads,
    Cold: m.cold_leads,
  }))

  async function generateInsight() {
    const text = await getAgentInsights(metrics, tierDist, parseFloat(avgScore), apiKey)
    setInsight(text)
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-slate-900 mb-6">Agent Performance Analysis</h2>

      <div className="grid grid-cols-5 gap-4 mb-6">
        <KPICard label="Total Agents"          value={metrics.length} />
        <KPICard label="Total Calls Analysed"  value={totalCalls.toLocaleString()} />
        <KPICard label="Top Performer"         value={topAgent?.agent_name} />
        <KPICard label="Avg Performance Score" value={`${avgScore}/100`} />
        <KPICard label="High-Tier Agents"      value={`${highCount}/${metrics.length}`} />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Agent Performance Score Ranking">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart
              data={[...metrics].sort((a, b) => a.composite_score - b.composite_score)}
              layout="vertical" margin={{ left: 20, right: 30 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
              <YAxis dataKey="agent_name" type="category" width={90} tick={{ fontSize: 11 }} />
              <Tooltip formatter={v => [`${v}/100`, 'Score']} />
              <Bar dataKey="composite_score" radius={[0, 3, 3, 0]}>
                {[...metrics].sort((a, b) => a.composite_score - b.composite_score).map((m, i) => (
                  <Cell key={i} fill={TIER_COLORS[m.tier] || '#2563EB'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Performance Tier Distribution">
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie data={tierData} dataKey="value" nameKey="name"
                   cx="50%" cy="50%" innerRadius={70} outerRadius={110}
                   label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {tierData.map((e, i) => (
                  <Cell key={i} fill={TIER_COLORS[e.name] || '#94A3B8'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Calls Handled per Agent">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={[...metrics].sort((a, b) => b.total_calls - a.total_calls)}
                      margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="agent_name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="total_calls" name="Calls" radius={[3, 3, 0, 0]}>
                {[...metrics].sort((a, b) => b.total_calls - a.total_calls).map((m, i) => (
                  <Cell key={i} fill={TIER_COLORS[m.tier] || '#2563EB'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Callback Scheduling Rate (%)">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={[...metrics].sort((a, b) => b.callback_rate - a.callback_rate)}
                      margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="agent_name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={v => [`${v}%`, 'Callback Rate']} />
              <Bar dataKey="callback_rate" name="Callback %" radius={[3, 3, 0, 0]}>
                {[...metrics].sort((a, b) => b.callback_rate - a.callback_rate).map((m, i) => (
                  <Cell key={i} fill={TIER_COLORS[m.tier] || '#2563EB'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Lead Type Handled per Agent" className="mb-4">
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={ltData} margin={{ top: 30, right: 10, left: 0, bottom: 70 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: 8 }} />
            <Bar dataKey="Hot"  stackId="a" fill="#DC2626" />
            <Bar dataKey="Warm" stackId="a" fill="#D97706" />
            <Bar dataKey="Cold" stackId="a" fill="#2563EB" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Agent Leaderboard" className="mb-4 overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-200">
              {['Rank','Agent','Tier','Score','Calls','Hot Lead %','Callback %','Test Drives','TD Completion %'].map(h => (
                <th key={h} className="text-left py-2 px-2 font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metrics.map((m, i) => {
              const bg = { High: 'bg-green-50', Medium: 'bg-yellow-50', Low: 'bg-red-50' }[m.tier] || ''
              return (
                <tr key={i} className={`border-b border-slate-100 ${bg}`}>
                  <td className="py-1.5 px-2 font-bold">{m.rank}</td>
                  <td className="py-1.5 px-2 font-medium">{m.agent_name}</td>
                  <td className="py-1.5 px-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold
                      ${m.tier === 'High'   ? 'bg-green-100 text-green-800' :
                        m.tier === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'}`}>
                      {m.tier}
                    </span>
                  </td>
                  <td className="py-1.5 px-2">{m.composite_score}</td>
                  <td className="py-1.5 px-2">{m.total_calls}</td>
                  <td className="py-1.5 px-2">{m.hot_lead_ratio}%</td>
                  <td className="py-1.5 px-2">{m.callback_rate}%</td>
                  <td className="py-1.5 px-2">{m.test_drives_assigned}</td>
                  <td className="py-1.5 px-2">{m.td_conversion_rate}%</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </ChartCard>

      <AIInsightPanel apiKey={apiKey} onGenerate={generateInsight} cachedInsight={insight} />
    </div>
  )
}
