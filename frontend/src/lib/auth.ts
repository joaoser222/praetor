import { createContext, useContext } from 'react';
import type { LoginFormValues } from '@/features/auth/action/schema';
import type { User } from '@/features/auth/action/types';

export interface AuthContextValue {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (values: LoginFormValues) => Promise<void>;
    logout: () => Promise<void>;
}

/**
 * Contexto da sessão do SPA.
 *
 * Os tokens ficam apenas em cookies HttpOnly (invisíveis ao JS); o estado é
 * reconstruído a partir do servidor pelo <AuthProvider>.
 */
export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/** Acessa o estado de autenticação. Requer <AuthProvider> acima na árvore. */
export function useAuth(): AuthContextValue {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth deve ser usado dentro de <AuthProvider>');
    }
    return context;
}
