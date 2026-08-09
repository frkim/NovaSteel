# Steel Production and Steel Processing — A Beginner's Guide

> **Who is this for?** Anyone who knows *nothing* about the steel industry and
> wants to understand, from the ground up, how steel is made, how it is shaped
> into useful products, and why it matters for **NovaSteel** and its
> *Project Ignition* AI platform.
>
> **How to read it.** Start at the top and work down — each section builds on
> the previous one. If you only have five minutes, read the
> [simplified version](steel-production-and-processing-simplified.md) instead.

---

## Table of contents

1. [Why steel matters](#1-why-steel-matters)
2. [What is steel? Iron, carbon and alloys](#2-what-is-steel-iron-carbon-and-alloys)
3. [The raw materials](#3-the-raw-materials)
4. [The two main production routes](#4-the-two-main-production-routes)
5. [Step 1 — Ironmaking: the blast furnace](#5-step-1--ironmaking-the-blast-furnace)
6. [Step 2 — Steelmaking: turning iron into steel](#6-step-2--steelmaking-turning-iron-into-steel)
7. [Step 3 — Casting: from liquid to solid](#7-step-3--casting-from-liquid-to-solid)
8. [Step 4 — Steel processing: rolling and finishing](#8-step-4--steel-processing-rolling-and-finishing)
9. [Steel products and grades](#9-steel-products-and-grades)
10. [Energy, emissions and sustainability](#10-energy-emissions-and-sustainability)
11. [Quality, safety and the role of operators](#11-quality-safety-and-the-role-of-operators)
12. [How this maps to NovaSteel and Project Ignition](#12-how-this-maps-to-novasteel-and-project-ignition)
13. [Glossary](#13-glossary)

---

## 1. Why steel matters

Steel is the **most widely used metal on the planet**. It is in the cars we
drive, the buildings and bridges we cross, the railways and pipelines that move
goods and energy, the machines in every factory, and the cans in our kitchens.
It is strong, relatively cheap, endlessly **recyclable**, and can be tuned to
thousands of different properties by changing its recipe.

Making steel is also one of the **most energy-intensive and carbon-intensive**
industrial activities in the world. The global steel industry is responsible for
roughly **7–9% of all human-made CO₂ emissions**. That single fact explains much
of what follows: nearly every modern improvement in steelmaking is about making
**more steel, of higher quality, with less energy and less carbon**.

**NovaSteel** is a Luxembourg-based *integrated* steel producer operating blast
furnaces and rolling mills across Luxembourg, Germany, Belgium and Spain. It
supplies flat and long steel to the automotive, construction, energy and
engineering industries. Understanding how a plant like this works is the key to
understanding the business problems that *Project Ignition* sets out to solve.

---

## 2. What is steel? Iron, carbon and alloys

### Iron vs. steel

**Iron** is a chemical element (symbol **Fe**) dug out of the ground as **iron
ore** — rock rich in iron oxides (iron combined with oxygen). Pure iron is
relatively soft and rusts easily, so it is rarely used on its own.

**Steel** is an **alloy** — a deliberate mixture — of **iron and a small amount
of carbon** (usually less than 2%). That pinch of carbon transforms soft iron
into a material that is far **stronger and harder**. Get the carbon wrong and
the metal becomes brittle; this is why controlling chemistry is so important.

| Material | Carbon content | Character |
| -------- | -------------- | --------- |
| Pure iron | ~0% | Soft, bends easily |
| Steel | up to ~2% | Strong, tough, versatile |
| Cast iron | ~2–4% | Hard but brittle |

### Alloying elements

Beyond carbon, steelmakers add small amounts of other elements to fine-tune the
properties:

- **Manganese** — strength and toughness
- **Chromium** — hardness and corrosion resistance (the key element in
  *stainless* steel)
- **Nickel** — toughness and corrosion resistance
- **Silicon** — used in electrical (transformer) steels
- **Molybdenum, vanadium, niobium** — strength at high temperature, fine grain

Changing the recipe — and the way the steel is heated and cooled — produces
thousands of distinct **grades**, each designed for a specific job. A
high-strength steel for a car's safety cage is a very different grade from a
deep-drawing steel for a smooth door panel, even though both are "steel".

---

## 3. The raw materials

Integrated steelmaking starts from rock and coal. The main inputs are:

- **Iron ore** — the source of iron. Often delivered as fine powder that is
  baked into lumps called **sinter** or **pellets** so air can flow through it
  in the furnace.
- **Coke** — coal that has been baked in the absence of air to drive off
  impurities. Coke is both the **fuel** that heats the furnace and the chemical
  **reducing agent** that strips oxygen away from the iron ore.
- **Limestone (flux)** — added to capture impurities and float them off as a
  glassy waste called **slag**.
- **Air / oxygen** — blasted in to burn the coke (hence the name *blast*
  furnace).
- **Steel scrap** — recycled steel, melted down again. Scrap is the main input
  for the alternative "electric" route described below.

> **Key idea — reduction.** Iron ore is iron that is "stuck" to oxygen. The
> central chemistry of ironmaking is **removing that oxygen** ("reduction") so
> you are left with metallic iron. Coke supplies the carbon that grabs the
> oxygen and leaves as carbon-dioxide and carbon-monoxide gas — which is exactly
> why the process emits so much CO₂.

---

## 4. The two main production routes

There are two dominant ways to make steel. NovaSteel is an **integrated**
producer, meaning it uses the first route.

### Route A — Integrated (Blast Furnace + Basic Oxygen Furnace)

Iron ore → **blast furnace** → liquid iron → **basic oxygen furnace (BOF)** →
steel. This is the classic, large-scale route for making steel **from raw ore**.
It produces the largest volumes and the highest, most consistent quality — but
it is the most **energy- and carbon-intensive**, because the blast furnace burns
huge amounts of coke.

### Route B — Electric (Electric Arc Furnace)

**Steel scrap** (and sometimes direct-reduced iron) → **electric arc furnace
(EAF)** → steel. Powerful electric arcs melt recycled scrap. This route uses far
**less energy and emits far less CO₂ per tonne**, and its footprint depends
heavily on how *clean* the electricity is. It is more flexible and quicker to
start and stop, which matters when electricity prices change hour by hour.

| | Integrated (BF–BOF) | Electric (EAF) |
| --- | --- | --- |
| Main input | Iron ore + coke | Steel scrap |
| Energy source | Coke (coal) | Electricity |
| CO₂ per tonne | High | Lower (depends on grid) |
| Typical use | Very large volumes, premium grades | Recycled / flexible production |

The rest of this guide follows **Route A**, NovaSteel's integrated route,
end to end.

---

## 5. Step 1 — Ironmaking: the blast furnace

![Schematic of a blast furnace](images/Blast_furnace_schema.png)

The **blast furnace** is the towering, chimney-like heart of an integrated steel
plant. It is essentially a giant, continuously running chemical reactor that
turns solid iron ore into **liquid iron**.

**How it works, step by step:**

1. **Charging from the top.** Layers of iron ore (as sinter/pellets), coke and
   limestone are dropped in from the top, building up a tall column inside the
   furnace.
2. **Hot blast from the bottom.** A blast of **very hot air (~1,200 °C)** — and
   often pure oxygen — is injected near the base.
3. **Burning and reduction.** The blast burns the coke, reaching temperatures
   above **2,000 °C**. The hot gases rise through the descending column, and the
   carbon from the coke **strips the oxygen out of the iron ore**, leaving
   metallic iron.
4. **Melting and collecting.** The iron melts and trickles down to collect at
   the bottom as **molten iron** (also called *hot metal* or *pig iron*). The
   limestone captures impurities and floats on top as **slag**, which is
   periodically drained off.
5. **Tapping.** Every few hours the furnace is "tapped": liquid iron is drained
   into giant ladles (called **torpedo cars**) and rushed, still molten, to the
   next step.

A blast furnace runs **non-stop for years** between major rebuilds. Its inside
is protected by a **refractory lining** — heat-resistant brick and material that
shields the steel shell from the extreme heat. **This lining slowly wears away.**
If it fails unexpectedly, molten iron can break through, causing a catastrophic
and dangerous failure that can cost millions of euros and halt production — a
problem we return to in [Section 12](#12-how-this-maps-to-novasteel-and-project-ignition).

> **The molten iron leaving the blast furnace is not yet steel.** It still
> contains too much carbon and unwanted impurities. Turning it into steel is the
> next step.

---

## 6. Step 2 — Steelmaking: turning iron into steel

The liquid iron from the blast furnace is "refined" into steel — meaning its
chemistry is **adjusted precisely** by removing excess carbon and impurities and
adding alloying elements.

### The Basic Oxygen Furnace (BOF)

In the **Basic Oxygen Furnace**, the molten iron (plus some scrap) is poured
into a huge pear-shaped vessel. A lance blows **pure oxygen** onto the surface at
supersonic speed. The oxygen burns off the excess carbon and impurities in a
violent, fiery reaction lasting only about **20 minutes**. The result is liquid
**raw steel** with the carbon brought down into the correct range.

### Electric Arc Furnace (EAF) — the alternative

In the electric route, an **Electric Arc Furnace** melts scrap using giant
electrodes that strike electric arcs hotter than the surface of the sun. It
arrives at the same place — liquid steel — by a different path.

### Secondary metallurgy (ladle refining)

Raw steel from the BOF or EAF is rarely ready as-is. It moves to **secondary
metallurgy** (also called *ladle refining*), where operators:

- **Fine-tune the chemistry** by adding precise amounts of alloying elements;
- **Remove dissolved gases** and unwanted inclusions for cleaner steel;
- **Adjust the temperature** so the steel is exactly right for casting.

This is where a generic batch of steel becomes a **specific grade** for a
specific customer — for example, a high-grade steel for automotive body panels.
Getting this chemistry and temperature consistently right is central to
**quality**, and is one of the hardest things to do reliably batch after batch.

---

## 7. Step 3 — Casting: from liquid to solid

Liquid steel must be solidified into a workable shape. Almost all modern steel is
solidified by **continuous casting**.

In continuous casting, liquid steel is poured into a water-cooled mould and
drawn out **continuously** as a glowing, solidifying strand. As it moves, it is
cooled and cut into long semi-finished shapes:

- **Slabs** — wide, flat blocks → become **flat products** (sheet, plate, coil).
- **Blooms / billets** — squarer, longer bars → become **long products**
  (beams, bars, rails, rods, wire).

These semi-finished pieces are the starting stock for the shaping step that
follows. They are essentially **steel in a convenient, storable form**, waiting
to be rolled into final products.

---

## 8. Step 4 — Steel processing: rolling and finishing

![Rolling mill](images/rolling_mils_pix.png)

"**Steel processing**" is everything that happens *after* the steel is cast —
turning those slabs and billets into the precise shapes, thicknesses and surface
finishes customers actually buy. The workhorse of processing is the
**rolling mill**.

### What is rolling?

**Rolling** squeezes hot or cold steel between heavy rotating rolls, like a
giant pasta machine. Each pass makes the steel **thinner, longer and flatter**
(or shapes it into a profile). It is the single most important way steel is
shaped.

### Hot rolling

The slab is reheated until it glows (~1,200 °C) and passed back and forth
through powerful rolls. While hot, steel is soft and easy to shape, so big
reductions in thickness are possible. A thick slab can become a long, thin
**hot-rolled coil** in minutes. Hot rolling is used for plates, structural
beams, rails and the starting coils for further processing.

### Cold rolling

To get thinner gauges, a smoother surface and tighter tolerances, hot-rolled
coil is rolled again **at room temperature**. Cold rolling makes the steel
**harder and stronger** and gives the excellent surface finish needed for, say,
visible car body panels or appliances.

### Finishing operations

After rolling, steel is often finished to add properties and protection:

- **Annealing** — controlled heating and cooling to soften the steel and relieve
  the stresses introduced by cold rolling, restoring formability.
- **Pickling** — an acid bath that removes the oxide scale from the surface.
- **Coating** — applying a protective layer:
  - **Galvanizing** — a zinc coating that prevents rust (common on car bodies).
  - **Tin plating** — for food and drink cans.
  - **Painting / organic coatings** — colour and weather protection.
- **Cutting, slitting and shaping** — trimming coils and plates to the exact
  widths, lengths and forms the customer ordered.

The output of processing is **finished steel**: coils, sheets, plates, beams,
bars, rods and wire, each made to a tight specification.

---

## 9. Steel products and grades

Steel products are usually split into two broad families:

- **Flat products** — made from slabs: plate, sheet, strip and coil. Used for car
  bodies, appliances, pipes, cans and packaging.
- **Long products** — made from blooms/billets: beams, columns, bars, rails,
  rods and wire. Used for construction, railways and reinforcement.

A **grade** is a precise specification — a defined chemistry plus a defined
processing history — that guarantees particular properties (strength, ductility,
corrosion resistance, formability). For example, **high-grade automotive steel**
must be strong yet formable enough to be pressed into complex shapes without
cracking, with a flawless surface and **very tight consistency from coil to
coil**. Customers like carmakers reject material that drifts outside
specification, so **consistency** is as valuable as the steel itself.

---

## 10. Energy, emissions and sustainability

Steelmaking is **hungry for energy** and is a **major source of CO₂**:

- The **blast furnace** burns enormous amounts of coke, and that carbon leaves as
  **CO₂**. This is the main reason steel accounts for a large share of global
  emissions.
- **Reheating, rolling and finishing** all consume large amounts of heat and
  electricity. At NovaSteel, **energy is about 35% of total production cost**.

Two big external pressures shape the economics:

- **The EU Emissions Trading System (EU ETS).** Producers must hold "allowances"
  for the CO₂ they emit. As allowances get scarcer and more expensive, **every
  tonne of CO₂ has a direct financial cost** — so cutting emissions cuts costs
  and penalties.
- **Volatile electricity prices.** Power prices change hour by hour. Running
  energy-intensive steps when electricity is **cheap and clean** — and easing off
  when it is **expensive and carbon-heavy** — can save a great deal of money and
  carbon.

This is why **energy optimization** and **emissions reduction** are not just
environmental goals but core **business** goals.

---

## 11. Quality, safety and the role of operators

Steel plants run **continuously**, at extreme temperatures, with molten metal and
heavy machinery. Two human factors dominate day-to-day success:

- **Quality control.** Every grade has tight tolerances. Tiny deviations in
  chemistry, temperature or rolling can push a whole batch out of specification,
  forcing it to be scrapped or downgraded. Consistency is everything, especially
  for demanding customers like carmakers.
- **Operator expertise.** Much of the know-how that keeps a plant running safely
  and efficiently lives in the heads of **experienced operators** — how a furnace
  "sounds" when something is wrong, how to react to an unusual reading, which
  small adjustment prevents a big problem. Much of this knowledge is **tacit**:
  never written down.

As skilled operators **retire**, decades of hard-won judgment can walk out the
door faster than it can be taught to newcomers. **Capturing and structuring that
knowledge** before it is lost is a strategic priority — and a perfect job for
modern AI.

---

## 12. How this maps to NovaSteel and Project Ignition

Everything above explains the business challenges behind NovaSteel's
*[Project Ignition](../usecase/usecase.md)*. The plant's pain points map directly
onto the steel basics in this guide:

| Steelmaking reality (this guide) | NovaSteel challenge | *Project Ignition* AI response |
| --- | --- | --- |
| The blast-furnace **refractory lining wears out** and can fail catastrophically ([§5](#5-step-1--ironmaking-the-blast-furnace)) | Lining failures are unpredictable and cost **~€8M per event** | **Physics-informed ML** predicts lining degradation from thermal signatures — *21-day advance warning* |
| Steelmaking is **energy-hungry** and exposed to spot prices & EU ETS ([§10](#10-energy-emissions-and-sustainability)) | Energy is **35% of cost**; CO₂ faces ETS penalties | An **energy-dispatch optimization agent** schedules energy-intensive steps around electricity prices & grid carbon |
| **Quality** of high-grade steel must be tightly consistent ([§9](#9-steel-products-and-grades), [§11](#11-quality-safety-and-the-role-of-operators)) | Quality is inconsistent for automotive customers | Data-driven optimization to lift **high-grade yield** |
| **Operator know-how is tacit** and retiring ([§11](#11-quality-safety-and-the-role-of-operators)) | Knowledge disappears faster than it is captured | A **GenAI knowledge-capture assistant** interviews operators and builds a searchable procedure library |

In short: once you understand *how* steel is made and *why* it is so energy-,
carbon- and knowledge-intensive, the case for an AI optimization platform like
Project Ignition becomes self-evident.

---

## 13. Glossary

| Term | Plain-English meaning |
| ---- | --------------------- |
| **Alloy** | A metal made by mixing a base metal with other elements to improve its properties. |
| **Annealing** | Heating and slowly cooling steel to soften it and relieve internal stress. |
| **Basic Oxygen Furnace (BOF)** | Vessel that blows oxygen through molten iron to burn off carbon and make steel. |
| **Billet / Bloom** | Long, square-ish semi-finished steel that is rolled into long products. |
| **Blast furnace** | Giant reactor that turns iron ore into liquid iron using coke and hot air. |
| **Coke** | Coal baked without air; the fuel and oxygen-remover in the blast furnace. |
| **Continuous casting** | Solidifying liquid steel into a continuous strand, then cutting it into slabs/billets. |
| **EAF (Electric Arc Furnace)** | Furnace that melts steel scrap with electric arcs. |
| **EU ETS** | EU Emissions Trading System — a market that puts a price on emitting CO₂. |
| **Flat products** | Sheet, plate, strip and coil made from slabs. |
| **Flux (limestone)** | Material added to capture impurities as slag. |
| **Grade** | A precise steel specification (chemistry + processing) guaranteeing set properties. |
| **Hot / cold rolling** | Squeezing steel between rolls to shape it — hot (soft) or cold (precise, strong). |
| **Iron ore** | Rock rich in iron oxides; the raw source of iron. |
| **Long products** | Beams, bars, rails, rods and wire made from blooms/billets. |
| **Molten / pig iron** | Liquid iron tapped from the blast furnace; not yet steel. |
| **Pickling** | Acid bath that cleans oxide scale off the steel surface. |
| **Refractory lining** | Heat-resistant brick that protects a furnace's steel shell from extreme heat. |
| **Secondary metallurgy** | Ladle refining that fine-tunes chemistry and temperature before casting. |
| **Slab** | Wide, flat semi-finished steel that is rolled into flat products. |
| **Slag** | Glassy waste that floats on molten metal, carrying away impurities. |
| **Steel** | Alloy of iron with a small, controlled amount of carbon. |

---

*See also: the [simplified one-page version](steel-production-and-processing-simplified.md)
and the NovaSteel [use case](../usecase/usecase.md).*
