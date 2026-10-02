/*
 * ROBOMLM — Shared Discovery Context Utility
 *
 * Discovery → Terminal / Buyer context bridge.
 *
 * Responsibilities:
 *   1. Parse Discovery query parameters
 *   2. Fall back to sessionStorage
 *   3. Normalize context
 *   4. Restore existing page controls
 *   5. Publish one common context event
 *
 * This utility does NOT:
 *   - create BUY/SELL decisions
 *   - create orders
 *   - authorize execution
 *   - call CAS
 *   - modify D13
 */

(function (window, document) {
    "use strict";

    const STORAGE_KEY = "robomlm.discovery.selection";
    const EVENT_NAME = "robomlm:discovery-context-restored";

    const DiscoveryContext = {

        /*
         * ------------------------------------------------------------
         * Normalize one context object.
         * ------------------------------------------------------------
         */
        normalize(raw) {
            raw = raw || {};

            return {
                symbol: String(raw.symbol || "").trim(),
                market: String(raw.market || "").trim(),
                instrument: String(raw.instrument || "").trim(),
                timeframe: String(
                    raw.timeframe || raw.tf || ""
                ).trim()
            };
        },

        /*
         * ------------------------------------------------------------
         * Parse URL query parameters.
         *
         * Supported:
         *   symbol
         *   market
         *   instrument
         *   timeframe
         *   tf
         * ------------------------------------------------------------
         */
        fromQuery() {
            const params = new URLSearchParams(
                window.location.search
            );

            return this.normalize({
                symbol: params.get("symbol"),
                market: params.get("market"),
                instrument: params.get("instrument"),
                timeframe:
                    params.get("timeframe") ||
                    params.get("tf")
            });
        },

        /*
         * ------------------------------------------------------------
         * Read Discovery selection from sessionStorage.
         * ------------------------------------------------------------
         */
        fromSession() {
            try {
                const raw = sessionStorage.getItem(STORAGE_KEY);

                if (!raw) {
                    return this.normalize({});
                }

                return this.normalize(JSON.parse(raw));
            } catch (error) {
                console.warn(
                    "[ROBOMLM] Invalid Discovery session context",
                    error
                );

                return this.normalize({});
            }
        },

        /*
         * ------------------------------------------------------------
         * Merge query + session.
         *
         * Query parameters always have priority.
         * Missing query values are restored from sessionStorage.
         * ------------------------------------------------------------
         */
        read() {
            const query = this.fromQuery();
            const session = this.fromSession();

            return this.normalize({
                symbol: query.symbol || session.symbol,
                market: query.market || session.market,
                instrument:
                    query.instrument ||
                    session.instrument,
                timeframe:
                    query.timeframe ||
                    session.timeframe
            });
        },

        /*
         * ------------------------------------------------------------
         * Determine whether there is anything to restore.
         * ------------------------------------------------------------
         */
        hasContext(context) {
            context = this.normalize(context);

            return Boolean(
                context.symbol ||
                context.market ||
                context.instrument ||
                context.timeframe
            );
        },

        /*
         * ------------------------------------------------------------
         * Save Discovery context.
         *
         * Used by Discovery handoff.
         * ------------------------------------------------------------
         */
        save(context) {
            context = this.normalize(context);

            try {
                sessionStorage.setItem(
                    STORAGE_KEY,
                    JSON.stringify(context)
                );
            } catch (error) {
                console.warn(
                    "[ROBOMLM] Could not save Discovery context",
                    error
                );
            }

            return context;
        },

        /*
         * ------------------------------------------------------------
         * Clear saved Discovery context.
         * ------------------------------------------------------------
         */
        clear() {
            try {
                sessionStorage.removeItem(STORAGE_KEY);
            } catch (error) {
                // Storage may be unavailable.
            }
        },

        /*
         * ------------------------------------------------------------
         * Find an existing page control.
         *
         * No fixed DOM architecture is imposed.
         * ------------------------------------------------------------
         */
        findControl(names) {
            for (const name of names || []) {

                const byId =
                    document.getElementById(name);

                if (byId) {
                    return byId;
                }

                const byName = document.querySelector(
                    `[name="${CSS.escape(name)}"]`
                );

                if (byName) {
                    return byName;
                }

                const byData = document.querySelector(
                    `[data-${CSS.escape(name)}]`
                );

                if (byData) {
                    return byData;
                }
            }

            return null;
        },

        /*
         * ------------------------------------------------------------
         * Restore one control.
         *
         * SELECT:
         *   value → case-insensitive value → visible text
         *
         * INPUT:
         *   direct value restoration
         * ------------------------------------------------------------
         */
        setControlValue(element, value) {
            if (!element || value === "") {
                return false;
            }

            const wanted = String(value);

            if (element.tagName === "SELECT") {

                const options =
                    Array.from(element.options);

                let match = options.find(
                    option =>
                        option.value === wanted
                );

                if (!match) {
                    match = options.find(
                        option =>
                            option.value.toLowerCase() ===
                            wanted.toLowerCase()
                    );
                }

                if (!match) {
                    match = options.find(
                        option =>
                            option.text.trim().toLowerCase() ===
                            wanted.toLowerCase()
                    );
                }

                if (!match) {
                    return false;
                }

                element.value = match.value;

                element.dispatchEvent(
                    new Event("input", {
                        bubbles: true
                    })
                );

                element.dispatchEvent(
                    new Event("change", {
                        bubbles: true
                    })
                );

                return true;
            }

            element.value = wanted;

            element.dispatchEvent(
                new Event("input", {
                    bubbles: true
                })
            );

            element.dispatchEvent(
                new Event("change", {
                    bubbles: true
                })
            );

            return true;
        },

        /*
         * ------------------------------------------------------------
         * Restore a named context field.
         * ------------------------------------------------------------
         */
        restoreField(context, field, names) {
            if (!context || !context[field]) {
                return false;
            }

            const control =
                this.findControl(names);

            return this.setControlValue(
                control,
                context[field]
            );
        },

        /*
         * ------------------------------------------------------------
         * Restore page controls.
         *
         * Market is intentionally restored first.
         * This allows an existing market→instrument dependency
         * to populate the instrument selector.
         * ------------------------------------------------------------
         */
        restore(options) {
            options = options || {};

            const context =
                this.normalize(
                    options.context || this.read()
                );

            if (!this.hasContext(context)) {
                return {
                    ok: false,
                    context,
                    restored: {}
                };
            }

            const restored = {
                market: false,
                instrument: false,
                symbol: false,
                timeframe: false
            };

            const controls = options.controls || {};

            /*
             * MARKET FIRST
             */
            restored.market = this.restoreField(
                context,
                "market",
                controls.market || [
                    "market",
                    "terminal-market",
                    "buyer-market",
                    "selected-market"
                ]
            );

            /*
             * SYMBOL
             */
            restored.symbol = this.restoreField(
                context,
                "symbol",
                controls.symbol || [
                    "symbol",
                    "terminal-symbol",
                    "buyer-symbol",
                    "selected-symbol",
                    "asset-symbol"
                ]
            );

            /*
             * TIMEFRAME
             */
            restored.timeframe = this.restoreField(
                context,
                "timeframe",
                controls.timeframe || [
                    "timeframe",
                    "tf",
                    "terminal-timeframe",
                    "buyer-timeframe",
                    "selected-timeframe"
                ]
            );

            /*
             * INSTRUMENT
             *
             * This may need to happen after an existing market
             * selector has populated its options.
             */
            const restoreInstrument = () => {
                restored.instrument = this.restoreField(
                    context,
                    "instrument",
                    controls.instrument || [
                        "instrument",
                        "terminal-instrument",
                        "buyer-instrument",
                        "selected-instrument"
                    ]
                );

                this.publish(context, {
                    restored,
                    page: options.page || null
                });
            };

            const instrumentDelay =
                Number.isFinite(options.instrumentDelay)
                    ? options.instrumentDelay
                    : 50;

            if (context.instrument) {
                window.setTimeout(
                    restoreInstrument,
                    instrumentDelay
                );
            } else {
                this.publish(context, {
                    restored,
                    page: options.page || null
                });
            }

            return {
                ok: true,
                context,
                restored
            };
        },

        /*
         * ------------------------------------------------------------
         * Update visual Discovery-context labels.
         * ------------------------------------------------------------
         */
        updateLabels(context) {
            context = this.normalize(context);

            document.querySelectorAll(
                "[data-discovery-symbol]"
            ).forEach(element => {
                element.textContent = context.symbol;
            });

            document.querySelectorAll(
                "[data-discovery-market]"
            ).forEach(element => {
                element.textContent = context.market;
            });

            document.querySelectorAll(
                "[data-discovery-instrument]"
            ).forEach(element => {
                element.textContent =
                    context.instrument;
            });

            document.querySelectorAll(
                "[data-discovery-timeframe]"
            ).forEach(element => {
                element.textContent =
                    context.timeframe;
            });
        },

        /*
         * ------------------------------------------------------------
         * Publish one standard event.
         *
         * Terminal and Buyer can listen to the same event.
         * ------------------------------------------------------------
         */
        publish(context, metadata) {
            context = this.normalize(context);
            metadata = metadata || {};

            this.updateLabels(context);

            const payload = {
                symbol: context.symbol,
                market: context.market,
                instrument: context.instrument,
                timeframe: context.timeframe,
                source: "discovery",
                page:
                    metadata.page ||
                    window.location.pathname,
                restored:
                    metadata.restored || {},
                timestamp:
                    new Date().toISOString()
            };

            /*
             * Public page state.
             */
            window.ROBOMLM_DISCOVERY_CONTEXT =
                Object.freeze({
                    ...payload
                });

            /*
             * Backward-compatible page-specific state.
             */
            if (
                window.location.pathname === "/terminal"
            ) {
                window.ROBOMLM_TERMINAL_CONTEXT =
                    Object.freeze({
                        ...payload
                    });
            }

            if (
                window.location.pathname === "/buyer"
            ) {
                window.ROBOMLM_BUYER_CONTEXT =
                    Object.freeze({
                        ...payload
                    });
            }

            document.dispatchEvent(
                new CustomEvent(
                    EVENT_NAME,
                    {
                        detail: payload
                    }
                )
            );

            return payload;
        },

        /*
         * ------------------------------------------------------------
         * Listen for the shared restoration event.
         * ------------------------------------------------------------
         */
        onRestored(callback) {
            if (typeof callback !== "function") {
                return function () {};
            }

            const handler = event => {
                callback(
                    event.detail || {}
                );
            };

            document.addEventListener(
                EVENT_NAME,
                handler
            );

            return function unsubscribe() {
                document.removeEventListener(
                    EVENT_NAME,
                    handler
                );
            };
        },

        /*
         * ------------------------------------------------------------
         * Build a clean handoff query string.
         * ------------------------------------------------------------
         */
        toQuery(context) {
            context = this.normalize(context);

            const params = new URLSearchParams();

            if (context.symbol) {
                params.set(
                    "symbol",
                    context.symbol
                );
            }

            if (context.market) {
                params.set(
                    "market",
                    context.market
                );
            }

            if (context.instrument) {
                params.set(
                    "instrument",
                    context.instrument
                );
            }

            if (context.timeframe) {
                params.set(
                    "timeframe",
                    context.timeframe
                );
            }

            return params.toString();
        },

        /*
         * ------------------------------------------------------------
         * Build Terminal URL.
         * ------------------------------------------------------------
         */
        terminalUrl(context) {
            const query =
                this.toQuery(context);

            return query
                ? `/terminal?${query}`
                : "/terminal";
        },

        /*
         * ------------------------------------------------------------
         * Build Buyer URL.
         * ------------------------------------------------------------
         */
        buyerUrl(context) {
            const query =
                this.toQuery(context);

            return query
                ? `/buyer?${query}`
                : "/buyer";
        },

        /*
         * ------------------------------------------------------------
         * Initialize a page.
         * ------------------------------------------------------------
         */
        init(options) {
            options = options || {};

            const context = this.read();

            if (!this.hasContext(context)) {
                return {
                    ok: false,
                    context,
                    restored: {}
                };
            }

            /*
             * Persist the merged query/session result.
             * This means a direct URL handoff survives subsequent
             * internal page transitions.
             */
            this.save(context);

            return this.restore({
                ...options,
                context
            });
        }
    };

    /*
     * Public shared utility.
     */
    window.ROBOMLM_DISCOVERY_CONTEXT =
        DiscoveryContext;

})(window, document);