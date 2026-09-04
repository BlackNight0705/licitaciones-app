import { NavLink } from "react-router-dom";
import { LayoutGrid, FileText, LogOut } from "lucide-react";
import { useAuth } from "../../context/AuthContext.jsx";

const navItems = [
  { to: "/", label: "Licitaciones", icon: LayoutGrid, end: true },
];

export default function Sidebar({ isOpen, onNavigate }) {
  const { logout } = useAuth();

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-brand-950 text-brand-100
        transition-transform duration-200 lg:static lg:translate-x-0
        ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
    >
      <div className="flex items-center gap-2.5 px-6 py-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-500">
          <FileText size={18} className="text-white" />
        </div>
        <div className="font-display text-base font-semibold text-white">
          Portal de Licitaciones
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {navItems.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-brand-800 text-white"
                  : "text-brand-200 hover:bg-brand-900 hover:text-white"
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-brand-900 p-3">
        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium
                     text-brand-200 transition-colors hover:bg-brand-900 hover:text-white"
        >
          <LogOut size={18} />
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}
