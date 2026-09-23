import { Route, Routes } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { PaymentsPage } from "./pages/PaymentsPage";

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<PaymentsPage />} />
      </Route>
    </Routes>
  );
}
