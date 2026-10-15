import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { clearSession, getAccessToken, getRefreshToken, saveTokens } from './auth';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    withCredentials: true,
});

api.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        throw new Error('Sem token de refresh');
    }
    const response = await api.post('/auth/action/refresh', { refresh_token: refreshToken });
    saveTokens(response.data);
    return response.data.access_token as string;
}

api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
        const status = error.response?.status;
        const url = original?.url ?? '';

        const isAuthEndpoint = url.includes('/auth/action/');

        if (status === 401 && original && !original._retry && !isAuthEndpoint) {
            original._retry = true;
            try {
                // Reaproveita uma única requisição de refresh concorrente.
                refreshPromise = refreshPromise ?? refreshAccessToken().finally(() => {
                    refreshPromise = null;
                });
                const newToken = await refreshPromise;
                original.headers.Authorization = `Bearer ${newToken}`;
                return api(original);
            } catch (refreshError) {
                clearSession();
                if (window.location.pathname !== '/login') {
                    window.location.href = '/login';
                }
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;
