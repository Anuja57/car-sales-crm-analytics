export default function ChartCard({ title, children, className = '' }) {
  return (
    <div className={`bg-white border border-slate-200 rounded p-4 ${className}`}>
      {title && (
        <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mb-4">
          {title}
        </h3>
      )}
      {children}
    </div>
  )
}
