import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import NavRail from "./NavRail";
import TerminalFrontendPanel from "./components/TerminalFrontendPanel";
import DiscoveryScanner from "../Discovery/scanner";
import AssetDetail from "../Discovery/asset-detail";
import Research from "../Research/research";
import Buyer from "../Buyer";
import ScalperTrading from "../ScalperTrading";
import Account from "../Account";
import HTF from "../HTF_Trading/htf-trading";
import Autorobomlm from "../autorobomlm";
import Memory from "../Memory";
import "./styles/app.css";
import "./styles/nav.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="rbm-app">
        <NavRail />
        <div className="rbm-app-main">
          <Routes>
            <Route path="/" element={<Navigate to="/terminal" replace />} />
            <Route path="/terminal" element={<TerminalFrontendPanel />} />
            <Route path="/discovery" element={<DiscoveryScanner />} />
            <Route path="/discovery/asset" element={<AssetDetail />} />
            <Route path="/research" element={<Research />} />
            <Route path="/buyer" element={<Buyer />} />
            <Route path="/scalper" element={<ScalperTrading />} />
            <Route path="/account" element={<Account />} />
            <Route path="/htf" element={<HTF />} />
            <Route path="/autorobomlm" element={<Autorobomlm />} />
            <Route path="/memory" element={<Memory />} />
            <Route path="*" element={<Navigate to="/terminal" replace />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}