import { Route, Routes } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { InvestigatePlaceholderPage } from "./pages/InvestigatePlaceholderPage";
import { PaymentDetailPage } from "./pages/PaymentDetailPage";
import { PaymentsPage } from "./pages/PaymentsPage";

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<PaymentsPage />} />
        <Route path="/payments/:paymentId" element={<PaymentDetailPage />} />
        <Route
          path="/payments/:paymentId/investigate"
          element={<InvestigatePlaceholderPage />}
        />
      </Route>
    </Routes>
  );
}
