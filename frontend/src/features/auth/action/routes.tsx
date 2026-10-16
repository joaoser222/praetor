import { User } from 'lucide-react';

export const authRoutes = [
    {
        path: '/profile',
        element: <div className="p-8"><h1>Página de Perfil</h1></div>,
        label: 'Perfil',
        icon: User,
        showInSidebar: true,
    },
];
