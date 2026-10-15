import { LayoutDashboard } from 'lucide-react';

export const dashboardRoutes = [
    {
        path: '/',
        element: <div className="p-8"><h1>Painel</h1><p className="text-gray-500 mt-2">Bem-vindo ao Praetor.</p></div>,
        label: 'Painel',
        icon: LayoutDashboard,
        showInSidebar: true,
    }
];
