import { useState } from "react";
import { ChevronUp, Zap, Send, Bot, LogOut } from "lucide-react";
import { motion } from "framer-motion";

const navItems = [
  { id: "scraper", label: "Scraper Web", icon: Zap },
  { id: "conexion", label: "Envio de Conexion", icon: Send },
  { id: "scrapers", label: "Scrapers", icon: Bot },
];

interface SidebarProps {
  activeItem: string;
  onNavigate: (id: string) => void;
}

export function Sidebar({ activeItem, onNavigate }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className="flex w-[190px] flex-col border-r border-border bg-sidebar">
      <div className="flex items-center justify-between px-4 py-4">
        <div>
          <p className="text-sm font-bold text-white">DATAPATH</p>
          <p className="text-xs text-slate-400">SCRAPER</p>
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-slate-400 hover:text-white"
        >
          <ChevronUp
            size={16}
            className={`transition-transform ${collapsed ? "rotate-180" : ""}`}
          />
        </button>
      </div>

      {!collapsed && (
        <nav className="flex flex-1 flex-col gap-1 px-2">
          {navItems.map((item) => {
            const isActive = activeItem === item.id;
            return (
              <motion.button
                key={item.id}
                whileTap={{ scale: 0.97 }}
                onClick={() => onNavigate(item.id)}
                className={`flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                  isActive
                    ? "bg-amber-500/20 text-amber-300 font-medium border border-amber-500/25"
                    : "text-slate-400 hover:bg-slate-700/50 hover:text-slate-200"
                }`}
              >
                <item.icon size={16} />
                {item.label}
              </motion.button>
            );
          })}
        </nav>
      )}

      <div className="mt-auto px-2 pb-4">
        <button className="flex w-full items-center gap-2.5 rounded-lg bg-amber-500/20 border border-amber-500/25 px-3 py-2.5 text-sm text-amber-300 transition-colors hover:bg-amber-500/30">
          <LogOut size={16} />
          Cerrar Sesion
        </button>
      </div>
    </aside>
  );
}
