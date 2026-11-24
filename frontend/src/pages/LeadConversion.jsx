import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell,
  FunnelChart, Funnel, LabelList,
  ResponsiveContainer,
} from 'recharts'
import KPICard        from '../components/KPICard'
import ChartCard      from '../components/ChartCard'
import AIInsightPanel from '../components/AIInsightPanel'
import { getConversionInsights } from '../api/client'

const TIER_COLORS   = { 'High Potential': '#16A34A', 'Medium Potential': '#D97706', 'Low Potential': '#DC2626' }
const FUNNEL_COLORS = ['#2563EB', '#0891B2', '#16A34A', '#D97706']

export default function LeadConversion({ data, apiKey }) {
  const [insight, setInsight] = useState(null)
  const { funnel, source_stats, model_stats, feature_importance, score_tiers,
          status_dist, td_dist, top_leads, prob_dist } = data

  const total     = funnel['Total Leads'] || 0
  const converted = funnel['Converted / Closed'] || 0
  const tdTaken   = funnel['Test Drive Taken'] || 0
  const highPot   = funnel['High Potential (Remaining)'] || 0
  const convRate  = total ? (converted / total * 100).toFixed(1) : 0
  const tdRate    = total ? (tdTaken   / total * 100).toFixed(1) : 0
  const avgProb   = prob_dist.length
    ? (prob_dist.reduce((s, r) => s + r.conversion_prob, 0) / prob_dist.length * 100).toFixed(1)
    : 0

  const funnelData = Object.entries(funnel).map(([name, value], i) => ({ name, value, fill: FUNNEL_COLORS[i] }))
  const tierData   = Object.entries(score_tiers).map(([name, value]) => ({ name, value }))
  const fiData     = Object.entries(feature_importance)
    .map(([k, v]) => ({ name: k.replace(/_enc|_/g, ' ').trim(), value: parseFloat(v.toFixed(3)) }))
    .sort((a, b) => a.value - b.value)

  async function generateInsight() {
    const text = await getConversionInsights(funnel, source_stats, model_stats, score_tiers, apiKey)
    setInsight(text)
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Lead Conversion Analysis</h2>
      <p className="text-sm text-slate-500 mb-6">
        Scores each lead's conversion probability based on test-drive behaviour, source, vehicle interest and lead age.
      </p>

      <div className="grid grid-cols-5 gap-4 mb-6">
        <KPICard label="Total Leads"           value={total.toLocaleString()} />
        <KPICard label="Converted / Closed"    value={converted.toLocaleString()} delta={`${convRate}% conversion rate`} />
        <KPICard label="Test Drives Taken"     value={tdTaken.toLocaleString()} delta={`${tdRate}% of leads`} />
        <KPICard label="High-Potential Leads"  value={highPot.toLocaleString()} delta="Unconverted — act now" />
        <KPICard label="Avg Conv. Probability" value={`${avgProb}%`} />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Lead Conversion Funnel">
          <ResponsiveContainer width="100%" height={300}>
            <FunnelChart>
              <Tooltip />
              <Funnel dataKey="value" data={funnelData} isAnimationActive>
                <LabelList position="center" fill="#fff" fontSize={12} fontWeight={600}
                           formatter={(v, e) => `${e?.name || ''}: ${v}`} />
                {funnelData.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Funnel>
            </FunnelChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="ML Score Tier Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={tierData} dataKey="value" nameKey="name"
                   cx="50%" cy="50%" innerRadius={65} outerRadius={105}
                   label={({ name, percent }) => `${name.split(' ')[0]} ${(percent * 100).toFixed(0)}%`}
              >
                {tierData.map((e, i) => <Cell key={i} fill={TIER_COLORS[e.name] || '#94A3B8'} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Total Leads by Source">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={source_stats} margin={{ bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="source_name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="total" fill="#2563EB" radius={[3, 3, 0, 0]} name="Leads" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Conversion Rate by Source (%)">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={[...source_stats].sort((a, b) => b.conversion_rate - a.conversion_rate)}
              margin={{ bottom: 60 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="source_name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={v => [`${v}%`, 'Conv. Rate']} />
              <Bar dataKey="conversion_rate" fill="#16A34A" radius={[3, 3, 0, 0]} name="Conv. Rate %" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Leads per Model">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={model_stats} margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="model_name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="total" fill="#2563EB" radius={[3, 3, 0, 0]} name="Leads" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Key Conversion Drivers">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={fiData} layout="vertical" margin={{ left: 20, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563EB" radius={[0, 3, 3, 0]} name="Importance" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Lead Status Breakdown">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={Object.entries(status_dist).map(([name, value]) => ({ name, value }))}
                dataKey="value" nameKey="name"
                cx="50%" cy="50%" innerRadius={55} outerRadius={90}
                label={({ name, percent }) => `${name.split('/')[0]} ${(percent * 100).toFixed(0)}%`}
              >
                {Object.keys(status_dist).map((_, i) => (
                  <Cell key={i} fill={['#16A34A', '#2563EB'][i % 2]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Test Drive Taken vs Not">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={Object.entries(td_dist).map(([name, value]) => ({ name, value }))}
                dataKey="value" nameKey="name"
                cx="50%" cy="50%" innerRadius={55} outerRadius={90}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {Object.keys(td_dist).map((_, i) => (
                  <Cell key={i} fill={['#0891B2', '#D97706', '#94A3B8'][i % 3]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Top High-Potential Leads (Unconverted)" className="mb-4 overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-200">
              {['Lead ID','Model','Source','Lead Type','Test Drive','Age (Days)','Conv. Prob.','Tier'].map(h => (
                <th key={h} className="text-left py-2 px-2 font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {top_leads.map((l, i) => (
              <tr key={i} className="border-b border-slate-100 bg-green-50">
                <td className="py-1.5 px-2">{l.id}</td>
                <td className="py-1.5 px-2">{l.model_name}</td>
                <td className="py-1.5 px-2">{l.source_name}</td>
                <td className="py-1.5 px-2">{l.lead_type_label}</td>
                <td className="py-1.5 px-2">{l.td_status_label}</td>
                <td className="py-1.5 px-2">{l.lead_age_days}</td>
                <td className="py-1.5 px-2 font-semibold">{(l.conversion_prob * 100).toFixed(1)}%</td>
                <td className="py-1.5 px-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-green-100 text-green-800">
                    {l.score_tier}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </ChartCard>

      <AIInsightPanel apiKey={apiKey} onGenerate={generateInsight} cachedInsight={insight} />
    </div>
  )
}
