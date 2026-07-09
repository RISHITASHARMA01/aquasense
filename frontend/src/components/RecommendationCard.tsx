import type { IrrigationOutlook, Recommendation } from '../types';

function outlookLabel(outlook: IrrigationOutlook | null | undefined, todayNeedsIrrigation: boolean): string | null {
  if (!outlook || todayNeedsIrrigation) return null;
  if (!outlook.next_irrigation_date) return `No irrigation expected in the next ${outlook.projection.length} days`;
  const days = outlook.projection.findIndex((p) => p.date === outlook.next_irrigation_date) + 1;
  return `Next irrigation likely in ~${days} day${days === 1 ? '' : 's'} (${outlook.next_irrigation_date})`;
}

export default function RecommendationCard({ rec, outlook }: { rec: Recommendation; outlook?: IrrigationOutlook | null }) {
  const outlookText = outlookLabel(outlook, rec.needs_irrigation);

  return (
    <div
      className={`rounded-xl border p-5 shadow-sm ${
        rec.needs_irrigation ? 'bg-amber-50 border-amber-200' : 'bg-emerald-50 border-emerald-200'
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-slate-800">Today's Recommendation</h3>
        <span className="text-xs text-slate-500">{rec.date}</span>
      </div>

      {rec.needs_irrigation ? (
        <div className="mb-3">
          <p className="text-3xl font-bold text-amber-700">{rec.gross_depth_mm.toFixed(1)} mm</p>
          <p className="text-sm text-amber-800">≈ {rec.duration_hours.toFixed(1)} hours of irrigation needed today</p>
        </div>
      ) : (
        <div className="mb-3">
          <p className="text-3xl font-bold text-emerald-700">No irrigation needed</p>
          <p className="text-sm text-emerald-800">Soil moisture is sufficient for today</p>
        </div>
      )}

      <p className="text-sm text-slate-600 mb-4">{rec.reasoning}</p>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
        <Stat label="ET₀" value={`${rec.et0_mm.toFixed(1)} mm`} />
        <Stat label="ETc" value={`${rec.etc_mm.toFixed(1)} mm`} />
        <Stat label="Kc" value={rec.kc.toFixed(2)} />
        <Stat label="Growth stage" value={rec.growth_stage} capitalize />
      </div>

      {outlookText && (
        <p className="text-xs font-medium text-slate-600 bg-white/60 rounded-lg px-3 py-2 mt-3 inline-block">
          📅 {outlookText}
        </p>
      )}

      {rec.used_radiation_fallback && (
        <p className="text-xs text-slate-400 mt-3">
          ⓘ Solar radiation data unavailable for this date — ET₀ used the Hargreaves temperature-based estimate
          instead of measured radiation.
        </p>
      )}
    </div>
  );
}

function Stat({ label, value, capitalize }: { label: string; value: string; capitalize?: boolean }) {
  return (
    <div className="bg-white/60 rounded-lg py-2">
      <p className={`text-sm font-semibold text-slate-700 ${capitalize ? 'capitalize' : ''}`}>{value}</p>
      <p className="text-xs text-slate-500">{label}</p>
    </div>
  );
}
