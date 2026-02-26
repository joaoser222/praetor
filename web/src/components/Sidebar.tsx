import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import { cn } from '../lib/utils';

interface SidebarProps {
    routes: any[];
    onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ routes, onLogout }) => {
    const location = useLocation();

    return (
        <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
            <div className="p-6">
                <h1 className="text-xl font-bold text-primary">Praetor</h1>
            </div>

            <nav className="flex-1 px-4 space-y-1">
                {routes.filter(r => r.showInSidebar).map((route) => {
                    const isActive = location.pathname === route.path;
                    return (
                        <Link
                            key={route.path}
                            to={route.path}
                            className={cn(
                                "flex items-center gap-3 px-4 py-2.5 text-sm font-medium rounded-lg transition-colors",
                                isActive
                                    ? "bg-primary/10 text-primary"
                                    : "text-gray-700 hover:bg-gray-100"
                            )}
                        >
                            <route.icon size={20} className={isActive ? "text-primary" : "text-gray-400"} />
                            {route.label}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-gray-100">
                <button
                    onClick={onLogout}
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm font-medium text-destructive rounded-lg hover:bg-destructive/5 transition-colors"
                >
                    <LogOut size={20} />
                    Logout
                </button>
            </div>
        </aside>
    );
};
