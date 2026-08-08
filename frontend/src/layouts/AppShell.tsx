import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Activity, LayoutDashboard, FileUp, List, LogOut, User as UserIcon } from "lucide-react";
import { cn } from "../lib/utils";

interface AppShellProps {
  children?: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Analyze", href: "/analyze", icon: FileUp },
    { name: "History", href: "/history", icon: List },
  ];

  if (user?.role === "REVIEWER" || user?.role === "ADMIN") {
    navItems.push({ name: "Reviews", href: "/reviews", icon: Activity });
  }

  return (
    <div className="flex min-h-screen flex-col bg-secondary/50">
      <header className="sticky top-0 z-40 w-full border-b bg-background shadow-sm">
        <div className="container flex h-16 items-center px-4 md:px-8 max-w-7xl mx-auto">
          <div className="flex items-center gap-2 mr-8">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
              <Activity className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="font-bold hidden sm:inline-block tracking-tight text-lg">
              MedVision AI
            </span>
          </div>
          
          <nav className="flex items-center space-x-1 lg:space-x-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
                  location.pathname === item.href
                    ? "bg-secondary text-secondary-foreground"
                    : "text-muted-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                <span className="hidden sm:inline">{item.name}</span>
              </Link>
            ))}
          </nav>
          
          <div className="ml-auto flex items-center space-x-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground hidden md:flex">
              <UserIcon className="h-4 w-4" />
              <span>{user?.email}</span>
              <span className="ml-2 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                {user?.role}
              </span>
            </div>
            <button
              onClick={logout}
              className="flex items-center justify-center p-2 rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </header>
      <main className="flex-1 w-full max-w-7xl mx-auto p-4 md:p-8">
        {children}
      </main>
    </div>
  );
}
