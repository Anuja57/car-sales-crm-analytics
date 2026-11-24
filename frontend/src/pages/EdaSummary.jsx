import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import ChartCard from '../components/ChartCard'

export default function EdaSummary({ data }) {
  const files = [
    { label: 'Leads',       eda: data.leads },
    { label: 'Calls',       eda: data.calls },
    { label: 'Test Drives', eda: data.testdrives },
  ]

  return (
    <div>
      <h2 className="text-xl font-bold text-slate-900 mb-1">EDA & Data Quality Summary</h2>
      <p className="text-sm text-slate-500 mb-6">
        Data quality check performed on your uploaded files before analysis.
      </p>
      {files.map(({ label, eda }) => (
        <ChartCard key={label} title={`${label} — ${eda.total_rows.toLocaleString()} rows x ${eda.total_cols} columns`} className="mb-4">
          <div className="grid grid-cols-3 gap-4 mb-4 text-center">
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Rows</p>
              <p className="text-xl font-bold text-slate-800">{eda.total_rows.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Columns</p>
              <p className="text-xl font-bold text-slate-800">{eda.total_cols}</p>
            </div>
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Duplicates Removed</p>
              <p className="text-xl font-bold text-slate-800">{eda.duplicates}</p>
            </div>
          </div>

          {Object.keys(eda.missing_pct || {}).length > 0 ? (
            <>
              <p className="text-xs font-semibold text-slate-500 mb-2">Top Columns with Missing Data:</p>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart
                  data={Object.entries(eda.missing_pct)
                    .sort((a, b) => b[1] - a[1]).slice(0, 15)
                    .map(([col, pct]) => ({ col, pct }))}
                  margin={{ bottom: 70 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="col" tick={{ fontSize: 9 }} angle={-40} textAnchor="end" />
                  <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                  <Tooltip formatter={v => [`${v}%`, 'Missing']} />
                  <Bar dataKey="pct" name="Missing %" radius={[3, 3, 0, 0]}>
                    {Object.keys(eda.missing_pct).slice(0, 15).map((_, i) => (
                      <Cell key={i} fill={`hsl(${i * 8}, 80%, 55%)`} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </>
          ) : (
            <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded px-3 py-2">
              No missing data detected in this file.
            </p>
          )}
        </ChartCard>
      ))}
    </div>
  )
}
