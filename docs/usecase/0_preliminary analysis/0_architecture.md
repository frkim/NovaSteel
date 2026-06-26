# Solution Architecture

This file contains information about the solution architecture.

## Overview

In a steel factory, a lot of components are involved in the toolchain, from sensors to agents or operators. This analysis defines where the focus needs to be applied and how data and decisions flow across the system.

## End-to-End Flow

1. **Sensors / Edge Devices** — Capture physical measurements (temperature, pressure, vibration, throughput) from the production line.
2. **Edge Gateway / IoT Connectivity** — Aggregates, buffers, and normalizes raw telemetry before sending it to the cloud.
3. **Ingestion & Streaming** — Receives high-frequency telemetry and routes it to storage and real-time processing pipelines.
4. **Data Processing & Analytics** — Cleans, transforms, and enriches the data; computes metrics and detects anomalies.
5. **AI Agents & Models** — Provide predictive insights, recommendations, and automated decision support.
6. **Operators & Applications** — Consume insights via dashboards, alerts, and control interfaces to take action.

## Architecture Layers

| Layer | Responsibility | Key Concerns |
|-------|----------------|--------------|
| Edge | Data capture and local pre-processing | Latency, reliability, offline operation |
| Connectivity | Secure transport to the cloud | Security, bandwidth, intermittent links |
| Ingestion | Scalable telemetry intake | Throughput, ordering, back-pressure |
| Processing | Transformation and analytics | Accuracy, scalability, cost |
| Intelligence | AI agents and ML models | Model quality, explainability, governance |
| Presentation | Operator-facing experiences | Usability, real-time updates, alerting |

## Areas of Focus

- Reliable, secure telemetry collection from heterogeneous sensors.
- Scalable real-time ingestion and processing of high-volume data.
- AI agents that deliver actionable, explainable insights to operators.
- Clear separation of concerns between edge, cloud, and presentation layers.

## Demo Simulator

To exercise the full toolchain — from sensors to AI agents and operators — **without
connecting to live plant systems**, the solution includes a **demo simulator**: a
service that **simulates events from multiple sensors for the main components of the
steel factory and rolling mills** and streams them through the same end-to-end flow
described above.

**Main components simulated:**

- **Furnace (EAF/BOF)** and its **refractory lining** — the asset behind failure
  prediction.
- **Ladle / secondary metallurgy** and **continuous caster**.
- **Reheat furnace** and **hot rolling-mill stands**.
- **Cooling / run-out table** and plant **utilities & energy**.

**Representative sensors & metrics:**

| Sensor type | Example metrics (units) |
|-------------|-------------------------|
| Pyrometers / IR / thermocouples | Temperature (°C), **heat-flux** (kW/m²), thermal gradient (°C/cm) |
| Vibration / acoustic | Vibration RMS & spectrum (mm/s), acoustic emission |
| Electrical | Electrode current (kA), power (MW), energy (kWh) |
| Off-gas analysers | CO / CO₂ / O₂ (%), dust (mg/Nm³) |
| Flow / pressure / level | Water & gas flow (m³/h, Nm³/h), pressure (bar), mould level (mm) |
| Mill instrumentation | Rolling force (MN), roll gap & strip thickness (mm/µm), strip tension (kN), speed (m/s) |

**Key characteristics:**

- Streams **synthetic, per-device telemetry cloud-direct via Azure IoT Hub** — the
  simulator sits at the **Sensors / Edge Devices** layer with no other change.
- Produces **physically correlated** signals and **injectable scenarios** (refractory
  wear-to-failure, vibration spike, off-gas drift, energy-price spike, quality
  excursion) for **reproducible, seeded** demos, with an optional accelerated clock.
- Every event is tagged `source=simulator` — **no real plant or personal data**.
- Replacing the simulator with live SCADA/historian tags is a **connection change,
  not a redesign**.

> Detailed component/sensor/metric/scenario catalogue:
> [`2_mckensey_analysis/15-appendices.md` §G](2_mckensey_analysis/15-appendices.md#g-demo-sensor-simulator-components-sensors--metrics).

## Azure Services

Lastly, this analysis evaluates which Azure services will be involved in this project. Candidate services include:

- **Azure IoT Hub / Azure IoT Operations** — Device connectivity and management.
- **Azure Event Hubs** — High-throughput telemetry ingestion and streaming.
- **Azure Stream Analytics / Azure Functions** — Real-time data processing and transformation.
- **Azure Data Lake Storage** — Durable storage for raw and curated data.
- **Azure Machine Learning / Azure AI Foundry** — Model training, deployment, and AI agents.
- **Azure Monitor / Application Insights** — Observability, logging, and alerting.

> **Note:** The final list of services will be refined as requirements are detailed in subsequent analysis documents.

