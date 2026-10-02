/*
 * ROBOMLM_PLUS
 * Discovery Backend Frontend Controller
 *
 * Purpose:
 *
 * Existing /discovery page
 *        |
 *        v
 * /api/discovery
 *        |
 *        +--> Universe
 *        +--> Liquidity
 *        +--> Risk
 *        +--> Timing
 *        +--> Scanner
 *        +--> Ranking
 *        +--> Top10
 *        +--> Opportunity
 *
 * Discovery ONLY.
 *
 * This file does NOT:
 *   - calculate EQE
 *   - calculate D13
 *   - create BUY/SELL decisions
 *   - place orders
 *   - call broker execution
 *   - bypass Risk
 *   - bypass CAS
 *
 * It only renders backend results.
 */

"use strict";


/* ============================================================
   CONFIGURATION
   ============================================================ */

const DISCOVERY_CONFIG = Object.freeze({
    base: "/api/discovery",

    pipelineEndpoint: "/api/discovery",
    backendMapEndpoint: "/api/discovery/backend-map",
    healthEndpoint: "/api/discovery/health",

    opportunityEndpoint: (symbol) =>
        `/api/discovery/opportunity/${encodeURIComponent(symbol)}`,

    refreshMs: 30000,

    defaultTimeframe: "1m",
    defaultLimit: 10,
});


/* ============================================================
   STATE
   ============================================================ */

const DiscoveryState = {
    loading: false,
    requestId: 0,

    market: null,
    instrument: null,
    universe: null,
    timeframe: DISCOVERY_CONFIG.defaultTimeframe,
    limit: DISCOVERY_CONFIG.defaultLimit,

    result: null,

    stages: {
        universe: null,
        liquidity: null,
        risk: null,
        timing: null,
        scanner: null,
        ranking: null,
        top10: null,
        opportunity: null,
    },

    selectedSymbol: null,

    error: null,
};


/* ============================================================
   DOM HELPERS
   ============================================================ */

function discoveryElement(selector) {
    return document.querySelector(selector);
}


function discoveryElements(selector) {
    return Array.from(
        document.querySelectorAll(selector)
    );
}


function setText(selector, value) {
    const element = discoveryElement(selector);

    if (!element) {
        return;
    }

    element.textContent =
        value === null ||
        value === undefined ||
        value === ""
            ? "—"
            : String(value);
}


function setHTML(selector, html) {
    const element = discoveryElement(selector);

    if (!element) {
        return;
    }

    element.innerHTML = html;
}


function escapeHTML(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* ============================================================
   LOADING STATE
   ============================================================ */

function setDiscoveryLoading(loading) {
    DiscoveryState.loading = Boolean(loading);

    document.body.dataset.discoveryLoading =
        loading ? "true" : "false";

    discoveryElements(
        "[data-discovery-loading]"
    ).forEach((element) => {
        element.hidden = !loading;
    });

    discoveryElements(
        "[data-discovery-content]"
    ).forEach((element) => {
        element.hidden = Boolean(loading);
    });

    discoveryElements(
        "[data-discovery-refresh]"
    ).forEach((element) => {
        element.disabled = Boolean(loading);
    });

    setText(
        "[data-discovery-status]",
        loading
            ? "Loading Discovery…"
            : "Ready"
    );
}


/* ============================================================
   ERROR STATE
   ============================================================ */

function showDiscoveryError(message) {
    DiscoveryState.error = message;

    discoveryElements(
        "[data-discovery-error]"
    ).forEach((element) => {
        element.hidden = false;
        element.textContent = message;
    });

    setText(
        "[data-discovery-status]",
        "Discovery unavailable"
    );
}


function clearDiscoveryError() {
    DiscoveryState.error = null;

    discoveryElements(
        "[data-discovery-error]"
    ).forEach((element) => {
        element.hidden = true;
        element.textContent = "";
    });
}


/* ============================================================
   HTTP
   ============================================================ */

async function discoveryFetch(
    url,
    options = {}
) {
    const response = await fetch(
        url,
        {
            credentials: "same-origin",
            headers: {
                "Accept": "application/json",
                ...(options.headers || {}),
            },
            ...options,
        }
    );

    let payload = null;

    try {
        payload = await response.json();
    } catch (_) {
        payload = null;
    }

    if (!response.ok) {
        const message =
            payload?.detail?.message ||
            payload?.detail ||
            payload?.message ||
            `HTTP ${response.status}`;

        throw new Error(
            String(message)
        );
    }

    return payload;
}


/* ============================================================
   QUERY BUILDING
   ============================================================ */

function buildDiscoveryQuery() {
    const params = new URLSearchParams();

    if (DiscoveryState.market) {
        params.set(
            "market",
            DiscoveryState.market
        );
    }

    if (DiscoveryState.instrument) {
        params.set(
            "instrument",
            DiscoveryState.instrument
        );
    }

    if (DiscoveryState.universe) {
        params.set(
            "universe",
            DiscoveryState.universe
        );
    }

    params.set(
        "timeframe",
        DiscoveryState.timeframe ||
            DISCOVERY_CONFIG.defaultTimeframe
    );

    params.set(
        "limit",
        String(
            DiscoveryState.limit ||
                DISCOVERY_CONFIG.defaultLimit
        )
    );

    return params.toString();
}


/* ============================================================
   STAGE STATUS
   ============================================================ */

function stageStatusValue(stage) {
    if (!stage) {
        return "UNKNOWN";
    }

    if (typeof stage === "string") {
        return stage;
    }

    return (
        stage.status ||
        stage.state ||
        "UNKNOWN"
    );
}


function stageLabel(status) {
    const normalized =
        String(status || "UNKNOWN")
            .toUpperCase();

    switch (normalized) {
        case "READY":
        case "PASS":
        case "VALID":
            return "READY";

        case "PARTIAL":
        case "REVIEW":
        case "REVIEW_REQUIRED":
            return "REVIEW";

        case "BLOCK":
        case "REJECT":
        case "REJECTED":
            return "BLOCKED";

        case "ERROR":
            return "ERROR";

        case "UNAVAILABLE":
        case "NOT_EXPOSED":
            return "NOT WIRED";

        default:
            return normalized;
    }
}


function renderStageStatus(
    stageName,
    stageData
) {
    const status =
        stageStatusValue(stageData);

    const label =
        stageLabel(status);

    discoveryElements(
        `[data-discovery-stage="${stageName}"]`
    ).forEach((element) => {
        element.dataset.status =
            label;

        const statusElement =
            element.querySelector(
                "[data-stage-status]"
            );

        if (statusElement) {
            statusElement.textContent =
                label;
        }
    });
}


/* ============================================================
   PIPELINE STAGE VISIBILITY
   ============================================================ */

function renderStages(result) {
    const stages =
        result?.stages || {};

    DiscoveryState.stages =
        {
            universe:
                stages.universe || null,

            liquidity:
                stages.liquidity || null,

            risk:
                stages.risk || null,

            timing:
                stages.timing || null,

            scanner:
                stages.scanner || null,

            ranking:
                stages.ranking || null,

            top10:
                stages.top10 || null,

            opportunity:
                stages.opportunity || null,
        };

    Object.entries(
        DiscoveryState.stages
    ).forEach(
        ([name, data]) => {
            renderStageStatus(
                name,
                data
            );
        }
    );

    setText(
        "[data-stage-universe-count]",
        countRows(
            stages.universe
        )
    );

    setText(
        "[data-stage-liquidity-count]",
        countRows(
            stages.liquidity
        )
    );

    setText(
        "[data-stage-risk-count]",
        countRows(
            stages.risk
        )
    );

    setText(
        "[data-stage-timing-count]",
        countRows(
            stages.timing
        )
    );

    setText(
        "[data-stage-scanner-count]",
        countRows(
            stages.scanner
        )
    );

    setText(
        "[data-stage-ranking-count]",
        countRows(
            stages.ranking
        )
    );

    setText(
        "[data-stage-top10-count]",
        countRows(
            stages.top10
        )
    );
}


/* ============================================================
   ROW EXTRACTION
   ============================================================ */

function unwrapBackendResult(value) {
    if (
        value &&
        typeof value === "object" &&
        !Array.isArray(value) &&
        Object.prototype.hasOwnProperty.call(
            value,
            "result"
        )
    ) {
        return value.result;
    }

    return value;
}


function rowsFromStage(value) {
    value =
        unwrapBackendResult(
            value
        );

    if (Array.isArray(value)) {
        return value;
    }

    if (
        value &&
        typeof value === "object"
    ) {
        const keys = [
            "rows",
            "items",
            "opportunities",
            "candidates",
            "results",
            "data",
        ];

        for (const key of keys) {
            if (
                Array.isArray(
                    value[key]
                )
            ) {
                return value[key];
            }
        }

        return [value];
    }

    return [];
}


function countRows(value) {
    return rowsFromStage(
        value
    ).length;
}


/* ============================================================
   TOP10 NORMALISATION
   ============================================================ */

function normaliseTop10(result) {
    let rows =
        result?.top10;

    if (!Array.isArray(rows)) {
        rows =
            rowsFromStage(
                result?.stages?.top10
            );
    }

    return rows.map(
        (row, index) => {
            if (
                row === null ||
                row === undefined
            ) {
                return {
                    rank: index + 1,
                };
            }

            if (
                typeof row !== "object"
            ) {
                return {
                    rank: index + 1,
                    symbol: String(row),
                };
            }

            return {
                rank:
                    row.rank ??
                    row.position ??
                    index + 1,

                symbol:
                    row.symbol ??
                    row.ticker ??
                    row.asset ??
                    row.instrument_symbol ??
                    "—",

                market:
                    row.market ??
                    row.market_type ??
                    "—",

                score:
                    row.score ??
                    row.ranking_score ??
                    row.opportunity_score ??
                    row.rank_score ??
                    null,

                eqe:
                    row.eqe ??
                    row.eqe_score ??
                    null,

                risk:
                    row.risk ??
                    row.risk_level ??
                    null,

                timing:
                    row.timing ??
                    row.timing_status ??
                    null,

                liquidity:
                    row.liquidity ??
                    row.liquidity_status ??
                    null,

                ...row,
            };
        }
    );
}


/* ============================================================
   DISCOVERY DIRECTION SAFETY
   ============================================================ */

function discoveryDisplayDirection(row) {
    /*
     * Discovery must not manufacture BUY/SELL.

     If the backend itself contains a directional field,
     display it only as backend-provided discovery metadata.

     Otherwise show DISCOVERY.
     */

    if (!row) {
        return "DISCOVERY";
    }

    const raw =
        row.direction ??
        row.bias ??
        row.discovery_direction ??
        null;

    if (
        raw === null ||
        raw === undefined ||
        raw === ""
    ) {
        return "DISCOVERY";
    }

    return String(raw);
}


/* ============================================================
   TOP10 RENDER
   ============================================================ */

function renderTop10(result) {
    const container =
        discoveryElement(
            "[data-discovery-top10]"
        );

    if (!container) {
        return;
    }

    const rows =
        normaliseTop10(
            result
        );

    if (!rows.length) {
        container.innerHTML = `
            <div class="discovery-empty">
                No qualifying opportunities returned.
            </div>
        `;

        setText(
            "[data-discovery-top10-count]",
            "0"
        );

        return;
    }

    const html =
        rows
            .slice(0, 10)
            .map(
                (row, index) => {
                    const symbol =
                        row.symbol ||
                        "—";

                    const score =
                        row.score;

                    const scoreText =
                        score === null ||
                        score === undefined
                            ? "—"
                            : score;

                    const risk =
                        row.risk ?? "—";

                    const timing =
                        row.timing ?? "—";

                    const liquidity =
                        row.liquidity ?? "—";

                    const direction =
                        discoveryDisplayDirection(
                            row
                        );

                    return `
                        <div
                            class="discovery-top10-row"
                            data-discovery-opportunity
                            data-symbol="${escapeHTML(symbol)}"
                            tabindex="0"
                            role="button"
                            aria-label="Open opportunity ${escapeHTML(symbol)}"
                        >
                            <div
                                class="discovery-rank"
                            >
                                ${index + 1}
                            </div>

                            <div
                                class="discovery-symbol"
                            >
                                ${escapeHTML(symbol)}
                            </div>

                            <div
                                class="discovery-market"
                            >
                                ${escapeHTML(row.market ?? "—")}
                            </div>

                            <div
                                class="discovery-score"
                            >
                                ${escapeHTML(scoreText)}
                            </div>

                            <div
                                class="discovery-risk"
                            >
                                ${escapeHTML(risk)}
                            </div>

                            <div
                                class="discovery-timing"
                            >
                                ${escapeHTML(timing)}
                            </div>

                            <div
                                class="discovery-liquidity"
                            >
                                ${escapeHTML(liquidity)}
                            </div>

                            <div
                                class="discovery-direction"
                            >
                                ${escapeHTML(direction)}
                            </div>

                            <button
                                type="button"
                                class="discovery-detail-button"
                                data-discovery-open="${escapeHTML(symbol)}"
                            >
                                View Opportunity
                            </button>
                        </div>
                    `;
                }
            )
            .join("");

    container.innerHTML = html;

    setText(
        "[data-discovery-top10-count]",
        rows.length
    );

    bindOpportunityNavigation();
}


/* ============================================================
   OPPORTUNITY NAVIGATION
   ============================================================ */

function bindOpportunityNavigation() {
    discoveryElements(
        "[data-discovery-open]"
    ).forEach(
        (button) => {
            if (
                button.dataset.discoveryBound ===
                "true"
            ) {
                return;
            }

            button.dataset.discoveryBound =
                "true";

            button.addEventListener(
                "click",
                (event) => {
                    event.preventDefault();
                    event.stopPropagation();

                    const symbol =
                        button.dataset.discoveryOpen;

                    if (symbol) {
                        openDiscoveryOpportunity(
                            symbol
                        );
                    }
                }
            );
        }
    );

    discoveryElements(
        "[data-discovery-opportunity]"
    ).forEach(
        (row) => {
            if (
                row.dataset.discoveryRowBound ===
                "true"
            ) {
                return;
            }

            row.dataset.discoveryRowBound =
                "true";

            row.addEventListener(
                "keydown",
                (event) => {
                    if (
                        event.key !== "Enter" &&
                        event.key !== " "
                    ) {
                        return;
                    }

                    event.preventDefault();

                    const symbol =
                        row.dataset.symbol;

                    if (symbol) {
                        openDiscoveryOpportunity(
                            symbol
                        );
                    }
                }
            );
        }
    );
}


/* ============================================================
   OPPORTUNITY DETAIL
   ============================================================ */

async function openDiscoveryOpportunity(
    symbol
) {
    DiscoveryState.selectedSymbol =
        symbol;

    showDiscoveryOpportunityLoading(
        symbol
    );

    try {
        const url =
            DISCOVERY_CONFIG.opportunityEndpoint(
                symbol
            );

        const result =
            await discoveryFetch(
                url
            );

        renderOpportunityDetail(
            result
        );

    } catch (error) {
        renderOpportunityError(
            symbol,
            error
        );
    }
}


/* ============================================================
   OPPORTUNITY LOADING
   ============================================================ */

function showDiscoveryOpportunityLoading(
    symbol
) {
    const panel =
        discoveryElement(
            "[data-discovery-opportunity-detail]"
        );

    if (!panel) {
        /*
         * If the existing page has no detail panel,
         * navigate to Terminal with the selected symbol.
         *
         * This is navigation only.
         */
        navigateToTerminal(
            symbol
        );

        return;
    }

    panel.hidden = false;

    panel.innerHTML = `
        <div class="discovery-opportunity-loading">
            Loading opportunity details for
            <strong>
                ${escapeHTML(symbol)}
            </strong>…
        </div>
    `;
}


/* ============================================================
   OPPORTUNITY DETAIL RENDER
   ============================================================ */

function renderOpportunityDetail(
    result
) {
    const panel =
        discoveryElement(
            "[data-discovery-opportunity-detail]"
        );

    if (!panel) {
        return;
    }

    panel.hidden = false;

    const symbol =
        result?.symbol ||
        DiscoveryState.selectedSymbol ||
        "—";

    const opportunity =
        result?.opportunity;

    const explanation =
        result?.explanation;

    panel.innerHTML = `
        <div
            class="discovery-opportunity-header"
        >
            <div>
                <div
                    class="discovery-detail-label"
                >
                    OPPORTUNITY
                </div>

                <h3>
                    ${escapeHTML(symbol)}
                </h3>
            </div>

            <button
                type="button"
                data-discovery-close-detail
            >
                Close
            </button>
        </div>

        <div
            class="discovery-opportunity-body"
        >
            <div
                data-discovery-opportunity-data
            >
                ${renderSafeObject(
                    opportunity
                )}
            </div>

            <div
                data-discovery-opportunity-explanation
            >
                ${renderSafeObject(
                    explanation
                )}
            </div>
        </div>

        <div
            class="discovery-opportunity-actions"
        >
            <button
                type="button"
                data-discovery-terminal="${escapeHTML(symbol)}"
            >
                Open Terminal
            </button>

            <button
                type="button"
                data-discovery-buyer="${escapeHTML(symbol)}"
            >
                Open Buyer
            </button>
        </div>
    `;

    const close =
        panel.querySelector(
            "[data-discovery-close-detail]"
        );

    if (close) {
        close.addEventListener(
            "click",
            () => {
                panel.hidden = true;
            }
        );
    }

    const terminal =
        panel.querySelector(
            "[data-discovery-terminal]"
        );

    if (terminal) {
        terminal.addEventListener(
            "click",
            () => {
                navigateToTerminal(
                    terminal.dataset.discoveryTerminal
                );
            }
        );
    }

    const buyer =
        panel.querySelector(
            "[data-discovery-buyer]"
        );

    if (buyer) {
        buyer.addEventListener(
            "click",
            () => {
                navigateToBuyer(
                    buyer.dataset.discoveryBuyer
                );
            }
        );
    }
}


/* ============================================================
   SAFE OBJECT DISPLAY
   ============================================================ */

function renderSafeObject(
    value
) {
    if (
        value === null ||
        value === undefined
    ) {
        return `
            <div class="discovery-no-data">
                No backend detail returned.
            </div>
        `;
    }

    if (
        typeof value === "string" ||
        typeof value === "number" ||
        typeof value === "boolean"
    ) {
        return `
            <div class="discovery-value">
                ${escapeHTML(value)}
            </div>
        `;
    }

    if (Array.isArray(value)) {
        if (!value.length) {
            return `
                <div class="discovery-no-data">
                    No data.
                </div>
            `;
        }

        return `
            <pre class="discovery-json">
${escapeHTML(
    JSON.stringify(
        value,
        null,
        2
    )
)}
            </pre>
        `;
    }

    return `
        <pre class="discovery-json">
${escapeHTML(
    JSON.stringify(
        value,
        null,
        2
    )
)}
        </pre>
    `;
}


function renderOpportunityError(
    symbol,
    error
) {
    const panel =
        discoveryElement(
            "[data-discovery-opportunity-detail]"
        );

    if (!panel) {
        return;
    }

    panel.hidden = false;

    panel.innerHTML = `
        <div
            class="discovery-error"
        >
            Unable to load opportunity
            <strong>
                ${escapeHTML(symbol)}
            </strong>.

            <div>
                ${escapeHTML(
                    error?.message ||
                    "Unknown backend error"
                )}
            </div>
        </div>
    `;
}


/* ============================================================
   NAVIGATION
   ============================================================ */

function navigateToTerminal(
    symbol
) {
    const encoded =
        encodeURIComponent(
            symbol
        );

    window.location.href =
        `/terminal?symbol=${encoded}`;
}


function navigateToBuyer(
    symbol
) {
    const encoded =
        encodeURIComponent(
            symbol
        );

    window.location.href =
        `/buyer?symbol=${encoded}`;
}


/* ============================================================
   MAIN LOAD
   ============================================================ */

async function loadDiscovery(
    options = {}
) {
    if (
        DiscoveryState.loading &&
        !options.force
    ) {
        return;
    }

    const requestId =
        ++DiscoveryState.requestId;

    clearDiscoveryError();

    setDiscoveryLoading(
        true
    );

    try {
        const query =
            buildDiscoveryQuery();

        const result =
            await discoveryFetch(
                `${DISCOVERY_CONFIG.pipelineEndpoint}?${query}`
            );

        /*
         * Ignore stale response.
         */
        if (
            requestId !==
            DiscoveryState.requestId
        ) {
            return;
        }

        DiscoveryState.result =
            result;

        renderStages(
            result
        );

        renderTop10(
            result
        );

        renderPipelineSummary(
            result
        );

        setText(
            "[data-discovery-status]",
            result?.status ||
                "READY"
        );

    } catch (error) {
        if (
            requestId !==
            DiscoveryState.requestId
        ) {
            return;
        }

        showDiscoveryError(
            error?.message ||
                "Discovery request failed."
        );

        renderTop10({
            top10: [],
        });

    } finally {
        if (
            requestId ===
            DiscoveryState.requestId
        ) {
            setDiscoveryLoading(
                false
            );
        }
    }
}


/* ============================================================
   PIPELINE SUMMARY
   ============================================================ */

function renderPipelineSummary(
    result
) {
    const order =
        result?.pipeline_order || [
            "UNIVERSE",
            "LIQUIDITY",
            "RISK",
            "TIMING",
            "SCANNER",
            "RANKING",
            "TOP10",
            "OPPORTUNITY",
        ];

    discoveryElements(
        "[data-discovery-pipeline]"
    ).forEach(
        (container) => {
            container.innerHTML =
                order
                    .map(
                        (stage, index) => `
                            <div
                                class="discovery-pipeline-stage"
                                data-pipeline-stage="${escapeHTML(stage)}"
                            >
                                <span>
                                    ${escapeHTML(stage)}
                                </span>

                                ${
                                    index <
                                    order.length - 1
                                        ? "<span>→</span>"
                                        : ""
                                }
                            </div>
                        `
                    )
                    .join("");
        }
    );
}


/* ============================================================
   FILTER BINDING
   ============================================================ */

function bindDiscoveryFilters() {
    discoveryElements(
        "[data-discovery-market]"
    ).forEach(
        (element) => {
            element.addEventListener(
                "change",
                () => {
                    DiscoveryState.market =
                        element.value ||
                        null;

                    loadDiscovery({
                        force: true,
                    });
                }
            );
        }
    );

    discoveryElements(
        "[data-discovery-instrument]"
    ).forEach(
        (element) => {
            element.addEventListener(
                "change",
                () => {
                    DiscoveryState.instrument =
                        element.value ||
                        null;

                    loadDiscovery({
                        force: true,
                    });
                }
            );
        }
    );

    discoveryElements(
        "[data-discovery-universe]"
    ).forEach(
        (element) => {
            element.addEventListener(
                "change",
                () => {
                    DiscoveryState.universe =
                        element.value ||
                        null;

                    loadDiscovery({
                        force: true,
                    });
                }
            );
        }
    );

    discoveryElements(
        "[data-discovery-timeframe]"
    ).forEach(
        (element) => {
            element.addEventListener(
                "change",
                () => {
                    DiscoveryState.timeframe =
                        element.value ||
                        DISCOVERY_CONFIG.defaultTimeframe;

                    loadDiscovery({
                        force: true,
                    });
                }
            );
        }
    );

    discoveryElements(
        "[data-discovery-refresh]"
    ).forEach(
        (element) => {
            element.addEventListener(
                "click",
                () => {
                    loadDiscovery({
                        force: true,
                    });
                }
            );
        }
    );
}


/* ============================================================
   HEALTH
   ============================================================ */

async function loadDiscoveryHealth() {
    try {
        const health =
            await discoveryFetch(
                DISCOVERY_CONFIG.healthEndpoint
            );

        const status =
            health?.status ||
            "UNKNOWN";

        setText(
            "[data-discovery-backend-health]",
            status
        );

        if (
            health?.domains
        ) {
            Object.entries(
                health.domains
            ).forEach(
                ([domain, value]) => {
                    const selector =
                        `[data-discovery-health="${domain}"]`;

                    setText(
                        selector,
                        value?.available
                            ? "AVAILABLE"
                            : "UNAVAILABLE"
                    );
                }
            );
        }

    } catch (error) {
        setText(
            "[data-discovery-backend-health]",
            "UNAVAILABLE"
        );
    }
}


/* ============================================================
   BACKEND MAP
   ============================================================ */

async function loadDiscoveryBackendMap() {
    try {
        const mapping =
            await discoveryFetch(
                DISCOVERY_CONFIG.backendMapEndpoint
            );

        discoveryElements(
            "[data-discovery-backend-map]"
        ).forEach(
            (container) => {
                container.innerHTML =
                    renderBackendMap(
                        mapping
                    );
            }
        );

    } catch (_) {
        /*
         * Backend map is diagnostic UI.
         * It must never block Discovery itself.
         */
    }
}


function renderBackendMap(
    mapping
) {
    const backend =
        mapping?.backend || {};

    const entries =
        Object.entries(
            backend
        );

    if (!entries.length) {
        return `
            <div>
                Backend map unavailable.
            </div>
        `;
    }

    return entries
        .map(
            ([domain, value]) => `
                <div
                    class="discovery-backend-row"
                >
                    <strong>
                        ${escapeHTML(domain)}
                    </strong>

                    <span>
                        ${value?.available
                            ? "AVAILABLE"
                            : "UNAVAILABLE"}
                    </span>
                </div>
            `
        )
        .join("");
}


/* ============================================================
   AUTO REFRESH
   ============================================================ */

function startDiscoveryRefresh() {
    window.setInterval(
        () => {
            if (
                document.visibilityState ===
                "visible"
            ) {
                loadDiscovery();
            }
        },
        DISCOVERY_CONFIG.refreshMs
    );
}


/* ============================================================
   PAGE INITIALISATION
   ============================================================ */

function initDiscoveryBackend() {
    /*
     * Do not initialize on other pages.
     */

    const isDiscoveryPage =
        window.location.pathname ===
            "/discovery" ||
        Boolean(
            discoveryElement(
                "[data-discovery-page]"
            )
        );

    if (!isDiscoveryPage) {
        return;
    }

    bindDiscoveryFilters();

    loadDiscoveryHealth();

    loadDiscoveryBackendMap();

    loadDiscovery({
        force: true,
    });

    startDiscoveryRefresh();
}


/* ============================================================
   PUBLIC API
   ============================================================ */

window.ROBOMLM_DISCOVERY = Object.freeze({
    state: DiscoveryState,

    load: loadDiscovery,

    openOpportunity:
        openDiscoveryOpportunity,

    refresh: () =>
        loadDiscovery({
            force: true,
        }),
});


/* ============================================================
   START
   ============================================================ */

if (
    document.readyState ===
    "loading"
) {
    document.addEventListener(
        "DOMContentLoaded",
        initDiscoveryBackend
    );
} else {
    initDiscoveryBackend();
}