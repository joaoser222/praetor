import api from '@/lib/api';
import { clearSession, saveTokens } from '@/lib/auth';
import type { LoginFormValues } from './schema';

export const authService = {
    async login(credentials: LoginFormValues) {
        const formData = new FormData();
        formData.append('username', credentials.email);
        formData.append('password', credentials.password);

        const response = await api.post('/auth/action/login', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        if (response.data.access_token) {
            saveTokens(response.data);
        }

        return response.data;
    },

    async logout() {
        clearSession();
        // Opcional: chamar o endpoint de logout para revogar o token de refresh no servidor.
    },

    async getProfile() {
        const response = await api.get('/auth/action/profile');
        return response.data;
    }
};
