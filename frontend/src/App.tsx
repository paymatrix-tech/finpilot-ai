import { Route, Routes } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { InvestigationPage } from "./pages/InvestigationPage";
import { SavedInvestigationPage } from "./pages/SavedInvestigationPage";
import { PaymentDetailPage } from "./pages/PaymentDetailPage";
import { PaymentsPage } from "./pages/PaymentsPage";

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<PaymentsPage />} />
        <Route path="/payments/:paymentId" element={<PaymentDetailPage />} />
        <Route
          path="/payments/:paymentId/investigations/:investigationId"
          element={<SavedInvestigationPage />}
        />
        <Route
          path="/payments/:paymentId/investigate"
          element={<InvestigationPage />}
        />
      </Route>
    </Routes>
  );
}
