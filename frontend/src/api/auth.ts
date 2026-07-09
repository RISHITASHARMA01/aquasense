import { apiClient } from './client';

export async function register(email: string, password: string): Promise<void> {
  await apiClient.post('/auth/register', { email, password });
}

export async function login(email: string, password: string): Promise<string> {
  const form = new URLSearchParams();
  form.set('username', email);
  form.set('password', password);
  const { data } = await apiClient.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return data.access_token;
}
