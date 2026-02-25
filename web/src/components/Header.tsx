import React from 'react';

export const Header: React.FC = () => {
    return (
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-end px-8 shrink-0">
            <div className="flex items-center gap-4 text-sm font-medium text-gray-600">
                <span>Admin User</span>
                <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
                    A
                </div>
            </div>
        </header>
    );
};
