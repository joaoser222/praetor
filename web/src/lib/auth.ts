const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export interface AuthTokens {
    access_token: string;
    refresh_token: string;
}

/** Persiste os tokens da sessão no armazenamento local. */
export function saveTokens(tokens: AuthTokens): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/** Remove todos os dados da sessão. */
export function clearSession(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/** Decodifica o payload de um JWT sem validar a assinatura. */
function decodeJwtPayload(token: string): { exp?: number } | null {
    try {
        const part = token.split('.')[1];
        if (!part) return null;
        const base64 = part.replace(/-/g, '+').replace(/_/g, '/');
        const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
        return JSON.parse(atob(padded)) as { exp?: number };
    } catch {
        return null;
    }
}

/** Indica se há um access token presente e ainda não expirado. */
export function isAuthenticated(): boolean {
    const token = getAccessToken();
    if (!token) return false;
    const payload = decodeJwtPayload(token);
    if (!payload?.exp) return true;
    return payload.exp * 1000 > Date.now();
}
