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

## Azure Services

Lastly, this analysis evaluates which Azure services will be involved in this project. Candidate services include:

- **Azure IoT Hub / Azure IoT Operations** — Device connectivity and management.
- **Azure Event Hubs** — High-throughput telemetry ingestion and streaming.
- **Azure Stream Analytics / Azure Functions** — Real-time data processing and transformation.
- **Azure Data Lake Storage** — Durable storage for raw and curated data.
- **Azure Machine Learning / Azure AI Foundry** — Model training, deployment, and AI agents.
- **Azure Monitor / Application Insights** — Observability, logging, and alerting.

> **Note:** The final list of services will be refined as requirements are detailed in subsequent analysis documents.

