/* ============================================================================
   ROBOMLM_PLUS — TERMINAL BACKEND BRIDGE
   PART 5
   ============================================================================

   Responsibility:
       Backend Terminal API → existing terminal.html

   This file DOES NOT:
       - calculate D1-D16
       - calculate EQE
       - manufacture BUY/SELL
       - calculate Risk
       - approve CAS
       - place orders
       - call broker APIs

   Backend authority:
       /api/terminal
       /api/terminal/context
       /api/terminal/frontend-map

   Existing UI selectors are preserved.
   ========================================================================== */

(function () {
    "use strict";

    const CONFIG = {
        terminal: "/api/terminal",
        context: "/api/terminal/context",
        frontendMap: "/api/terminal/frontend-map",
        refreshMs: 5000
    };

    const state = {
        loading: false,
        lastResult: null,
        lastContext: null,
        lastMap: null,
        timer: null,
        initialized: false
    };

    /* ========================================================================
       BASIC HELPERS
       ======================================================================== */

    function $(selector) {
        try {
            return document.querySelector(selector);
        } catch (_) {
            return null;
        }
    }

    function setText(selector, value) {
        const el = $(selector);
        if (!el) return;

        if (value === undefined || value === null || value === "") {
            return;
        }

        el.textContent = String(value);
    }

    function setHTML(selector, value) {
        const el = $(selector);
        if (!el) return;

        el.innerHTML = value == null ? "" : String(value);
    }

    function show(selector, visible) {
        const el = $(selector);
        if (!el) return;

        el.hidden = !visible;
        el.style.display = visible ? "" : "none";
    }

    function number(value, fallback = null) {
        if (value === undefined || value === null || value === "") {
            return fallback;
        }

        const n = Number(value);
        return Number.isFinite(n) ? n : fallback;
    }

    function clamp(value, min, max) {
        const n = number(value, null);
        if (n === null) return null;
        return Math.min(max, Math.max(min, n));
    }

    function firstDefined(...values) {
        for (const value of values) {
            if (
                value !== undefined &&
                value !== null &&
                value !== ""
            ) {
                return value;
            }
        }
        return null;
    }

    function object(value) {
        return value && typeof value === "object" ? value : {};
    }

    function array(value) {
        return Array.isArray(value) ? value : [];
    }

    function upper(value) {
        return value == null ? "" : String(value).toUpperCase();
    }

    function safeJSON(value) {
        try {
            return JSON.stringify(value);
        } catch (_) {
            return "";
        }
    }

    /* ========================================================================
       QUERY / DISCOVERY CONTEXT
       ======================================================================== */

    function getDiscoveryContext() {
        const globalContext =
            window.ROBOMLM_TERMINAL_CONTEXT ||
            window.ROBOMLM_DISCOVERY_CONTEXT;

        if (globalContext && typeof globalContext === "object") {
            const value =
                typeof globalContext.get === "function"
                    ? globalContext.get()
                    : globalContext;

            if (value && typeof value === "object") {
                return value;
            }
        }

        const params = new URLSearchParams(window.location.search);

        return {
            symbol: params.get("symbol") || "BTC/USDT",
            market: params.get("market") || "",
            instrument: params.get("instrument") || "",
            timeframe:
                params.get("timeframe") ||
                params.get("tf") ||
                "1m"
        };
    }

    function currentSymbol() {
        const context = getDiscoveryContext();

        return (
            context.symbol ||
            $("#symbol-select")?.value ||
            "BTC/USDT"
        );
    }

    function currentTimeframe() {
        const context = getDiscoveryContext();

        return (
            context.timeframe ||
            document.querySelector("[data-tf].active")?.dataset.tf ||
            "1m"
        );
    }

    function buildTerminalURL() {
        const params = new URLSearchParams();

        params.set("symbol", currentSymbol());
        params.set("timeframe", currentTimeframe());

        const context = getDiscoveryContext();

        if (context.market) {
            params.set("market", context.market);
        }

        if (context.instrument) {
            params.set("instrument", context.instrument);
        }

        return `${CONFIG.terminal}?${params.toString()}`;
    }

    /* ========================================================================
       API
       ======================================================================== */

    async function fetchJSON(url, options = {}) {
        const response = await fetch(url, {
            cache: "no-store",
            credentials: "same-origin",
            ...options
        });

        let data = null;

        try {
            data = await response.json();
        } catch (_) {
            data = null;
        }

        if (!response.ok) {
            const message =
                data?.message ||
                data?.error ||
                `HTTP ${response.status}`;

            throw new Error(message);
        }

        return data;
    }

    async function fetchTerminal() {
        const symbol = currentSymbol();
        const timeframe = currentTimeframe();
        const context = getDiscoveryContext();

        const params = new URLSearchParams();

        params.set("symbol", symbol);
        params.set("timeframe", timeframe);

        if (context.market) {
            params.set("market", context.market);
        }

        if (context.instrument) {
            params.set("instrument", context.instrument);
        }

        return fetchJSON(`${CONFIG.terminal}?${params.toString()}`);
    }

    async function fetchContext() {
        const symbol = currentSymbol();
        const timeframe = currentTimeframe();
        const context = getDiscoveryContext();

        const params = new URLSearchParams();

        params.set("symbol", symbol);
        params.set("timeframe", timeframe);

        if (context.market) {
            params.set("market", context.market);
        }

        if (context.instrument) {
            params.set("instrument", context.instrument);
        }

        return fetchJSON(`${CONFIG.context}?${params.toString()}`);
    }

    async function fetchFrontendMap() {
        return fetchJSON(CONFIG.frontendMap);
    }

    /* ========================================================================
       RESULT NORMALIZATION
       ======================================================================== */

    function unwrapResult(payload) {
        if (!payload || typeof payload !== "object") {
            return {};
        }

        if (
            payload.result &&
            typeof payload.result === "object" &&
            !Array.isArray(payload.result)
        ) {
            return {
                ...payload,
                ...payload.result
            };
        }

        if (
            payload.data &&
            typeof payload.data === "object" &&
            !Array.isArray(payload.data)
        ) {
            return {
                ...payload,
                ...payload.data
            };
        }

        return payload;
    }

    function findSection(result, names) {
        for (const name of names) {
            if (
                result[name] !== undefined &&
                result[name] !== null
            ) {
                return result[name];
            }
        }

        return null;
    }

    function normalizeTerminalResult(payload) {
        const root = unwrapResult(payload);

        const market = object(
            findSection(root, [
                "market",
                "market_context",
                "marketContext"
            ])
        );

        const evidence = object(
            findSection(root, [
                "evidence",
                "evidence_strip",
                "evidenceStrip"
            ])
        );

        const intelligence = object(
            findSection(root, [
                "intelligence",
                "intelligence_panel",
                "intelligencePanel"
            ])
        );

        const decision = object(
            findSection(root, [
                "decision",
                "decision_outlook",
                "decisionOutlook"
            ])
        );

        const risk = object(
            findSection(root, [
                "risk",
                "risk_panel",
                "riskPanel"
            ])
        );

        const cas = object(
            findSection(root, [
                "cas",
                "cas_status",
                "casStatus"
            ])
        );

        return {
            root,
            market,
            evidence,
            intelligence,
            decision,
            risk,
            cas
        };
    }

    /* ========================================================================
       MARKET
       ======================================================================== */

    function renderMarket(normalized) {
        const root = normalized.root;
        const market = normalized.market;

        const symbol = firstDefined(
            root.symbol,
            market.symbol,
            currentSymbol()
        );

        const price = firstDefined(
            root.price,
            market.price,
            market.last_price,
            market.lastPrice,
            market.current_price,
            market.currentPrice
        );

        const change = firstDefined(
            root.change,
            root.change_pct,
            root.changePercent,
            market.change,
            market.change_pct,
            market.changePercent,
            market.percent_change,
            market.percentChange
        );

        const state = firstDefined(
            root.market_state,
            root.marketState,
            market.state,
            market.market_state,
            market.marketState
        );

        setText("#sb-price", price);
        setText("#sb-change", change);
        setText("#state-badge", state);

        const symbolControl = $("#symbol-select");

        if (symbolControl && symbol) {
            /*
             * Only restore the value if the option already exists.
             * Never create synthetic instruments in the frontend.
             */
            const optionExists =
                Array.from(symbolControl.options || []).some(
                    option => option.value === String(symbol)
                );

            if (optionExists) {
                symbolControl.value = String(symbol);
            }
        }
    }

    /* ========================================================================
       PORTFOLIO
       ======================================================================== */

    function renderPortfolio(root) {
        const portfolio = object(
            firstDefined(
                root.portfolio,
                root.account,
                root.position
            )
        );

        setText(
            "#pf-capital",
            firstDefined(
                portfolio.capital,
                portfolio.starting_capital,
                portfolio.startingCapital
            )
        );

        setText(
            "#pf-balance",
            firstDefined(
                portfolio.balance,
                portfolio.equity,
                portfolio.account_balance,
                portfolio.accountBalance
            )
        );

        setText(
            "#pf-pnl",
            firstDefined(
                portfolio.pnl,
                portfolio.total_pnl,
                portfolio.totalPnl
            )
        );

        setText(
            "#pf-open",
            firstDefined(
                portfolio.open,
                portfolio.open_positions,
                portfolio.openPositions
            )
        );

        setText(
            "#pf-winrate",
            firstDefined(
                portfolio.winrate,
                portfolio.win_rate,
                portfolio.winRate
            )
        );

        setText(
            "#pf-mode",
            firstDefined(
                portfolio.mode,
                root.mode
            )
        );

        renderPositions(
            firstDefined(
                portfolio.positions,
                root.positions
            )
        );
    }

    function renderPositions(positions) {
        const container = $("#pf-pos-list");

        if (!container) return;

        const rows = array(positions);

        if (!rows.length) {
            container.innerHTML = "";
            return;
        }

        container.innerHTML = rows
            .map(position => {
                const p = object(position);

                const symbol = firstDefined(
                    p.symbol,
                    p.instrument,
                    ""
                );

                const direction = upper(
                    firstDefined(
                        p.direction,
                        p.side,
                        ""
                    )
                );

                const entry = firstDefined(
                    p.entry,
                    p.entry_price,
                    p.entryPrice
                );

                const pnl = firstDefined(
                    p.pnl,
                    p.unrealized_pnl,
                    p.unrealizedPnl
                );

                return `
                    <div class="terminal-position-row">
                        <span>${escapeHTML(symbol)}</span>
                        <span>${escapeHTML(direction)}</span>
                        <span>${escapeHTML(entry)}</span>
                        <span>${escapeHTML(pnl)}</span>
                    </div>
                `;
            })
            .join("");
    }

    /* ========================================================================
       EVIDENCE
       ======================================================================== */

    function renderEvidence(normalized) {
        const root = normalized.root;
        const evidence = normalized.evidence;

        const container = $("#evidence-strip");

        if (!container) return;

        const items = firstDefined(
            evidence.items,
            evidence.evidence,
            root.evidence_items,
            root.evidenceItems
        );

        if (Array.isArray(items)) {
            renderEvidenceItems(container, items);
            return;
        }

        /*
         * If backend provides an already formatted evidence payload,
         * preserve it rather than inventing evidence.
         */
        if (Array.isArray(evidence.cards)) {
            renderEvidenceItems(container, evidence.cards);
            return;
        }

        if (evidence.html) {
            container.innerHTML = evidence.html;
            return;
        }

        /*
         * Do not manufacture evidence when backend did not provide it.
         */
        container.innerHTML = "";
    }

    function renderEvidenceItems(container, items) {
        container.innerHTML = items
            .map(item => {
                const e = object(item);

                const id = firstDefined(
                    e.id,
                    e.code,
                    e.name,
                    "EVIDENCE"
                );

                const value = firstDefined(
                    e.value,
                    e.score,
                    e.status,
                    ""
                );

                const status = firstDefined(
                    e.status,
                    e.quality,
                    ""
                );

                return `
                    <div class="terminal-evidence-item">
                        <span class="terminal-evidence-id">
                            ${escapeHTML(id)}
                        </span>
                        <span class="terminal-evidence-value">
                            ${escapeHTML(value)}
                        </span>
                        <span class="terminal-evidence-status">
                            ${escapeHTML(status)}
                        </span>
                    </div>
                `;
            })
            .join("");
    }

    /* ========================================================================
       INTELLIGENCE / METRICS
       ======================================================================== */

    function renderIntelligence(normalized) {
        const root = normalized.root;
        const intelligence = normalized.intelligence;

        const metrics = firstDefined(
            root.metrics,
            intelligence.metrics,
            intelligence.items
        );

        if (!Array.isArray(metrics)) {
            return;
        }

        const container = $("#metrics-strip");

        if (!container) return;

        container.innerHTML = metrics
            .map(metric => {
                const m = object(metric);

                return `
                    <div class="terminal-metric">
                        <span class="terminal-metric-name">
                            ${escapeHTML(
                                firstDefined(
                                    m.name,
                                    m.id,
                                    "Metric"
                                )
                            )}
                        </span>
                        <span class="terminal-metric-value">
                            ${escapeHTML(
                                firstDefined(
                                    m.score,
                                    m.value,
                                    ""
                                )
                            )}
                        </span>
                        <span class="terminal-metric-status">
                            ${escapeHTML(
                                firstDefined(
                                    m.status,
                                    ""
                                )
                            )}
                        </span>
                    </div>
                `;
            })
            .join("");
    }

    /* ========================================================================
       DECISION / D13
       ======================================================================== */

    function renderDecision(normalized) {
        const root = normalized.root;
        const decision = normalized.decision;

        const decisionValue = firstDefined(
            decision.decision,
            decision.status,
            root.decision
        );

        const direction = firstDefined(
            decision.direction,
            root.direction
        );

        const confidence = firstDefined(
            decision.confidence,
            decision.confidence_score,
            decision.confidenceScore,
            root.confidence
        );

        const grade = firstDefined(
            decision.grade,
            decision.quality_grade,
            decision.qualityGrade,
            root.grade
        );

        const rr = firstDefined(
            decision.rr,
            decision.risk_reward,
            decision.riskReward,
            root.rr
        );

        const reason = firstDefined(
            decision.reason,
            decision.reason_text,
            decision.reasonText,
            decision.gate_reasons,
            decision.gateReasons
        );

        const advisory = firstDefined(
            decision.advisory,
            decision.explanation,
            decision.explainer
        );

        setText("#decision-box", decisionValue);

        setText(
            "#d13-signal-text",
            firstDefined(
                direction,
                decisionValue
            )
        );

        setText("#d13-conf", formatScore(confidence));
        setText("#d13-grade", grade);
        setText("#d13-rr", rr);
        setText("#decision-reason", formatReason(reason));
        setText("#d13-advisory", advisory);

        updateDecisionProgress(confidence);

        /*
         * HOLD remains HOLD.
         * No frontend transformation into BUY/SELL is allowed.
         */
        const signalBox = $("#d13-signal-box");

        if (signalBox) {
            signalBox.dataset.decision =
                upper(decisionValue || "UNKNOWN");

            signalBox.dataset.direction =
                upper(direction || "UNKNOWN");
        }
    }

    function formatScore(value) {
        const n = number(value, null);

        if (n === null) return value;

        return n <= 1
            ? `${(n * 100).toFixed(1)}%`
            : `${n.toFixed(1)}%`;
    }

    function updateDecisionProgress(value) {
        const bar = $("#decision-progress-bar");

        if (!bar) return;

        const n = number(value, null);

        if (n === null) {
            bar.style.width = "0%";
            return;
        }

        const percentage = n <= 1 ? n * 100 : clamp(n, 0, 100);

        bar.style.width = `${percentage}%`;
    }

    function formatReason(value) {
        if (Array.isArray(value)) {
            return value.join(" | ");
        }

        if (value && typeof value === "object") {
            return Object.entries(value)
                .map(([key, val]) => `${key}: ${val}`)
                .join(" | ");
        }

        return value;
    }

    /* ========================================================================
       RISK
       ======================================================================== */

    function renderRisk(normalized) {
        const root = normalized.root;
        const risk = normalized.risk;

        const riskPayload = {
            ...risk
        };

        /*
         * Risk is displayed only.
         * Frontend never approves or modifies risk.
         */
        if (riskPayload.status !== undefined) {
            setText("#decision-risk-status", riskPayload.status);
        }

        if (riskPayload.score !== undefined) {
            setText("#decision-risk-score", riskPayload.score);
        }

        /*
         * Manual TP/SL fields are intentionally NOT populated from
         * arbitrary frontend calculations.
         *
         * If the backend provides authorized values, expose them.
         */
        const tp = firstDefined(
            risk.take_profit,
            risk.takeProfit,
            risk.tp
        );

        const sl = firstDefined(
            risk.stop_loss,
            risk.stopLoss,
            risk.sl
        );

        if (tp !== null) {
            const el = $("#in-tp");

            if (el && !el.matches(":focus")) {
                el.value = tp;
            }
        }

        if (sl !== null) {
            const el = $("#in-sl");

            if (el && !el.matches(":focus")) {
                el.value = sl;
            }
        }

        /*
         * Keep root referenced so this function can evolve with the
         * backend contract without creating another risk engine.
         */
        void root;
    }

    /* ========================================================================
       CAS
       ======================================================================== */

    function renderCAS(normalized) {
        const root = normalized.root;
        const cas = normalized.cas;

        const status = firstDefined(
            cas.status,
            cas.state,
            cas.result,
            root.cas_status,
            root.casStatus
        );

        const approved = firstDefined(
            cas.approved,
            cas.authorized,
            cas.allowed
        );

        const reason = firstDefined(
            cas.reason,
            cas.reasons,
            cas.gate_reasons,
            cas.gateReasons
        );

        const container = $("#p-cas");

        if (!container) return;

        let text = "";

        if (status !== null) {
            text = String(status);
        }

        if (approved !== null) {
            text += text
                ? ` | ${approved ? "AUTHORIZED" : "NOT AUTHORIZED"}`
                : approved
                    ? "AUTHORIZED"
                    : "NOT AUTHORIZED";
        }

        if (reason) {
            text += text
                ? ` | ${formatReason(reason)}`
                : formatReason(reason);
        }

        /*
         * No CAS result = no fabricated approval.
         */
        container.textContent =
            text || "CAS STATUS UNAVAILABLE";
    }

    /* ========================================================================
       TRADE BUTTON SAFETY
       ======================================================================== */

    function renderTradeControls(normalized) {
        const decision = normalized.decision;
        const cas = normalized.cas;

        const decisionValue = upper(
            firstDefined(
                decision.decision,
                decision.status,
                normalized.root.decision
            )
        );

        const direction = upper(
            firstDefined(
                decision.direction,
                normalized.root.direction
            )
        );

        const casApproved = firstDefined(
            cas.approved,
            cas.authorized,
            cas.allowed
        );

        const actionable =
            decisionValue &&
            decisionValue !== "HOLD" &&
            decisionValue !== "NEUTRAL";

        const callButton = $("#btn-call");
        const putButton = $("#btn-put");
        const confirmButton = $("#btn-confirm");

        /*
         * IMPORTANT:
         * Display state only.
         *
         * Actual trade authorization must remain backend/CAS owned.
         */
        if (callButton) {
            callButton.dataset.backendDirection = direction;
            callButton.dataset.casApproved =
                casApproved === true ? "true" : "false";
        }

        if (putButton) {
            putButton.dataset.backendDirection = direction;
            putButton.dataset.casApproved =
                casApproved === true ? "true" : "false";
        }

        if (confirmButton) {
            confirmButton.dataset.backendActionable =
                actionable ? "true" : "false";

            confirmButton.dataset.casApproved =
                casApproved === true ? "true" : "false";
        }
    }

    /* ========================================================================
       COMPLETE RENDER
       ======================================================================== */

    function render(payload) {
        state.lastResult = payload;

        const normalized = normalizeTerminalResult(payload);

        renderMarket(normalized);
        renderPortfolio(normalized.root);
        renderEvidence(normalized);
        renderIntelligence(normalized);
        renderDecision(normalized);
        renderRisk(normalized);
        renderCAS(normalized);
        renderTradeControls(normalized);

        updateLog(payload);
    }

    /* ========================================================================
       LOG
       ======================================================================== */

    function updateLog(payload) {
        const container = $("#p-log");

        if (!container) return;

        const root = unwrapResult(payload);

        const timestamp = firstDefined(
            root.timestamp,
            root.generated_at,
            root.generatedAt
        );

        const status = firstDefined(
            root.status,
            "OK"
        );

        container.dataset.backendStatus = String(status);

        if (timestamp) {
            container.dataset.timestamp = String(timestamp);
        }
    }

    /* ========================================================================
       ERROR STATE
       ======================================================================== */

    function renderError(error) {
        const message =
            error?.message ||
            "Terminal backend unavailable";

        const statusBadge = $("#state-badge");

        if (statusBadge) {
            statusBadge.textContent = "BACKEND ERROR";
        }

        const decisionBox = $("#decision-box");

        if (decisionBox) {
            decisionBox.textContent = "UNAVAILABLE";
        }

        const cas = $("#p-cas");

        if (cas) {
            cas.textContent = "CAS STATUS UNAVAILABLE";
        }

        const log = $("#p-log");

        if (log) {
            log.dataset.backendStatus = "ERROR";
            log.dataset.error = message;
        }

        console.error("[ROBOMLM] Terminal backend error:", error);
    }

    /* ========================================================================
       CONTEXT
       ======================================================================== */

    async function loadContext() {
        try {
            state.lastContext = await fetchContext();
            return state.lastContext;
        } catch (error) {
            /*
             * Context endpoint is supplemental.
             * Main Terminal API remains authoritative.
             */
            console.warn(
                "[ROBOMLM] Terminal context unavailable:",
                error
            );

            return null;
        }
    }

    /* ========================================================================
       FRONTEND MAP
       ======================================================================== */

    async function loadFrontendMap() {
        try {
            state.lastMap = await fetchFrontendMap();
            return state.lastMap;
        } catch (error) {
            console.warn(
                "[ROBOMLM] Terminal frontend map unavailable:",
                error
            );

            return null;
        }
    }

    /* ========================================================================
       REFRESH
       ======================================================================== */

    async function refresh() {
        if (state.loading) {
            return state.lastResult;
        }

        state.loading = true;

        try {
            const result = await fetchTerminal();

            render(result);

            return result;
        } catch (error) {
            renderError(error);
            return null;
        } finally {
            state.loading = false;
        }
    }

    function startAutoRefresh() {
        stopAutoRefresh();

        state.timer = window.setInterval(
            refresh,
            CONFIG.refreshMs
        );
    }

    function stopAutoRefresh() {
        if (state.timer !== null) {
            window.clearInterval(state.timer);
            state.timer = null;
        }
    }

    /* ========================================================================
       TIMEFRAME EVENTS
       ======================================================================== */

    function bindTimeframes() {
        document
            .querySelectorAll("[data-tf]")
            .forEach(button => {
                button.addEventListener("click", function () {
                    const tf = this.dataset.tf;

                    if (!tf) return;

                    /*
                     * If the discovery context helper exists, let it remain
                     * the owner of persistent context.
                     */
                    const context =
                        window.ROBOMLM_DISCOVERY_CONTEXT;

                    if (
                        context &&
                        typeof context.save === "function"
                    ) {
                        const current =
                            getDiscoveryContext();

                        context.save({
                            ...current,
                            timeframe: tf
                        });
                    }

                    window.setTimeout(
                        refresh,
                        0
                    );
                });
            });
    }

    /* ========================================================================
       SYMBOL EVENTS
       ======================================================================== */

    function bindSymbol() {
        const symbolSelect = $("#symbol-select");

        if (!symbolSelect) return;

        symbolSelect.addEventListener(
            "change",
            function () {
                const symbol = this.value;

                const context =
                    window.ROBOMLM_DISCOVERY_CONTEXT;

                if (
                    context &&
                    typeof context.save === "function"
                ) {
                    const current =
                        getDiscoveryContext();

                    context.save({
                        ...current,
                        symbol
                    });
                }

                refresh();
            }
        );
    }

    /* ========================================================================
       DISCOVERY RESTORE EVENT
       ======================================================================== */

    function bindDiscoveryContext() {
        window.addEventListener(
            "robomlm:discovery-context-restored",
            function () {
                refresh();
            }
        );
    }

    /* ========================================================================
       PUBLIC API
       ======================================================================== */

    const api = {
        config: CONFIG,
        state,

        refresh,
        render,
        loadContext,
        loadFrontendMap,

        getContext: getDiscoveryContext,
        getSymbol: currentSymbol,
        getTimeframe: currentTimeframe,
        buildURL: buildTerminalURL,

        startAutoRefresh,
        stopAutoRefresh
    };

    window.ROBOMLM_TERMINAL_BACKEND = api;

    /* ========================================================================
       INIT
       ======================================================================== */

    function init() {
        if (state.initialized) {
            return api;
        }

        state.initialized = true;

        bindTimeframes();
        bindSymbol();
        bindDiscoveryContext();

        /*
         * Main Terminal result first.
         * Context/map are supplementary and must never block the main result.
         */
        refresh();

        loadContext();
        loadFrontendMap();

        startAutoRefresh();

        return api;
    }

    function escapeHTML(value) {
        if (value === undefined || value === null) {
            return "";
        }

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            init,
            { once: true }
        );
    } else {
        init();
    }

})();
```javascript
/* ============================================================================
   ROBOMLM TERMINAL BACKEND — PART 6
   REAL MARKET CHART WIRING

   File:
       web/static/js/terminal_backend.js

   Purpose:
       Existing #chart DOM ko real backend candle data se connect karna.

   Rules:
       - No random candles
       - No synthetic market data
       - No BUY / SELL generation
       - No D13 calculation
       - No EQE calculation
       - No Risk calculation
       - No CAS calculation
       - Existing backend remains authoritative
============================================================================ */

(function () {
    "use strict";

    const CHART_CONFIG = {
        endpoint: "/api/live/candles",
        defaultLimit: 120,
        refreshMs: 5000,
        minCandles: 2
    };

    let chartState = {
        candles: [],
        symbol: null,
        timeframe: null,
        loading: false,
        lastUpdated: null,
        error: null
    };

    function chartElement() {
        return document.getElementById("chart");
    }

    function safeNumber(value, fallback = null) {
        const n = Number(value);
        return Number.isFinite(n) ? n : fallback;
    }

    function normaliseSymbol(symbol) {
        return String(symbol || "")
            .trim()
            .replace("-", "/")
            .replace("_", "/")
            .toUpperCase();
    }

    function currentTerminalContext() {
        const ctx = window.ROBOMLM_TERMINAL_CONTEXT || {};
        const params = new URLSearchParams(window.location.search);

        const symbol =
            ctx.symbol ||
            params.get("symbol") ||
            document.getElementById("symbol-select")?.value ||
            "BTC/USDT";

        const timeframe =
            ctx.timeframe ||
            params.get("timeframe") ||
            params.get("tf") ||
            document.querySelector("[data-tf].active")?.dataset?.tf ||
            document.querySelector("[data-tf][aria-selected='true']")?.dataset?.tf ||
            "1m";

        return {
            symbol: normaliseSymbol(symbol),
            timeframe: String(timeframe || "1m")
        };
    }

    function timeframeToBackendValue(timeframe) {
        const value = String(timeframe || "1m").trim().toLowerCase();

        const map = {
            "1m": "1",
            "3m": "3",
            "5m": "5",
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "2h": "120",
            "4h": "240",
            "6h": "360",
            "12h": "720",
            "1d": "D",
            "1w": "W",
            "1mth": "M"
        };

        return map[value] || value;
    }

    function buildCandleUrl(context) {
        const params = new URLSearchParams();

        params.set("symbol", context.symbol);
        params.set(
            "timeframe",
            timeframeToBackendValue(context.timeframe)
        );
        params.set("limit", String(CHART_CONFIG.defaultLimit));

        return `${CHART_CONFIG.endpoint}?${params.toString()}`;
    }

    function extractCandleRows(payload) {
        if (!payload) {
            return [];
        }

        let rows = [];

        if (Array.isArray(payload)) {
            rows = payload;
        } else if (Array.isArray(payload.candles)) {
            rows = payload.candles;
        } else if (Array.isArray(payload.data)) {
            rows = payload.data;
        } else if (Array.isArray(payload.result)) {
            rows = payload.result;
        } else if (payload.result && Array.isArray(payload.result.list)) {
            rows = payload.result.list;
        }

        return rows
            .map(function (row) {
                /*
                 * Supported canonical/object form:
                 * {
                 *   timestamp,
                 *   open,
                 *   high,
                 *   low,
                 *   close,
                 *   volume
                 * }
                 */

                if (
                    row &&
                    typeof row === "object" &&
                    !Array.isArray(row)
                ) {
                    return {
                        timestamp: safeNumber(
                            row.timestamp ??
                            row.time ??
                            row.ts ??
                            row.startTime
                        ),
                        open: safeNumber(row.open),
                        high: safeNumber(row.high),
                        low: safeNumber(row.low),
                        close: safeNumber(row.close),
                        volume: safeNumber(row.volume, 0)
                    };
                }

                /*
                 * Bybit-style fallback:
                 * [timestamp, open, high, low, close, volume, ...]
                 *
                 * This does NOT create data. It only normalises an
                 * already-returned adapter response.
                 */
                if (Array.isArray(row) && row.length >= 5) {
                    return {
                        timestamp: safeNumber(row[0]),
                        open: safeNumber(row[1]),
                        high: safeNumber(row[2]),
                        low: safeNumber(row[3]),
                        close: safeNumber(row[4]),
                        volume: safeNumber(row[5], 0)
                    };
                }

                return null;
            })
            .filter(function (candle) {
                return (
                    candle &&
                    Number.isFinite(candle.timestamp) &&
                    Number.isFinite(candle.open) &&
                    Number.isFinite(candle.high) &&
                    Number.isFinite(candle.low) &&
                    Number.isFinite(candle.close) &&
                    candle.high >= candle.low
                );
            })
            .sort(function (a, b) {
                return a.timestamp - b.timestamp;
            });
    }

    function canvasContext() {
        const canvas = chartElement();

        if (!canvas) {
            return null;
        }

        /*
         * Existing #chart may be a canvas.
         * If it is not, do not replace the user's DOM.
         */
        if (typeof canvas.getContext !== "function") {
            return null;
        }

        return canvas.getContext("2d");
    }

    function resizeCanvas(canvas) {
        if (!canvas) {
            return;
        }

        const rect = canvas.getBoundingClientRect();

        const width = Math.max(
            320,
            Math.floor(rect.width || canvas.clientWidth || 900)
        );

        const height = Math.max(
            220,
            Math.floor(rect.height || canvas.clientHeight || 360)
        );

        const dpr = window.devicePixelRatio || 1;

        canvas.width = Math.floor(width * dpr);
        canvas.height = Math.floor(height * dpr);

        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
    }

    function drawEmptyChart(message) {
        const canvas = chartElement();
        const ctx = canvasContext();

        if (!canvas || !ctx) {
            return;
        }

        resizeCanvas(canvas);

        const width = canvas.clientWidth || 900;
        const height = canvas.clientHeight || 360;

        ctx.clearRect(0, 0, width, height);

        ctx.font = "13px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(
            message || "Market data unavailable",
            width / 2,
            height / 2
        );
    }

    function drawChart(candles) {
        const canvas = chartElement();
        const ctx = canvasContext();

        if (!canvas || !ctx) {
            return;
        }

        if (!Array.isArray(candles) || candles.length < CHART_CONFIG.minCandles) {
            drawEmptyChart("Insufficient market data");
            return;
        }

        resizeCanvas(canvas);

        const width = canvas.clientWidth || 900;
        const height = canvas.clientHeight || 360;

        ctx.clearRect(0, 0, width, height);

        const padding = {
            left: 12,
            right: 58,
            top: 18,
            bottom: 28
        };

        const plotWidth =
            width - padding.left - padding.right;

        const plotHeight =
            height - padding.top - padding.bottom;

        const highs = candles.map(c => c.high);
        const lows = candles.map(c => c.low);

        let maxPrice = Math.max.apply(null, highs);
        let minPrice = Math.min.apply(null, lows);

        if (
            !Number.isFinite(maxPrice) ||
            !Number.isFinite(minPrice) ||
            maxPrice <= minPrice
        ) {
            drawEmptyChart("Invalid market range");
            return;
        }

        /*
         * Small visual breathing room.
         * This is presentation only and does not alter backend prices.
         */
        const range = maxPrice - minPrice;
        maxPrice += range * 0.04;
        minPrice -= range * 0.04;

        function xFor(index) {
            if (candles.length === 1) {
                return padding.left + plotWidth / 2;
            }

            return (
                padding.left +
                (index / (candles.length - 1)) * plotWidth
            );
        }

        function yFor(price) {
            return (
                padding.top +
                ((maxPrice - price) / (maxPrice - minPrice)) *
                    plotHeight
            );
        }

        /*
         * Grid.
         */
        ctx.save();
        ctx.lineWidth = 1;
        ctx.globalAlpha = 0.15;

        for (let i = 0; i <= 4; i++) {
            const y =
                padding.top +
                (i / 4) * plotHeight;

            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.stroke();
        }

        for (let i = 0; i <= 5; i++) {
            const x =
                padding.left +
                (i / 5) * plotWidth;

            ctx.beginPath();
            ctx.moveTo(x, padding.top);
            ctx.lineTo(x, height - padding.bottom);
            ctx.stroke();
        }

        ctx.restore();

        /*
         * Price labels.
         */
        ctx.save();
        ctx.font = "11px sans-serif";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";

        for (let i = 0; i <= 4; i++) {
            const price =
                maxPrice -
                ((maxPrice - minPrice) * i) / 4;

            const y =
                padding.top +
                (i / 4) * plotHeight;

            ctx.fillText(
                formatChartPrice(price),
                width - padding.right + 8,
                y
            );
        }

        ctx.restore();

        /*
         * Candle geometry.
         */
        const slotWidth =
            plotWidth / Math.max(candles.length, 1);

        const candleWidth = Math.max(
            1,
            Math.min(12, slotWidth * 0.62)
        );

        candles.forEach(function (candle, index) {
            const x = xFor(index);

            const openY = yFor(candle.open);
            const closeY = yFor(candle.close);
            const highY = yFor(candle.high);
            const lowY = yFor(candle.low);

            /*
             * Do not assign trading meaning to candle colour.
             * It simply represents OHLC direction.
             */
            ctx.beginPath();
            ctx.moveTo(x, highY);
            ctx.lineTo(x, lowY);
            ctx.stroke();

            const bodyTop = Math.min(openY, closeY);
            const bodyBottom = Math.max(openY, closeY);
            const bodyHeight = Math.max(
                1,
                bodyBottom - bodyTop
            );

            ctx.fillRect(
                x - candleWidth / 2,
                bodyTop,
                candleWidth,
                bodyHeight
            );
        });

        /*
         * Latest price line.
         */
        const latest = candles[candles.length - 1];

        if (latest && Number.isFinite(latest.close)) {
            const latestY = yFor(latest.close);

            ctx.save();
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(padding.left, latestY);
            ctx.lineTo(width - padding.right, latestY);
            ctx.stroke();
            ctx.restore();

            ctx.save();
            ctx.font = "11px sans-serif";
            ctx.textAlign = "left";
            ctx.textBaseline = "middle";
            ctx.fillText(
                formatChartPrice(latest.close),
                width - padding.right + 8,
                latestY
            );
            ctx.restore();
        }

        /*
         * Time labels.
         */
        const labelIndexes = [
            0,
            Math.floor((candles.length - 1) / 2),
            candles.length - 1
        ];

        ctx.save();
        ctx.font = "10px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "top";

        labelIndexes.forEach(function (index) {
            const candle = candles[index];

            if (!candle) {
                return;
            }

            const x = xFor(index);

            ctx.fillText(
                formatChartTime(candle.timestamp),
                x,
                height - padding.bottom + 8
            );
        });

        ctx.restore();
    }

    function formatChartPrice(value) {
        if (!Number.isFinite(value)) {
            return "—";
        }

        const absolute = Math.abs(value);

        if (absolute >= 1000) {
            return value.toLocaleString(undefined, {
                maximumFractionDigits: 2
            });
        }

        if (absolute >= 1) {
            return value.toLocaleString(undefined, {
                maximumFractionDigits: 4
            });
        }

        return value.toLocaleString(undefined, {
            maximumFractionDigits: 8
        });
    }

    function formatChartTime(timestamp) {
        if (!Number.isFinite(timestamp)) {
            return "";
        }

        const millis =
            timestamp < 100000000000
                ? timestamp * 1000
                : timestamp;

        const date = new Date(millis);

        if (Number.isNaN(date.getTime())) {
            return "";
        }

        return date.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });
    }

    function setChartStatus(message) {
        const canvas = chartElement();

        if (!canvas) {
            return;
        }

        canvas.dataset.chartStatus = String(message || "");
    }

    async function fetchChartData() {
        if (chartState.loading) {
            return chartState;
        }

        const canvas = chartElement();

        if (!canvas) {
            return chartState;
        }

        const context = currentTerminalContext();

        chartState.symbol = context.symbol;
        chartState.timeframe = context.timeframe;
        chartState.loading = true;
        chartState.error = null;

        try {
            const response = await fetch(
                buildCandleUrl(context),
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    cache: "no-store"
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Market candle request failed: HTTP ${response.status}`
                );
            }

            const payload = await response.json();

            const candles = extractCandleRows(payload);

            if (candles.length < CHART_CONFIG.minCandles) {
                chartState.candles = candles;
                chartState.error = "INSUFFICIENT_MARKET_DATA";

                drawEmptyChart(
                    "Insufficient market data"
                );

                setChartStatus(
                    "INSUFFICIENT_MARKET_DATA"
                );

                return chartState;
            }

            chartState.candles = candles;
            chartState.lastUpdated = new Date().toISOString();
            chartState.error = null;

            drawChart(candles);

            setChartStatus("LIVE");

            return chartState;
        } catch (error) {
            chartState.error =
                error instanceof Error
                    ? error.message
                    : String(error);

            /*
             * Important:
             * On failure we do NOT fabricate candles.
             * Existing chart is cleared rather than replaced with fake data.
             */
            drawEmptyChart("Market data unavailable");

            setChartStatus("ERROR");

            console.error(
                "[ROBOMLM] terminal chart error:",
                error
            );

            return chartState;
        } finally {
            chartState.loading = false;
        }
    }

    function bindChartRefresh() {
        if (window.__ROBOMLM_TERMINAL_CHART_BOUND__) {
            return;
        }

        window.__ROBOMLM_TERMINAL_CHART_BOUND__ = true;

        /*
         * Timeframe buttons.
         */
        document.querySelectorAll("[data-tf]").forEach(
            function (button) {
                button.addEventListener("click", function () {
                    window.setTimeout(
                        fetchChartData,
                        0
                    );
                });
            }
        );

        /*
         * Symbol selector.
         */
        const symbolSelect =
            document.getElementById("symbol-select");

        if (symbolSelect) {
            symbolSelect.addEventListener(
                "change",
                function () {
                    window.setTimeout(
                        fetchChartData,
                        0
                    );
                }
            );
        }

        /*
         * Discovery → Terminal restoration.
         */
        window.addEventListener(
            "robomlm:discovery-context-restored",
            function () {
                window.setTimeout(
                    fetchChartData,
                    0
                );
            }
        );

        /*
         * Responsive redraw.
         */
        window.addEventListener(
            "resize",
            function () {
                if (
                    Array.isArray(chartState.candles) &&
                    chartState.candles.length >=
                        CHART_CONFIG.minCandles
                ) {
                    drawChart(chartState.candles);
                }
            }
        );

        /*
         * Initial chart.
         */
        fetchChartData();

        /*
         * Real-data refresh.
         */
        window.setInterval(
            fetchChartData,
            CHART_CONFIG.refreshMs
        );
    }

    function initTerminalChart() {
        if (!chartElement()) {
            return;
        }

        bindChartRefresh();
    }

    /*
     * Public API for terminal.js / future existing frontend code.
     */
    window.ROBOMLM_TERMINAL_CHART = {
        init: initTerminalChart,
        refresh: fetchChartData,
        redraw: function () {
            drawChart(chartState.candles);
        },
        getState: function () {
            return {
                symbol: chartState.symbol,
                timeframe: chartState.timeframe,
                candleCount: chartState.candles.length,
                loading: chartState.loading,
                lastUpdated: chartState.lastUpdated,
                error: chartState.error
            };
        }
    };

    /*
     * DOM-ready.
     */
    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initTerminalChart,
            { once: true }
        );
    } else {
        initTerminalChart();
    }
})();
```
