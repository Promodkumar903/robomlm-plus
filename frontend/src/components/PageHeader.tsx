import { ReactNode } from "react";

export interface PageHeaderProps {
  title?: string;
  subtitle?: string;
  eyebrow?: string;
  actions?: ReactNode;
  status?: ReactNode;
}

export default function PageHeader({
  title,
  subtitle,
  eyebrow,
  actions,
  status,
}: PageHeaderProps) {
  return (
    <header className="rbm-page-header">
      <div>
        {eyebrow && <div className="rbm-page-eyebrow">{eyebrow}</div>}
        {title && <h1>{title}</h1>}
        {subtitle && <p>{subtitle}</p>}
      </div>
      {(actions || status) && (
        <div className="rbm-page-header-actions">
          {status}
          {actions}
        </div>
      )}
    </header>
  );
}