import { useRef } from 'react'

export default function FileSlot({ label, file, onSelect, onRemove }) {
  const inputRef = useRef()

  if (file) {
    return (
      <div className="mb-4">
        <p className="text-xs font-semibold text-green-800 uppercase tracking-wide mb-1">{label}</p>
        <div className="flex items-center gap-2 bg-green-100 border border-green-200 rounded-md px-3 py-2">
          <span className="flex-1 text-xs font-medium text-green-900 truncate min-w-0" title={file.name}>
            {file.name}
          </span>
          <button
            onClick={onRemove}
            className="shrink-0 w-5 h-5 flex items-center justify-center rounded-full
                       bg-green-200 hover:bg-green-300 text-green-800 hover:text-green-900
                       text-[10px] font-bold transition-colors"
            title="Remove file"
          >
            ✕
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="mb-4">
      <label className="block text-xs font-semibold text-green-800 uppercase tracking-wide mb-1">
        {label}
      </label>
      <button
        onClick={() => inputRef.current.click()}
        className="w-full border-2 border-dashed border-green-300 rounded px-3 py-2
                   text-xs text-green-700 hover:border-green-500 hover:bg-green-50
                   transition-colors text-left"
      >
        Click to upload CSV
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={e => e.target.files[0] && onSelect(e.target.files[0])}
      />
    </div>
  )
}
