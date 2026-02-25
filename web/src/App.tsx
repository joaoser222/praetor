import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import LoginPage from './features/auth/action/pages/LoginPage';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';

// ----------------------------------------------------------------------
// Dynamic Route Discovery
// ----------------------------------------------------------------------
const featureModules = import.meta.glob('./features/**/routes.tsx', { eager: true });

interface RouteConfig {
  path: string;
  element: React.ReactNode;
  label: string;
  icon: any;
  showInSidebar?: boolean;
}

const allRoutes: RouteConfig[] = Object.values(featureModules).flatMap((module: any) => {
  const exportName = Object.keys(module).find(key => key.endsWith('Routes'));
  return exportName ? module[exportName] : [];
});

// ----------------------------------------------------------------------
// Auth Guard
// ----------------------------------------------------------------------
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  };

  return (
    <Router>
      <div className="min-h-screen bg-background font-sans antialiased">
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route path="*" element={
            <PrivateRoute>
              <div className="flex min-h-screen">
                <Sidebar routes={allRoutes} onLogout={handleLogout} />

                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header />

                  <main className="flex-1 overflow-auto p-6 bg-gray-50/50">
                    <Routes>
                      {allRoutes.map((route) => (
                        <Route key={route.path} path={route.path} element={route.element} />
                      ))}
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </main>
                </div>
              </div>
            </PrivateRoute>
          } />
        </Routes>
      </div>
      <Toaster position="top-right" />
    </Router>
  );
}

export default App;
