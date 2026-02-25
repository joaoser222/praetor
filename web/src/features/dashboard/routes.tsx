import { LayoutDashboard } from 'lucide-react';

export const dashboardRoutes = [
    {
        path: '/',
        element: <div className="p-8"><h1>Dashboard</h1><p className="text-gray-500 mt-2">Welcome to PraetorAPI.</p></div>,
        label: 'Dashboard',
        icon: LayoutDashboard,
        showInSidebar: true,
    }
];
