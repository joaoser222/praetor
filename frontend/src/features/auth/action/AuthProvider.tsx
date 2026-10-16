import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { AuthContext, type AuthContextValue } from '@/lib/auth';
import { authService } from './service';
import type { LoginFormValues } from './schema';
import type { User } from './types';

/**
 * Mantém o estado de autenticação do SPA.
 *
 * Os tokens ficam apenas em cookies HttpOnly (invisíveis ao JS), então o estado
 * é reconstruído a partir do servidor (`/auth/action/profile`) no carregamento.
 */
export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Restaura a sessão no boot: se houver cookie válido, /profile responde 200;
    // se o access tiver expirado, o interceptor renova antes de responder.
    useEffect(() => {
        let active = true;

        authService
            .getProfile()
            .then((profile) => {
                if (active) setUser(profile);
            })
            .catch(() => {
                if (active) setUser(null);
            })
            .finally(() => {
                if (active) setIsLoading(false);
            });

        return () => {
            active = false;
        };
    }, []);

    const login = useCallback(async (values: LoginFormValues) => {
        await authService.login(values);
        setUser(await authService.getProfile());
    }, []);

    const logout = useCallback(async () => {
        try {
            await authService.logout();
        } finally {
            setUser(null);
        }
    }, []);

    const value = useMemo<AuthContextValue>(
        () => ({ user, isLoading, isAuthenticated: user !== null, login, logout }),
        [user, isLoading, login, logout],
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
