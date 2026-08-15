import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import { AppShell } from "./layouts/AppShell";
import { Login } from "./pages/auth/Login";
import { HomePage } from "./pages/HomePage";
import { AnalyzePage } from "./pages/AnalyzePage";
import { HistoryPage } from "./pages/HistoryPage";
import { ReviewsPage } from "./pages/ReviewsPage";
import { ModelCenter } from "./pages/ModelCenter";
import { BatchAnalysis } from "./pages/BatchAnalysis";

function ProtectedRoute({ children, requireRoles }: { children?: React.ReactNode, requireRoles?: string[] }) {
  const { user, isLoading } = useAuth();
  
  if (isLoading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (requireRoles && !requireRoles.includes(user.role)) return <Navigate to="/" replace />;
  
  return <>{children || <Outlet />}</>;
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
        <Route path="/" element={<HomePage />} />
        <Route path="/analyze" element={<AnalyzePage />} />
        <Route path="/batch" element={<BatchAnalysis />} />
        <Route path="/history" element={<HistoryPage />} />
      </Route>

      <Route element={<ProtectedRoute requireRoles={["REVIEWER", "ADMIN"]}><AppShell /></ProtectedRoute>}>
        <Route path="/reviews" element={<ReviewsPage />} />
        <Route path="/models" element={<ModelCenter />} />
      </Route>
    </Routes>
  );
}
