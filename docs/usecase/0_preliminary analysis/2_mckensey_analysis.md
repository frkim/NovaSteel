# 📑 Table of Contents — NovaSteel AI-Powered Steel Production Optimisation Platform

> 📖 **This is the outline.** The full, section-by-section analysis is built out in
> the [`2_mckensey_analysis/`](2_mckensey_analysis/README.md) folder — one file per
> section (0–15). Start at the [index / README](2_mckensey_analysis/README.md) or the
> [Executive Summary](2_mckensey_analysis/00-executive-summary.md).

## 0. 🧭 Executive Summary

- 0.1 Industrial context (NovaSteel — integrated steel producer, HQ Luxembourg; plants in Luxembourg, Germany, Belgium, Spain)
- 0.2 Client problem (energy ≈ 35% of production cost, CO₂ / EU ETS penalties, €8M furnace-lining failures, automotive-grade quality, retiring expertise)
- 0.3 Proposed solution (AI-driven production-optimisation platform on Microsoft Fabric + Foundry)
- 0.4 Expected value (−14% energy/ton, −22% CO₂, 21-day failure warning, +8% high-grade yield)
- 0.5 Recommendation and next steps

## 1. 🏭 Industry Context & Strategic Drivers

- 1.1 Overview of European steel industry
- 1.2 Energy volatility and cost pressure
- 1.3 EU ETS and carbon pricing impact
- 1.4 Competitive landscape (global steel producers)
- 1.5 Digital transformation maturity in heavy industry

## 2. 🚨 Business Problem Definition

- 2.1 Energy inefficiency — energy ≈ 35% of total production cost, with no real-time optimisation
- 2.2 Unpredictable furnace-lining wear — catastrophic failures costing €8M per event
- 2.3 Quality variability in high-grade steel for automotive customers
- 2.4 Knowledge loss — skilled operators retiring faster than expertise is captured
- 2.5 Operational constraints across a 4-country footprint (Luxembourg, Germany, Belgium, Spain)

## 3. 🎯 Transformation Objectives

- 3.1 Reduce energy consumption per ton by 14%
- 3.2 Reduce CO₂ emissions by 22% (lower EU ETS exposure)
- 3.3 Predict furnace-lining failure with 21-day advance warning
- 3.4 Improve high-grade steel yield by 8%
- 3.5 Capture and structure operator expertise before it is lost

## 4. 💡 Solution Overview

- 4.1 End-to-end AI optimisation platform
- 4.2 Core capability pillars:
  - Predictive maintenance intelligence
  - Energy optimisation engine
  - Quality control AI system
  - GenAI knowledge capture system
- 4.3 High-level value flow

## 5. 🏗️ Target Architecture

- 5.1 Conceptual architecture (cloud-first, Azure IoT Hub ingestion)
- 5.2 Industrial IoT layer (sensors, SCADA, PLC → Azure IoT Hub, cloud-direct)
- 5.3 Data platform (Microsoft Fabric / OneLake lakehouse)
- 5.4 AI/ML layer (Microsoft Fabric Data Science + Microsoft Foundry — training, inference, optimisation agents)
- 5.5 Integration layer (ERP, MES, EAM systems)
- 5.6 Visualization & decision layer (Power BI / dashboards)

## 6. 🧠 AI & Analytics Design

- 6.1 Physics-informed ML — furnace-lining degradation from thermal signatures
- 6.2 Predictive maintenance models (RUL + "failure within 21 days" alert)
- 6.3 Energy-dispatch optimisation agent (schedules energy-intensive steps around electricity spot prices / grid carbon)
- 6.4 Quality prediction models (steel composition consistency for automotive grades)
- 6.5 GenAI knowledge-capture assistant (operator interviews → procedure library; RAG via Microsoft Foundry / Foundry IQ)
- 6.6 Model lifecycle (MLOps in Microsoft Fabric Data Science)
- 6.7 Demo sensor simulator (simulates multi-sensor events for the main factory/mill components; injectable scenarios for live demos)

## 7. 📊 Data Strategy & Governance

- 7.1 Industrial data sources (IoT, MES, ERP, external energy markets)
- 7.2 Data architecture and flow
- 7.3 Data quality management
- 7.4 Data governance framework
- 7.5 GDPR compliance considerations
- 7.6 Data lineage and traceability

## 8. 🔐 Security, Risk & Compliance

- 8.1 Cybersecurity in industrial environments (OT/IT boundary, Purdue model)
- 8.2 EU AI Act compliance strategy
- 8.3 GDPR compliance (operator interviews — lawful basis, DPIA, anonymisation)
- 8.4 Model explainability and auditability
- 8.5 Operational and safety-critical system risk management

## 9. 🚀 Implementation Roadmap

- 9.1 Phase 1 — Pilot (single furnace / site)
- 9.2 Phase 2 — Expansion (multi-line deployment)
- 9.3 Phase 3 — Multi-country scaling (Luxembourg, Germany, Belgium, Spain)
- 9.4 Change management strategy
- 9.5 Workforce upskilling and adoption plan

## 10. 📈 Value Realisation

- 10.1 Financial impact model (OPEX reduction, avoided €8M furnace failures)
- 10.2 Energy savings analysis (−14% energy/ton)
- 10.3 CO₂ reduction impact (−22%, EU ETS cost avoidance)
- 10.4 Production yield improvement (+8% high-grade yield)
- 10.5 KPI dashboard definition

## 11. 🧪 Operating Model

- 11.1 AI Center of Excellence structure
- 11.2 Roles & responsibilities (IT / OT / Data / Operations)
- 11.3 Model ownership and governance
- 11.4 Continuous improvement loop
- 11.5 Vendor and ecosystem strategy

## 12. ⚙️ Technology Stack

- 12.1 Azure cloud services mapping
- 12.2 Cloud-direct ingestion architecture (Azure IoT Hub + Event Hubs, no edge runtime)
- 12.3 Data platform (Microsoft Fabric — OneLake, Real-Time Intelligence, Data Science)
- 12.4 AI services (Microsoft Foundry — Foundry Agent Service, Foundry IQ, Azure OpenAI; Fabric Data Science / ML)
- 12.5 Observability and monitoring tools (Azure Monitor / Application Insights)

## 13. ⚠️ Risks & Mitigation

- 13.1 Model risk (drift, bias, reliability)
- 13.2 Operational risk (production disruption)
- 13.3 Cyber risk
- 13.4 Change resistance
- 13.5 Mitigation strategies

## 14. 📌 Key Recommendations

- 14.1 Strategic priorities
- 14.2 Quick wins vs long-term bets
- 14.3 Scaling strategy
- 14.4 Investment priorities

## 15. 📎 Appendices

- A. Glossary (industrial + AI terms)
- B. KPI definitions
- C. Architecture diagrams (detailed)
- D. Data schema overview
- E. Model technical specifications
- F. EU ETS overview and assumptions
- G. Demo sensor simulator (main components, sensors, metrics & scenarios)
