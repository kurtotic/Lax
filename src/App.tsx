import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { RecruitingProvider } from "./context/RecruitingStore";
import { Header } from "./components/Header";
import { BrowsePage } from "./pages/BrowsePage";
import { SchoolPage } from "./pages/SchoolPage";
import { TargetsPage } from "./pages/TargetsPage";

export default function App() {
  return (
    <RecruitingProvider>
      <BrowserRouter>
        <div className="flex min-h-screen flex-col">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<BrowsePage />} />
              <Route path="/schools/:id" element={<SchoolPage />} />
              <Route path="/targets" element={<TargetsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <footer className="border-t border-line px-4 py-6 text-center text-xs text-muted">
            Lax is a family recruiting notebook — not an official NCAA directory. Confirm stats
            with each school before you apply or commit.
          </footer>
        </div>
      </BrowserRouter>
    </RecruitingProvider>
  );
}
