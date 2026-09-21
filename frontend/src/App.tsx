import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ScanPage from "./pages/ScanPage";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));
const HelpPage = lazy(() => import("./pages/HelpPage"));

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<ScanPage />} />
        <Route path="history" element={<Suspense fallback={null}><DashboardPage /></Suspense>} />
        <Route path="settings" element={<Suspense fallback={null}><SettingsPage /></Suspense>} />
        <Route path="help" element={<Suspense fallback={null}><HelpPage /></Suspense>} />
      </Route>
    </Routes>
  );
}
