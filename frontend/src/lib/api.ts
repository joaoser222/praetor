import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';

// Cookie-first: os tokens de sessão vivem em cookies HttpOnly (invisíveis ao JS).
// O cliente não lê nem envia tokens — apenas envia/aceita cookies.
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    withCredentials: true,
});

let refreshPromise: Promise<void> | null = null;

/** Renova a sessão usando o cookie HttpOnly 'refresh_token'. */
async function refreshSession(): Promise<void> {
    await api.post('/auth/action/refresh');
}

api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
        const status = error.response?.status;
        const url = original?.url ?? '';

        // Só os endpoints do próprio fluxo de auth ficam de fora do refresh
        // automático; /profile, por exemplo, PRECISA disparar o refresh.
        const isAuthFlowEndpoint = [
            '/auth/action/login',
            '/auth/action/refresh',
            '/auth/action/logout',
        ].some((path) => url.includes(path));

        if (status === 401 && original && !original._retry && !isAuthFlowEndpoint) {
            original._retry = true;
            try {
                // Reaproveita uma única renovação concorrente.
                refreshPromise = refreshPromise ?? refreshSession().finally(() => {
                    refreshPromise = null;
                });
                await refreshPromise;
                // Os cookies renovados viajam automaticamente na repetição.
                return api(original);
            } catch (refreshError) {
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
