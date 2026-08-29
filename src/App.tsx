import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { RecruitingProvider } from "./context/RecruitingStore";
import { Header } from "./components/Header";
import { BrowsePage } from "./pages/BrowsePage";
import { SchoolPage } from "./pages/SchoolPage";
import { TargetsPage } from "./pages/TargetsPage";

const basename = import.meta.env.BASE_URL.replace(/\/$/, "") || undefined;

export default function App() {
  return (
    <RecruitingProvider>
      <BrowserRouter basename={basename}>
        <div className="flex min-h-screen flex-col bg-white">
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
            Notes and your target list are saved in this browser on this device — they are not
            synced to iCloud or other phones unless you export a backup. Confirm stats with each
            school before you apply or commit.
          </footer>
        </div>
      </BrowserRouter>
    </RecruitingProvider>
  );
}
