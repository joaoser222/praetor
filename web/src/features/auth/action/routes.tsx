import { User } from 'lucide-react';

export const authRoutes = [
    {
        path: '/profile',
        element: <div className="p-8"><h1>Profile Page</h1></div>,
        label: 'Profile',
        icon: User,
        showInSidebar: true,
    },
];
