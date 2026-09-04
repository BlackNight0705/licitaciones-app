import { Menu } from "lucide-react";

export default function Navbar({ title, onMenuClick }) {
  return (
    <header className="flex items-center gap-3 border-b border-brand-100 bg-white/80 px-4 py-4 backdrop-blur lg:px-8">
      <button
        type="button"
        onClick={onMenuClick}
        className="rounded-lg p-2 text-ink-700 hover:bg-brand-50 lg:hidden"
        aria-label="Abrir menú"
      >
        <Menu size={20} />
      </button>
      <h1 className="font-display text-xl font-semibold text-ink-900">{title}</h1>
    </header>
  );
}
