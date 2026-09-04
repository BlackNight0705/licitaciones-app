import { Routes, Route, Navigate } from "react-router-dom";
import PrivateRoute from "./routes/PrivateRoute.jsx";
import DashboardLayout from "./components/layout/DashboardLayout.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import LicitacionDetailPage from "./pages/LicitacionDetailPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<PrivateRoute />}>
        <Route element={<DashboardLayout title="Licitaciones" />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/licitaciones/:id" element={<LicitacionDetailPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
