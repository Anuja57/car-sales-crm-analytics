import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell,
  ComposedChart, Line,
  ResponsiveContainer,
} from 'recharts'
import KPICard        from '../components/KPICard'
import ChartCard      from '../components/ChartCard'
import AIInsightPanel from '../components/AIInsightPanel'
import { getConnectivityInsights } from '../api/client'

const SEG_COLORS  = { 'Highly Engaged': '#16A34A', 'Moderately Engaged': '#D97706', 'Low Engagement': '#DC2626' }
const TYPE_COLORS = { Hot: '#DC2626', Warm: '#D97706', Cold: '#2563EB', Unknown: '#94A3B8' }

export default function CustomerConnectivity({ data, apiKey }) {
  const [insight, setInsight] = useState(null)
  const { segments, avg_calls, avg_cb_rate, time_series, location_stats, lead_type_dist, model_interest } = data

  const segData       = Object.entries(segments).map(([name, value]) => ({ name, value }))
  const totalLTD      = lead_type_dist.reduce((s, r) => s + r.count, 0)
  const hotPct        = ((lead_type_dist.find(r => r.lead_type === 'Hot')?.count || 0) / (totalLTD || 1) * 100).toFixed(1)
  const highlyEngaged = segments['Highly Engaged'] || 0

  async function generateInsight() {
    const text = await getConnectivityInsights(segments, avg_calls, avg_cb_rate, lead_type_dist, apiKey)
    setInsight(text)
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Customer Connectivity Analysis</h2>
      <p className="text-sm text-slate-500 mb-6">
        Evaluates customer engagement using call frequency, callback rates and lead quality signals.
      </p>

      <div className="grid grid-cols-5 gap-4 mb-6">
        <KPICard label="Unique Customers"   value={Object.values(segments).reduce((s, v) => s + v, 0).toLocaleString()} />
        <KPICard label="Avg Calls/Customer" value={avg_calls.toFixed(1)} />
        <KPICard label="Avg Callback Rate"  value={`${avg_cb_rate.toFixed(1)}%`} />
        <KPICard label="Highly Engaged"     value={highlyEngaged} />
        <KPICard label="Hot Lead Share"     value={`${hotPct}%`} />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Customer Engagement Segments">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={segData} dataKey="value" nameKey="name"
                   cx="50%" cy="50%" innerRadius={65} outerRadius={105}
                   label={({ name, percent }) => `${name.split(' ')[0]} ${(percent * 100).toFixed(0)}%`}
              >
                {segData.map((e, i) => <Cell key={i} fill={SEG_COLORS[e.name] || '#94A3B8'} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Lead Type Distribution (Calls)">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={lead_type_dist} dataKey="count" nameKey="lead_type"
                   cx="50%" cy="50%" innerRadius={65} outerRadius={105}
                   label={({ lead_type, percent }) => `${lead_type} ${(percent * 100).toFixed(0)}%`}
              >
                {lead_type_dist.map((e, i) => <Cell key={i} fill={TYPE_COLORS[e.lead_type] || '#94A3B8'} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Daily Call Volume and Lead Type Trend" className="mb-4">
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={time_series}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="call_date" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="cold_calls" stackId="a" fill="#93C5FD" name="Cold" />
            <Bar dataKey="warm_calls" stackId="a" fill="#FCD34D" name="Warm" />
            <Bar dataKey="hot_calls"  stackId="a" fill="#F87171" name="Hot" radius={[3, 3, 0, 0]} />
            <Line dataKey="call_count" stroke="#1E40AF" strokeWidth={2.5} dot={{ r: 4 }} name="Total" />
          </ComposedChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <ChartCard title="Call Volume by Showroom Location">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={location_stats.slice(0, 10)} margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="location_label" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="calls" fill="#2563EB" radius={[3, 3, 0, 0]} name="Calls" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Customer Interest by Car Model">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={model_interest} margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="model" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="customers" fill="#0891B2" radius={[3, 3, 0, 0]} name="Customers" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <AIInsightPanel apiKey={apiKey} onGenerate={generateInsight} cachedInsight={insight} />
    </div>
  )
}
