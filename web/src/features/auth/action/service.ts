import api from '../../../lib/api';



export const authService = {
    async login(credentials: any) {
        const formData = new FormData();
        formData.append('username', credentials.email);
        formData.append('password', credentials.password);

        const response = await api.post('/auth/action/login', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        if (response.data.access_token) {
            localStorage.setItem('access_token', response.data.access_token);
        }

        return response.data;
    },

    async logout() {
        localStorage.removeItem('access_token');
        // Optional: call logout endpoint if you want to revoke refresh token
    },

    async getProfile() {
        const response = await api.get('/auth/action/profile');
        return response.data;
    }
};
