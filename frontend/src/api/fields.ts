import { apiClient } from './client';
import type { Field, Forecast, History, Recommendation, Crop, WaterSavings } from '../types';

export async function listFields(): Promise<Field[]> {
  const { data } = await apiClient.get('/fields');
  return data;
}

export async function getField(fieldId: number): Promise<Field> {
  const { data } = await apiClient.get(`/fields/${fieldId}`);
  return data;
}

export interface CreateFieldPayload {
  name: string;
  latitude: number;
  longitude: number;
  soil_type: string;
  area_hectares: number;
  irrigation_method: string;
}

export async function createField(payload: CreateFieldPayload): Promise<Field> {
  const { data } = await apiClient.post('/fields', payload);
  return data;
}

export async function updateField(fieldId: number, payload: Partial<CreateFieldPayload>): Promise<Field> {
  const { data } = await apiClient.patch(`/fields/${fieldId}`, payload);
  return data;
}

export async function deleteField(fieldId: number): Promise<void> {
  await apiClient.delete(`/fields/${fieldId}`);
}

export async function plantCrop(fieldId: number, cropId: number, plantingDate: string): Promise<Field> {
  const { data } = await apiClient.post(`/fields/${fieldId}/crops`, {
    crop_id: cropId,
    planting_date: plantingDate,
  });
  return data;
}

export async function listCrops(): Promise<Crop[]> {
  const { data } = await apiClient.get('/crops');
  return data;
}

export async function getRecommendation(fieldId: number): Promise<Recommendation> {
  const { data } = await apiClient.get(`/fields/${fieldId}/recommendation`);
  return data;
}

export async function getHistory(fieldId: number, days = 30): Promise<History> {
  const { data } = await apiClient.get(`/fields/${fieldId}/history`, { params: { days } });
  return data;
}

export async function getForecast(fieldId: number): Promise<Forecast> {
  const { data } = await apiClient.get(`/fields/${fieldId}/forecast`);
  return data;
}

export async function getWaterSavings(fieldId: number): Promise<WaterSavings> {
  const { data } = await apiClient.get(`/fields/${fieldId}/water-savings`);
  return data;
}
