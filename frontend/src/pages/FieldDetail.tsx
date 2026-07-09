import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import * as api from '../api/fields';
import type { Field, History, Forecast, Recommendation } from '../types';
import RecommendationCard from '../components/RecommendationCard';
import MoistureChart from '../components/MoistureChart';
import WeatherStrip from '../components/WeatherStrip';
import PlantCropForm from '../components/PlantCropForm';

export default function FieldDetail() {
  const { fieldId } = useParams();
  const id = Number(fieldId);
  const navigate = useNavigate();

  const [field, setField] = useState<Field | null>(null);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [history, setHistory] = useState<History | null>(null);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [recError, setRecError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const fetchedField = await api.getField(id);
    setField(fetchedField);
    api.getForecast(id).then(setForecast).catch(() => {});

    const hasActiveCrop = fetchedField.crops.some((c) => c.is_active);
    if (hasActiveCrop) {
      setRecError('');
      Promise.all([api.getRecommendation(id), api.getHistory(id, 30)])
        .then(([rec, hist]) => {
          setRecommendation(rec);
          setHistory(hist);
        })
        .catch((err) => setRecError(err?.response?.data?.detail || 'Could not load recommendation'));
    }
    setLoading(false);
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleDelete() {
    if (!confirm(`Delete field "${field?.name}"? This cannot be undone.`)) return;
    await api.deleteField(id);
    navigate('/');
  }

  if (loading || !field) {
    return <p className="text-slate-500">Loading...</p>;
  }

  const activeCrop = field.crops.find((c) => c.is_active);

  return (
    <div className="space-y-6">
      <div>
        <Link to="/" className="text-sm text-aqua-600 mb-2 inline-block">
          ← Back to dashboard
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">{field.name}</h1>
            <p className="text-sm text-slate-500 capitalize">
              {field.soil_type.replace('_', ' ')} soil · {field.area_hectares} ha · {field.irrigation_method}{' '}
              irrigation · ({field.latitude.toFixed(3)}, {field.longitude.toFixed(3)})
            </p>
          </div>
          <div className="flex gap-2">
            <Link
              to={`/fields/${field.id}/edit`}
              className="text-sm border border-slate-300 px-3 py-1.5 rounded-lg hover:bg-slate-50"
            >
              Edit
            </Link>
            <button
              onClick={handleDelete}
              className="text-sm border border-red-200 text-red-600 px-3 py-1.5 rounded-lg hover:bg-red-50"
            >
              Delete
            </button>
          </div>
        </div>
      </div>

      {!activeCrop ? (
        <PlantCropForm fieldId={field.id} onPlanted={load} />
      ) : (
        <>
          <p className="text-sm text-slate-500">
            Growing <span className="font-medium text-slate-700">{activeCrop.crop.name}</span> since{' '}
            {activeCrop.planting_date}
          </p>

          {recError ? (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-4">{recError}</p>
          ) : recommendation ? (
            <RecommendationCard rec={recommendation} />
          ) : (
            <p className="text-slate-500">Loading recommendation...</p>
          )}

          {history && recommendation && <MoistureChart points={history.points} tawMm={recommendation.taw_mm} />}
        </>
      )}

      {forecast && <WeatherStrip points={forecast.points} />}
    </div>
  );
}
