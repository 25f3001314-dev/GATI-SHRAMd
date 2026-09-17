"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { StatusBadge } from "./StatusBadge";

const navigation = [
  { href: "/dashboard", label: "Overview" },
  { href: "/data", label: "Data provenance" },
  { href: "/model", label: "Model status" },
  { href: "/architecture", label: "Architecture" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const sidebarContent = (
    <>
      <div className="brand">
        <div className="brand-header">
          <div className="brand-mark">GS</div>
          <button
            className="menu-close"
            type="button"
            onClick={() => setMobileOpen(false)}
            aria-label="Close navigation"
          >
            ×
          </button>
        </div>
        <div className="brand-name">Gati Shram</div>
        <div className="brand-subtitle">Predictive mobility intelligence</div>
      </div>
      <div className="nav-label">Workspace</div>
      <nav className="nav-list" aria-label="Primary navigation">
        {navigation.map((item) => (
          <Link className={`nav-link ${pathname === item.href ? "active" : ""}`} href={item.href} key={item.href} onClick={() => setMobileOpen(false)}>
            <span className="nav-dot" aria-hidden="true" />
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="sidebar-footer">
        <StatusBadge tone="amber">DEMO ENVIRONMENT</StatusBadge>
        <p>Outputs are synthetic or prototype estimates unless provenance says otherwise.</p>
      </div>
    </>
  );

  return (
    <div className="shell">
      <aside className="sidebar">{sidebarContent}</aside>
      {mobileOpen ? <button className="drawer-backdrop" type="button" onClick={() => setMobileOpen(false)} aria-label="Close navigation" /> : null}
      <aside className={`mobile-sidebar ${mobileOpen ? "open" : ""}`}>{sidebarContent}</aside>
      <div className="main">
        <header className="topbar">
          <button className="menu-toggle" type="button" onClick={() => setMobileOpen(true)} aria-label="Open navigation">
            <span />
            <span />
            <span />
          </button>
          <span className="topbar-title">Mobility intelligence workspace</span>
          <div className="topbar-meta"><span>September 2026 prototype</span><a className="topbar-link" href="/docs" target="_blank" rel="noreferrer">API docs</a></div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
