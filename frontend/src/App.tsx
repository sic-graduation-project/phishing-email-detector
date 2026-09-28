import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";

const ScanPage = lazy(() => import("./pages/ScanPage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));
const HelpPage = lazy(() => import("./pages/HelpPage"));

export default function App() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-slate-500">Loading…</div>}><Routes>
      <Route element={<Layout />}>
        <Route index element={<ScanPage />} />
        <Route path="history" element={<DashboardPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="help" element={<HelpPage />} />
      </Route>
    </Routes></Suspense>
  );
}
