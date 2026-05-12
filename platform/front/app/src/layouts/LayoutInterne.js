import { Link, Outlet } from "react-router-dom";

const menuItems = [
  { path: "/interne/HomePage", label: "Supervision" },
  { path: "/externe/HomePage", label: "Espace externe" },
  { path: "/", label: "Accueil" },
];

export default function LayoutInterne() {
  return (
    <div className="internal-shell">
      <aside className="internal-sidebar">
        <div className="internal-brand">
          <h2>ObRail</h2>
          <p>Espace interne</p>
        </div>

        <nav className="internal-nav" aria-label="Navigation interne">
          {menuItems.map((item) => (
            <Link key={item.path} to={item.path}>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      <section className="internal-content">
        <Outlet />
      </section>
    </div>
  );
}
