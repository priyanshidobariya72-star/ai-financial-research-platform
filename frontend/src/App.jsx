import { NavLink, Route, Routes } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import ChatPage from "./pages/ChatPage";
import UploadPage from "./pages/UploadPage";
import ComparePage from "./pages/ComparePage";
import { HealthBadge } from "./components/HealthBadge";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/chat", label: "Chat" },
  { to: "/upload", label: "Upload" },
  { to: "/compare", label: "Compare" }
];

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">AF</span>
          <div>
            <h1>Research Desk</h1>
            <p>Equity workflow over market, news, and filings.</p>
          </div>
        </div>
        <nav className="nav-list">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <HealthBadge />
      </aside>
      <main className="main-panel">
        <header className="page-header">
          <div>
            <p className="eyebrow">AI Financial Research Platform</p>
            <h2>Unified market, news, RAG, and agent workflows</h2>
          </div>
        </header>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/compare" element={<ComparePage />} />
        </Routes>
      </main>
    </div>
  );
}
