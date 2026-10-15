import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from '@mantine/core';
import LoginPage from '@/features/auth/action/pages/LoginPage';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import type { RouteConfig } from '@/lib/routes';
import { clearSession, isAuthenticated } from '@/lib/auth';

// ----------------------------------------------------------------------
// Descoberta dinâmica de rotas
// ----------------------------------------------------------------------
const featureModules = import.meta.glob('./features/**/routes.tsx', { eager: true });

const allRoutes: RouteConfig[] = Object.values(featureModules).flatMap((module) => {
  const featureModule = module as Record<string, unknown>;
  const exportName = Object.keys(featureModule).find(key => key.endsWith('Routes'));
  const routes = (exportName ? featureModule[exportName] : []) as RouteConfig[];
  return routes.map((r) => ({
    ...r,
    path: r.path === '/' ? '/panel' : `/panel${r.path.startsWith('/') ? r.path : '/' + r.path}`
  }));
});

// ----------------------------------------------------------------------
// Proteção de autenticação
// ----------------------------------------------------------------------
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  return isAuthenticated() ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  const handleLogout = () => {
    clearSession();
    window.location.href = '/login';
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route path="/panel/*" element={
          <PrivateRoute>
            <AppShell
              header={{ height: 64 }}
              navbar={{ width: 260, breakpoint: 'sm' }}
              padding="md"
            >
              <AppShell.Header>
                <Header />
              </AppShell.Header>

              <AppShell.Navbar p="xs">
                <Sidebar routes={allRoutes} onLogout={handleLogout} />
              </AppShell.Navbar>

              <AppShell.Main>
                <Routes>
                  {allRoutes.map((route) => {
                    const relativePath = route.path === '/panel' ? '' : route.path.replace('/panel/', '');
                    return <Route key={route.path} path={relativePath} element={route.element} />;
                  })}
                  <Route path="*" element={<Navigate to="/panel" replace />} />
                </Routes>
              </AppShell.Main>
            </AppShell>
          </PrivateRoute>
        } />

        <Route path="/" element={<Navigate to="/panel" replace />} />
        <Route path="*" element={<Navigate to="/panel" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
