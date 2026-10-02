import { ReactNode } from "react";

export interface AppShellProps {
  children: ReactNode;
  className?: string;
}

export default function AppShell({ children, className }: AppShellProps) {
  return (
    <div className={`rbm-app-shell ${className ?? ""}`.trim()}>
      {children}
    </div>
  );
}