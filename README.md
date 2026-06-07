# **NovaSteel — AI‑Powered Steel Production Optimization Platform**

## 🏭 **Industry Profile**

- **Industry**: Heavy Industry & Metals  
- **Headquarters**: Luxembourg  
- **Operating Region**: Luxembourg, Germany, Belgium, Spain  
- **Regulatory Context**: GDPR • EU AI Act • Sector‑specific EU Directives

---

## ⚠️ **Business Challenge**

A Luxembourg-based integrated steel producer operating blast furnaces and rolling mills across four countries faces:

- **Energy costs** represent 35% of total production cost with no real‑time optimization  
- **CO₂ emissions** under increasing pressure from EU Emissions Trading System (ETS) penalties  
- **Furnace lining wear** impossible to predict, causing catastrophic failures costing **€8M per event**  
- **Quality consistency issues** in high‑grade steel for automotive customers  
- **Skilled operators retiring**, with knowledge disappearing faster than it can be captured

---

## 🎯 **Transformation Objective**

Implement an **AI‑driven production optimization platform** that:

- Reduces energy consumption  
- Predicts equipment failures  
- Improves steel quality  
- Captures and structures operational expertise before it is lost

---

## 📈 **Expected Outcomes**

- **Energy consumption per ton** reduced by **14%**  
- **CO₂ emissions** reduced by **22%**  
- **Furnace lining failure prediction** with **21‑day advance warning**  
- **High‑grade steel yield** improved by **8%**

---

## 🤖 **AI Infusion Point**

- A **physics‑informed ML model** predicts furnace lining degradation from thermal signatures  
- An **energy dispatch optimization agent** schedules energy‑intensive processes around electricity spot prices  
- A **GenAI knowledge‑capture system** interviews operators and structures expertise into searchable procedure libraries

---

## ▶️ **Live demo**

A self‑contained, dependency‑free implementation of the
[demo script](documentation/work/08-demo-script.md) ships in
[`novasteel_demo.py`](novasteel_demo.py). It proves the three AI workloads plus
the compliance **trust moment** entirely on **synthetic, clearly‑labelled data**
— no real plant or personal data, and no external cloud services required (so it
doubles as the recorded fallback).

```bash
python novasteel_demo.py      # serves http://127.0.0.1:5000/
python -m unittest test_novasteel_demo
```

| Scene | Workload | Proof on screen | KPI |
| ----- | -------- | --------------- | --- |
| A | Furnace‑lining RUL | **21‑day** advance alert + uncertainty band + drivers | O3 — avoid ~€8M failures |
| B | Energy‑dispatch optimization | €/ton & tCO₂/ton deltas (**−14% / −22%**) | O1 / O2 |
| C | GenAI knowledge capture | Grounded answer with **citations** + interview mode | O4 — supports +8% yield |
| Trust | Compliance | Hash‑chained **audit / lineage** log | GDPR + EU AI Act, EU‑resident |
