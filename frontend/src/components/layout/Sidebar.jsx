import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import {
  MdDashboard, MdUpload, MdAutoGraph, MdAssessment,
  MdLogout, MdPerson, MdSettings, MdAdminPanelSettings,
  MdMenu, MdClose, MdAnalytics, MdMonitor, MdWarning,
} from "react-icons/md";
import { TbBrain } from "react-icons/tb";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: MdDashboard },
  { to: "/datasets", label: "Datasets", icon: MdUpload },
  { to: "/forecast", label: "Forecast", icon: TbBrain },
  { to: "/analytics", label: "Analytics", icon: MdAnalytics },
  { to: "/anomalies", label: "Anomalies", icon: MdWarning },
  { to: "/reports", label: "Reports", icon: MdAssessment },
  { to: "/monitoring", label: "Monitoring", icon: MdMonitor },
  { to: "/profile", label: "Profile", icon: MdSettings },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => { logout(); navigate("/login"); };
  const closeMobile = () => setMobileOpen(false);

  const SidebarContent = () => (
    <>
      <div className="px-5 py-5 border-b border-primary-100 dark:border-primary-900 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center shadow-green-glow">
            <MdAutoGraph className="text-white text-lg" />
          </div>
          <div>
            <span className="font-display font-bold text-sm leading-none" style={{ color: "var(--text)" }}>ForecastIQ</span>
            <p className="text-[10px] text-primary-500 mt-0.5">Enterprise v3.0</p>
          </div>
        </div>
        <button onClick={closeMobile} className="md:hidden text-primary-400 hover:text-primary-700">
          <MdClose className="text-xl" />
        </button>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto scrollbar-thin">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} onClick={closeMobile}
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <Icon className="text-lg flex-shrink-0" />{label}
          </NavLink>
        ))}
        {user?.is_admin && (
          <div className="pt-2 mt-2 border-t border-primary-100 dark:border-primary-900">
            <NavLink to="/admin" onClick={closeMobile}
              className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
              <MdAdminPanelSettings className="text-lg flex-shrink-0" />Admin Panel
            </NavLink>
          </div>
        )}
      </nav>

      <div className="px-3 pb-4 border-t border-primary-100 dark:border-primary-900 pt-3">
        <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-primary-50 dark:bg-primary-900/50 mb-2">
          <div className="w-7 h-7 bg-primary-200 dark:bg-primary-800 rounded-full flex items-center justify-center flex-shrink-0">
            <MdPerson className="text-primary-700 dark:text-primary-300 text-sm" />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold truncate" style={{ color: "var(--text)" }}>
              {user?.full_name || user?.username}
            </p>
            <p className="text-[10px] text-primary-500 truncate capitalize">
              {user?.is_admin ? "👑 Super Admin" : user?.role || "analyst"}
            </p>
          </div>
        </div>
        <button onClick={handleLogout}
          className="sidebar-link w-full text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600">
          <MdLogout className="text-lg" />Sign Out
        </button>
      </div>
    </>
  );

  return (
    <>
      <button onClick={() => setMobileOpen(true)}
        className="md:hidden fixed top-4 left-4 z-50 w-9 h-9 bg-white dark:bg-primary-950 border border-primary-200 dark:border-primary-800 rounded-xl flex items-center justify-center shadow-glass">
        <MdMenu className="text-primary-700 dark:text-primary-300 text-xl" />
      </button>

      {mobileOpen && (
        <div className="md:hidden fixed inset-0 bg-black/30 z-40 backdrop-blur-sm" onClick={closeMobile} />
      )}

      <aside className={`md:hidden fixed top-0 left-0 h-full w-64 backdrop-blur-md border-r flex flex-col z-50 transition-transform duration-300
        bg-white/95 dark:bg-primary-950/95 border-primary-100 dark:border-primary-900
        ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <SidebarContent />
      </aside>

      <aside className="hidden md:flex w-60 min-h-screen backdrop-blur-md border-r flex-col
        bg-white/80 dark:bg-primary-950/80 border-primary-100 dark:border-primary-900 transition-colors duration-300">
        <SidebarContent />
      </aside>
    </>
  );
}
