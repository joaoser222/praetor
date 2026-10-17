import api from '@/lib/api';
import type { LoginFormValues } from './schema';
import type { User } from './types';

export const authService = {
    async login(credentials: LoginFormValues) {
        const formData = new FormData();
        formData.append('username', credentials.email);
        formData.append('password', credentials.password);

        // O servidor grava os tokens em cookies HttpOnly; o SPA ignora o corpo.
        const response = await api.post('/auth/action/login', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    },

    /** Revoga a sessão no servidor (limpa os cookies HttpOnly). */
    async logout() {
        try {
            await api.post('/auth/action/logout');
        } catch {
            // Mesmo que a revogação falhe, o estado local é limpo pelo provider.
        }
    },

    /** Retorna o usuário autenticado ou lança 401 se não houver sessão válida. */
    async getProfile(): Promise<User> {
        const response = await api.get<User>('/auth/action/profile');
        return response.data;
    }
};
