export default function KPICard({ label, value, delta }) {
  return (
    <div className="bg-white border border-slate-200 border-t-[3px] border-t-blue-600
                    rounded p-4 min-h-[96px]">
      <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mb-1.5">
        {label}
      </p>
      <p className="text-2xl font-bold text-slate-900 tracking-tight">{value}</p>
      {delta && <p className="text-xs text-slate-500 mt-1">{delta}</p>}
    </div>
  )
}
