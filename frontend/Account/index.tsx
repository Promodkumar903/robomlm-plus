import { useMemo, useState } from "react";

import "./account.css";
import { useAccountData } from "./useAccountData";

type AccountMode = "REAL" | "DEMO";
type Currency = "USD" | "USDT" | "INR";

interface AccountSnapshot {
  balance: number | null;
  available: number | null;
  equity: number | null;
  margin: number | null;
  unrealizedPnl: number | null;
  realizedPnl: number | null;
}

interface Position {
  symbol: string;
  side: string;
  quantity: number | null;
  entryPrice: number | null;
  markPrice: number | null;
  pnl: number | null;
  status: string;
}

interface BrokerState {
  connected: boolean | null;
  provider: string;
  account: string;
  status: string;
}

const EMPTY_SNAPSHOT: AccountSnapshot = {
  balance: null,
  available: null,
  equity: null,
  margin: null,
  unrealizedPnl: null,
  realizedPnl: null,
};

const EMPTY_BROKER: BrokerState = {
  connected: null,
  provider: "Backend controlled",
  account: "—",
  status: "NOT AVAILABLE",
};

function formatMoney(
  value: number | null,
  currency: Currency
): string {
  if (value === null || !Number.isFinite(value)) {
    return "—";
  }

  const currencyMap: Record<Currency, string> = {
    USD: "USD",
    USDT: "USDT",
    INR: "INR",
  };

  return `${currencyMap[currency]} ${value.toLocaleString(
    undefined,
    {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }
  )}`;
}

function formatNumber(
  value: number | null
): string {
  if (value === null || !Number.isFinite(value)) {
    return "—";
  }

  return value.toLocaleString(undefined, {
    maximumFractionDigits: 6,
  });
}

function StateBadge({
  value,
}: {
  value: string;
}) {
  const normalized = value.toUpperCase();

  const className =
    normalized === "CONNECTED" ||
    normalized === "ACTIVE" ||
    normalized === "READY"
      ? "account-status account-status-positive"
      : normalized === "NOT AVAILABLE" ||
          normalized === "DISCONNECTED" ||
          normalized === "BLOCKED"
        ? "account-status account-status-neutral"
        : "account-status";

  return (
    <span className={className}>
      {value}
    </span>
  );
}

function Metric({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <article className="account-metric">
      <span className="account-metric-label">
        {label}
      </span>

      <strong className="account-metric-value">
        {value}
      </strong>

      <small className="account-metric-detail">
        {detail}
      </small>
    </article>
  );
}

export default function Account() {
  const account = useAccountData();

  const mode = account.mode;
  const setMode = account.setMode;
  const currency = account.currency;
  const setCurrency = account.setCurrency;
  const snapshot = account.snapshot;
  const broker = account.broker;
  const positions = account.positions;

  const hasBackendSnapshot = useMemo(
    () =>
      Object.values(snapshot).some(
        (value) =>
          value !== null
      ),
    [snapshot]
  );

  const hasPositions =
    positions.length > 0;

  return (
    <main className="account-page">
      <header className="account-header">
        <div>
          <p className="account-eyebrow">
            ROBOMLM+ / ACCOUNT
          </p>

          <h1>Account</h1>

          <p className="account-subtitle">
            Account, capital, position and
            broker-state visibility.
          </p>
        </div>

        <div className="account-header-controls">
          <label className="account-control">
            <span>Account mode</span>

            <select
              value={mode}
              onChange={(event) =>
                setMode(
                  event.target
                    .value as AccountMode
                )
              }
            >
              <option value="REAL">
                REAL
              </option>

              <option value="DEMO">
                DEMO
              </option>
            </select>
          </label>

          <label className="account-control">
            <span>Currency</span>

            <select
              value={currency}
              onChange={(event) =>
                setCurrency(
                  event.target
                    .value as Currency
                )
              }
            >
              <option value="USD">
                USD
              </option>

              <option value="USDT">
                USDT
              </option>

              <option value="INR">
                INR
              </option>
            </select>
          </label>
        </div>
      </header>

      <section className="account-status-banner">
        <div className="account-status-banner-main">
          <span className="account-eyebrow">
            Account state
          </span>

          <strong>
            {mode} ACCOUNT
          </strong>

          <p>
            {hasBackendSnapshot
              ? "Backend account data is available."
              : "Account balances are controlled by the backend and are not currently available through the verified frontend contract."}
          </p>
        </div>

        <StateBadge
          value={
            hasBackendSnapshot
              ? "ACTIVE"
              : "NOT AVAILABLE"
          }
        />
      </section>

      <section className="account-metrics">
        <Metric
          label="Balance"
          value={formatMoney(
            snapshot.balance,
            currency
          )}
          detail="Backend account balance"
        />

        <Metric
          label="Available"
          value={formatMoney(
            snapshot.available,
            currency
          )}
          detail="Available capital"
        />

        <Metric
          label="Equity"
          value={formatMoney(
            snapshot.equity,
            currency
          )}
          detail="Current account equity"
        />

        <Metric
          label="Margin"
          value={formatMoney(
            snapshot.margin,
            currency
          )}
          detail="Used margin"
        />
      </section>

      <section className="account-grid">
        <article className="account-panel">
          <div className="account-panel-header">
            <div>
              <span className="account-eyebrow">
                P&L
              </span>

              <h2>
                Performance state
              </h2>
            </div>
          </div>

          <div className="account-detail-list">
            <div className="account-detail-row">
              <span>
                Unrealized P&L
              </span>

              <strong>
                {formatMoney(
                  snapshot.unrealizedPnl,
                  currency
                )}
              </strong>
            </div>

            <div className="account-detail-row">
              <span>
                Realized P&L
              </span>

              <strong>
                {formatMoney(
                  snapshot.realizedPnl,
                  currency
                )}
              </strong>
            </div>

            <div className="account-detail-row">
              <span>
                Account mode
              </span>

              <strong>
                {mode}
              </strong>
            </div>

            <div className="account-detail-row">
              <span>
                Currency
              </span>

              <strong>
                {currency}
              </strong>
            </div>
          </div>
        </article>

        <article className="account-panel">
          <div className="account-panel-header">
            <div>
              <span className="account-eyebrow">
                Broker
              </span>

              <h2>
                Connection state
              </h2>
            </div>

            <StateBadge
              value={
                broker.connected === true
                  ? "CONNECTED"
                  : broker.connected ===
                      false
                    ? "DISCONNECTED"
                    : "NOT AVAILABLE"
              }
            />
          </div>

          <div className="account-detail-list">
            <div className="account-detail-row">
              <span>
                Provider
              </span>

              <strong>
                {broker.provider}
              </strong>
            </div>

            <div className="account-detail-row">
              <span>
                Account
              </span>

              <strong>
                {broker.account}
              </strong>
            </div>

            <div className="account-detail-row">
              <span>
                Connection
              </span>

              <strong>
                {broker.status}
              </strong>
            </div>
          </div>
        </article>
      </section>

      <section className="account-panel">
        <div className="account-panel-header">
          <div>
            <span className="account-eyebrow">
              Positions
            </span>

            <h2>
              Open positions
            </h2>
          </div>

          <span className="account-count">
            {positions.length}
          </span>
        </div>

        {!hasPositions ? (
          <div className="account-empty">
            <strong>
              No position data available
            </strong>

            <p>
              The frontend will display
              backend position records here
              when the verified account
              contract provides them.
            </p>
          </div>
        ) : (
          <div className="account-table-wrap">
            <table className="account-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Side</th>
                  <th>Quantity</th>
                  <th>Entry</th>
                  <th>Mark</th>
                  <th>P&L</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {positions.map(
                  (position) => (
                    <tr
                      key={`${position.symbol}-${position.side}`}
                    >
                      <td>
                        {position.symbol}
                      </td>

                      <td>
                        {position.side}
                      </td>

                      <td>
                        {formatNumber(
                          position.quantity
                        )}
                      </td>

                      <td>
                        {formatNumber(
                          position.entryPrice
                        )}
                      </td>

                      <td>
                        {formatNumber(
                          position.markPrice
                        )}
                      </td>

                      <td>
                        {formatMoney(
                          position.pnl,
                          currency
                        )}
                      </td>

                      <td>
                        <StateBadge
                          value={
                            position.status
                          }
                        />
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="account-panel account-authority">
        <span className="account-eyebrow">
          System boundary
        </span>

        <h2>
          Backend remains authoritative
        </h2>

        <p>
          This page does not fabricate
          balances, broker connections,
          positions, margin, or P&L. Those
          values must come from the
          authoritative backend account and
          broker services.
        </p>
      </section>
    </main>
  );
}