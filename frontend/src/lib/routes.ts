import type { ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';

/**
 * Configuração de uma rota descoberta automaticamente a partir de
 * `features/**\/routes.tsx`. O prefixo `/panel` é adicionado em `App.tsx`.
 */
export interface RouteConfig {
    path: string;
    element: ReactNode;
    label: string;
    icon: LucideIcon;
    showInSidebar?: boolean;
}
