interface Row {
  name: string;
  'AquaSense (mm)': number;
  'Fixed Schedule (mm)': number;
}

export default function WaterSavingsChart({ rows }: { rows: Row[] }) {
  const maxValue = Math.max(1, ...rows.flatMap((r) => [r['AquaSense (mm)'], r['Fixed Schedule (mm)']]));

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      <h3 className="font-semibold text-slate-800 mb-1">Water Applied: AquaSense vs. Fixed Schedule</h3>
      <div className="flex items-center gap-4 text-xs text-slate-500 mb-5">
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-sm bg-aqua-600 inline-block" /> AquaSense
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-sm bg-slate-300 inline-block" /> Fixed Schedule
        </span>
      </div>
      <div className="space-y-5">
        {rows.map((row) => (
          <div key={row.name}>
            <p className="text-sm font-medium text-slate-700 mb-1.5">{row.name}</p>
            <div className="space-y-1">
              <BarRow value={row['AquaSense (mm)']} max={maxValue} colorClass="bg-aqua-600" />
              <BarRow value={row['Fixed Schedule (mm)']} max={maxValue} colorClass="bg-slate-300" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function BarRow({ value, max, colorClass }: { value: number; max: number; colorClass: string }) {
  const widthPercent = Math.max(2, (value / max) * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-slate-100 rounded h-5 overflow-hidden">
        <div className={`h-5 rounded ${colorClass}`} style={{ width: `${widthPercent}%` }} />
      </div>
      <span className="text-xs text-slate-500 w-16 text-right">{Math.round(value)}mm</span>
    </div>
  );
}
