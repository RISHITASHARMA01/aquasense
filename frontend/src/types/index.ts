export interface Crop {
  id: number;
  name: string;
  root_depth_m: number;
  depletion_fraction_p: number;
  stages: string[];
  stage_lengths_days: number[];
  kc_values: number[];
}

export interface FieldCrop {
  id: number;
  crop_id: number;
  planting_date: string;
  current_depletion_mm: number;
  is_active: boolean;
  crop: Crop;
}

export interface Field {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  soil_type: string;
  area_hectares: number;
  irrigation_method: string;
  crops: FieldCrop[];
}

export interface Recommendation {
  field_id: number;
  date: string;
  et0_mm: number;
  etc_mm: number;
  kc: number;
  growth_stage: string;
  used_radiation_fallback: boolean;
  depletion_mm: number;
  taw_mm: number;
  raw_mm: number;
  needs_irrigation: boolean;
  net_depth_mm: number;
  gross_depth_mm: number;
  duration_hours: number;
  reasoning: string;
}

export interface HistoryPoint {
  date: string;
  et0_mm: number;
  etc_mm: number;
  depletion_mm: number;
  precipitation_mm: number;
  irrigated_mm: number;
}

export interface History {
  field_id: number;
  points: HistoryPoint[];
}

export interface ForecastPoint {
  date: string;
  t_max_c: number;
  t_min_c: number;
  precipitation_mm: number;
}

export interface Forecast {
  field_id: number;
  points: ForecastPoint[];
}

export interface OutlookProjectionPoint {
  date: string;
  projected_depletion_mm: number;
  needs_irrigation: boolean;
}

export interface IrrigationOutlook {
  field_id: number;
  raw_mm: number;
  next_irrigation_date: string | null;
  projection: OutlookProjectionPoint[];
}

export interface WaterSavings {
  field_id: number;
  days_simulated: number;
  aquasense_total_mm: number;
  aquasense_events: number;
  fixed_schedule_total_mm: number;
  fixed_schedule_events: number;
  fixed_schedule_interval_days: number;
  percent_water_saved: number;
}

export const SOIL_TYPES = ['sandy', 'sandy_loam', 'loam', 'clay_loam', 'clay'] as const;
export const IRRIGATION_METHODS = ['drip', 'sprinkler', 'flood'] as const;
