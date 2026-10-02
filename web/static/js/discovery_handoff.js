/*
 * ROBOMLM_PLUS
 * Discovery -> Terminal / Buyer Handoff
 *
 * PART 5
 *
 * PURPOSE
 * -------
 * Discovery has already performed:
 *
 *   Universe
 *      ->
 *   Liquidity
 *      ->
 *   Risk Filter
 *      ->
 *   Timing
 *      ->
 *   Scanner
 *      ->
 *   Ranking
 *      ->
 *   Top10
 *      ->
 *   Opportunity
 *
 * This file handles ONLY the frontend handoff.
 *
 * Discovery does NOT:
 *   - create BUY/SELL
 *   - create an order
 *   - authorize execution
 *   - call CAS for execution
 *   - bypass D13
 *   - bypass Risk
 *
 * Terminal / Buyer are downstream analysis surfaces.
 */


"use strict";


/* ============================================================
   CONFIG
   ============================================================ */

const DISCOVERY_HANDOFF = Object.freeze({

    terminalPath: "/terminal",

    buyerPath: "/buyer",

    discoveryPath: "/discovery",

    storageKey:
        "robomlm.discovery.selected_opportunity",

});


/* ============================================================
   STATE
   ============================================================ */

const DiscoveryHandoffState = {

    symbol: null,

    market: null,

    instrument: null,

    timeframe: null,

    opportunity: null,

    source: "DISCOVERY",

};


/* ============================================================
   SAFE HELPERS
   ============================================================ */

function dhEscape(value) {

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


function dhSetText(
    selector,
    value
) {

    const element =
        document.querySelector(
            selector
        );

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


/* ============================================================
   OPPORTUNITY EXTRACTION
   ============================================================ */

function extractOpportunitySymbol(
    opportunity
) {

    if (!opportunity) {
        return null;
    }

    if (
        typeof opportunity === "string"
    ) {
        return opportunity;
    }

    return (
        opportunity.symbol ||
        opportunity.ticker ||
        opportunity.asset ||
        opportunity.instrument_symbol ||
        null
    );
}


function extractOpportunityMarket(
    opportunity
) {

    if (
        !opportunity ||
        typeof opportunity !== "object"
    ) {
        return null;
    }

    return (
        opportunity.market ||
        opportunity.market_type ||
        null
    );
}


function extractOpportunityInstrument(
    opportunity
) {

    if (
        !opportunity ||
        typeof opportunity !== "object"
    ) {
        return null;
    }

    return (
        opportunity.instrument ||
        opportunity.instrument_type ||
        null
    );
}


function extractOpportunityTimeframe(
    opportunity
) {

    if (
        !opportunity ||
        typeof opportunity !== "object"
    ) {
        return null;
    }

    return (
        opportunity.timeframe ||
        opportunity.interval ||
        null
    );
}


/* ============================================================
   SAVE DISCOVERY SELECTION
   ============================================================ */

function saveDiscoverySelection(
    opportunity
) {

    const symbol =
        extractOpportunitySymbol(
            opportunity
        );

    if (!symbol) {
        return false;
    }

    DiscoveryHandoffState.symbol =
        symbol;

    DiscoveryHandoffState.market =
        extractOpportunityMarket(
            opportunity
        );

    DiscoveryHandoffState.instrument =
        extractOpportunityInstrument(
            opportunity
        );

    DiscoveryHandoffState.timeframe =
        extractOpportunityTimeframe(
            opportunity
        );

    DiscoveryHandoffState.opportunity =
        opportunity;

    /*
     * Store only the discovery selection.
     *
     * No order.
     * No execution instruction.
     * No authorization.
     */

    try {

        sessionStorage.setItem(
            DISCOVERY_HANDOFF.storageKey,
            JSON.stringify({
                symbol:
                    DiscoveryHandoffState.symbol,

                market:
                    DiscoveryHandoffState.market,

                instrument:
                    DiscoveryHandoffState.instrument,

                timeframe:
                    DiscoveryHandoffState.timeframe,

                source: "DISCOVERY",
            })
        );

    } catch (_) {

        /*
         * Session storage is convenience only.
         * Navigation must still work.
         */

    }

    return true;
}


/* ============================================================
   BUILD TERMINAL URL
   ============================================================ */

function buildTerminalUrl(
    opportunity
) {

    const symbol =
        extractOpportunitySymbol(
            opportunity
        );

    if (!symbol) {
        return null;
    }

    const params =
        new URLSearchParams();

    params.set(
        "symbol",
        symbol
    );

    const market =
        extractOpportunityMarket(
            opportunity
        );

    if (market) {

        params.set(
            "market",
            market
        );
    }

    const instrument =
        extractOpportunityInstrument(
            opportunity
        );

    if (instrument) {

        params.set(
            "instrument",
            instrument
        );
    }

    const timeframe =
        extractOpportunityTimeframe(
            opportunity
        );

    if (timeframe) {

        params.set(
            "timeframe",
            timeframe
        );
    }

    params.set(
        "source",
        "discovery"
    );

    return (
        `${DISCOVERY_HANDOFF.terminalPath}?${params.toString()}`
    );
}


/* ============================================================
   BUILD BUYER URL
   ============================================================ */

function buildBuyerUrl(
    opportunity
) {

    const symbol =
        extractOpportunitySymbol(
            opportunity
        );

    if (!symbol) {
        return null;
    }

    const params =
        new URLSearchParams();

    params.set(
        "symbol",
        symbol
    );

    const market =
        extractOpportunityMarket(
            opportunity
        );

    if (market) {

        params.set(
            "market",
            market
        );
    }

    const instrument =
        extractOpportunityInstrument(
            opportunity
        );

    if (instrument) {

        params.set(
            "instrument",
            instrument
        );
    }

    const timeframe =
        extractOpportunityTimeframe(
            opportunity
        );

    if (timeframe) {

        params.set(
            "timeframe",
            timeframe
        );
    }

    params.set(
        "source",
        "discovery"
    );

    return (
        `${DISCOVERY_HANDOFF.buyerPath}?${params.toString()}`
    );
}


/* ============================================================
   TERMINAL HANDOFF
   ============================================================ */

function handoffToTerminal(
    opportunity
) {

    if (
        !saveDiscoverySelection(
            opportunity
        )
    ) {

        showHandoffError(
            "Discovery opportunity has no valid symbol."
        );

        return;
    }

    const url =
        buildTerminalUrl(
            opportunity
        );

    if (!url) {

        showHandoffError(
            "Unable to create Terminal navigation."
        );

        return;
    }

    window.location.assign(
        url
    );
}


/* ============================================================
   BUYER HANDOFF
   ============================================================ */

function handoffToBuyer(
    opportunity
) {

    if (
        !saveDiscoverySelection(
            opportunity
        )
    ) {

        showHandoffError(
            "Discovery opportunity has no valid symbol."
        );

        return;
    }

    const url =
        buildBuyerUrl(
            opportunity
        );

    if (!url) {

        showHandoffError(
            "Unable to create Buyer navigation."
        );

        return;
    }

    window.location.assign(
        url
    );
}


/* ============================================================
   Handoff ERROR
   ============================================================ */

function showHandoffError(
    message
) {

    const existing =
        document.querySelector(
            "[data-discovery-handoff-error]"
        );

    if (existing) {

        existing.hidden = false;

        existing.textContent =
            message;

        return;
    }

    console.error(
        "ROBOMLM Discovery handoff:",
        message
    );
}


/* ============================================================
   OPPORTUNITY DETAIL ACTIONS
   ============================================================ */

function bindOpportunityHandoffButtons() {

    document
        .querySelectorAll(
            "[data-discovery-handoff-terminal]"
        )
        .forEach(
            (button) => {

                if (
                    button.dataset
                        .discoveryHandoffBound ===
                    "true"
                ) {
                    return;
                }

                button.dataset
                    .discoveryHandoffBound =
                    "true";

                button.addEventListener(
                    "click",
                    (event) => {

                        event.preventDefault();

                        const symbol =
                            button.dataset
                                .discoveryHandoffTerminal;

                        if (!symbol) {

                            showHandoffError(
                                "No Discovery symbol selected."
                            );

                            return;
                        }

                        handoffToTerminal({
                            symbol: symbol,
                            source: "DISCOVERY",
                        });

                    }
                );

            }
        );


    document
        .querySelectorAll(
            "[data-discovery-handoff-buyer]"
        )
        .forEach(
            (button) => {

                if (
                    button.dataset
                        .discoveryHandoffBound ===
                    "true"
                ) {
                    return;
                }

                button.dataset
                    .discoveryHandoffBound =
                    "true";

                button.addEventListener(
                    "click",
                    (event) => {

                        event.preventDefault();

                        const symbol =
                            button.dataset
                                .discoveryHandoffBuyer;

                        if (!symbol) {

                            showHandoffError(
                                "No Discovery symbol selected."
                            );

                            return;
                        }

                        handoffToBuyer({
                            symbol: symbol,
                            source: "DISCOVERY",
                        });

                    }
                );

            }
        );
}


/* ============================================================
   TOP10 ROW HANDOFF
   ============================================================ */

function bindTop10HandoffButtons() {

    document
        .querySelectorAll(
            "[data-discovery-top10-terminal]"
        )
        .forEach(
            (button) => {

                if (
                    button.dataset.bound ===
                    "true"
                ) {
                    return;
                }

                button.dataset.bound =
                    "true";

                button.addEventListener(
                    "click",
                    (event) => {

                        event.preventDefault();

                        const symbol =
                            button.dataset
                                .discoveryTop10Terminal;

                        if (symbol) {

                            handoffToTerminal({
                                symbol: symbol,
                                source: "DISCOVERY_TOP10",
                            });

                        }

                    }
                );

            }
        );


    document
        .querySelectorAll(
            "[data-discovery-top10-buyer]"
        )
        .forEach(
            (button) => {

                if (
                    button.dataset.bound ===
                    "true"
                ) {
                    return;
                }

                button.dataset.bound =
                    "true";

                button.addEventListener(
                    "click",
                    (event) => {

                        event.preventDefault();

                        const symbol =
                            button.dataset
                                .discoveryTop10Buyer;

                        if (symbol) {

                            handoffToBuyer({
                                symbol: symbol,
                                source: "DISCOVERY_TOP10",
                            });

                        }

                    }
                );

            }
        );
}


/* ============================================================
   RECOVER SESSION SELECTION
   ============================================================ */

function recoverDiscoverySelection() {

    try {

        const raw =
            sessionStorage.getItem(
                DISCOVERY_HANDOFF.storageKey
            );

        if (!raw) {
            return null;
        }

        const parsed =
            JSON.parse(
                raw
            );

        if (
            !parsed ||
            !parsed.symbol
        ) {
            return null;
        }

        DiscoveryHandoffState.symbol =
            parsed.symbol;

        DiscoveryHandoffState.market =
            parsed.market || null;

        DiscoveryHandoffState.instrument =
            parsed.instrument || null;

        DiscoveryHandoffState.timeframe =
            parsed.timeframe || null;

        return parsed;

    } catch (_) {

        return null;
    }
}


/* ============================================================
   DISCOVERY DETAIL SUMMARY
   ============================================================ */

function renderHandoffSummary(
    opportunity
) {

    const container =
        document.querySelector(
            "[data-discovery-handoff-summary]"
        );

    if (!container) {
        return;
    }

    const symbol =
        extractOpportunitySymbol(
            opportunity
        );

    const market =
        extractOpportunityMarket(
            opportunity
        );

    const instrument =
        extractOpportunityInstrument(
            opportunity
        );

    const timeframe =
        extractOpportunityTimeframe(
            opportunity
        );

    container.innerHTML = `

        <div
            class="discovery-handoff-summary"
        >

            <div>
                <span>
                    Selected Asset
                </span>

                <strong>
                    ${dhEscape(
                        symbol || "—"
                    )}
                </strong>
            </div>

            <div>
                <span>
                    Market
                </span>

                <strong>
                    ${dhEscape(
                        market || "—"
                    )}
                </strong>
            </div>

            <div>
                <span>
                    Instrument
                </span>

                <strong>
                    ${dhEscape(
                        instrument || "—"
                    )}
                </strong>
            </div>

            <div>
                <span>
                    Timeframe
                </span>

                <strong>
                    ${dhEscape(
                        timeframe || "—"
                    )}
                </strong>
            </div>

        </div>

    `;
}


/* ============================================================
   DETAIL ACTION AREA
   ============================================================ */

function renderHandoffActions(
    opportunity
) {

    const container =
        document.querySelector(
            "[data-discovery-handoff-actions]"
        );

    if (!container) {
        return;
    }

    const symbol =
        extractOpportunitySymbol(
            opportunity
        );

    if (!symbol) {

        container.innerHTML = `
            <div>
                No valid opportunity selected.
            </div>
        `;

        return;
    }

    container.innerHTML = `

        <button
            type="button"
            data-discovery-handoff-terminal="${dhEscape(symbol)}"
        >
            Open Terminal
        </button>

        <button
            type="button"
            data-discovery-handoff-buyer="${dhEscape(symbol)}"
        >
            Open Buyer
        </button>

    `;

    bindOpportunityHandoffButtons();
}


/* ============================================================
   PUBLIC DISCOVERY HANDOFF API
   ============================================================ */

window.ROBOMLM_DISCOVERY_HANDOFF =
    Object.freeze({

        state:
            DiscoveryHandoffState,

        save:
            saveDiscoverySelection,

        terminal:
            handoffToTerminal,

        buyer:
            handoffToBuyer,

        terminalUrl:
            buildTerminalUrl,

        buyerUrl:
            buildBuyerUrl,

        recover:
            recoverDiscoverySelection,

        renderSummary:
            renderHandoffSummary,

        renderActions:
            renderHandoffActions,

    });


/* ============================================================
   INITIALISE
   ============================================================ */

function initDiscoveryHandoff() {

    const isDiscovery =
        window.location.pathname ===
            DISCOVERY_HANDOFF.discoveryPath ||
        document.querySelector(
            "[data-discovery-page]"
        );

    if (!isDiscovery) {
        return;
    }

    bindOpportunityHandoffButtons();

    bindTop10HandoffButtons();

    recoverDiscoverySelection();
}


if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initDiscoveryHandoff
    );

} else {

    initDiscoveryHandoff();

}