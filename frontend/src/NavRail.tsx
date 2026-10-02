import { NavLink } from "react-router-dom";

const ITEMS = [
  { to: "/terminal",    label: "Terminal",    icon: "M3 3h18v18H3z M3 9h18 M9 21V9" },
  { to: "/discovery",   label: "Discovery",   icon: "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z M21 21l-4.35-4.35" },
  { to: "/research",    label: "Research",    icon: "M9 3v6l-4 9h14l-4-9V3 M8 3h8" },
  { to: "/buyer",       label: "Buyer",       icon: "M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z M3 6h18 M16 10a4 4 0 0 1-8 0" },
  { to: "/htf",         label: "HTF",         icon: "M12 6v6l4 2 M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z" },
  { to: "/scalper",     label: "Scalper",     icon: "M13 2 3 14h9l-1 8 10-12h-9z" },
  { to: "/autorobomlm", label: "AutoROBOMLM", icon: "M12 2v4 M12 18v4 M4.93 4.93l2.83 2.83 M16.24 16.24l2.83 2.83 M2 12h4 M18 12h4 M4.93 19.07l2.83-2.83 M16.24 7.76l2.83-2.83" },
  { to: "/memory",      label: "Memory",      icon: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 6v6l4 2" },
  { to: "/account",     label: "Account",     icon: "M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2 M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" },
];

export default function NavRail() {
  return (
    <nav className="rbm-navrail">
      <div className="rbm-navrail-logo">R+</div>
      <div className="rbm-navrail-items">
        {ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `rbm-navrail-btn ${isActive ? "rbm-navrail-btn-active" : ""}`
            }
            title={item.label}
            aria-label={item.label}
          >
            <svg
              width="18" height="18" viewBox="0 0 24 24"
              fill="none" stroke="currentColor"
              strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"
            >
              <path d={item.icon} />
            </svg>
            <span className="rbm-navrail-tip">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}