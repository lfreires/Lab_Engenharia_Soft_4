import { apiClient } from '../client';
import { AuthResponse, LoginRequest, RegisterRequest } from '../types';

export const authService = {
  async register(data: RegisterRequest): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/api/v1/auth/register', data);
    return response.data;
  },

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', data);
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('authToken');
  },

  getToken(): string | null {
    return localStorage.getItem('authToken');
  },

  setToken(token: string): void {
    localStorage.setItem('authToken', token);
  },
};
