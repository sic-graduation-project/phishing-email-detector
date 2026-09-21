import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ScanPage from "./pages/ScanPage";
import DashboardPage from "./pages/DashboardPage";
import SettingsPage from "./pages/SettingsPage";
import HelpPage from "./pages/HelpPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<ScanPage />} />
        <Route path="history" element={<DashboardPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="help" element={<HelpPage />} />
      </Route>
    </Routes>
  );
}
