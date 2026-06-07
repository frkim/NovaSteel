"""Tests for the NovaSteel Project Ignition demo (``novasteel_demo``).

Run with::

    python -m unittest test_novasteel_demo

These tests validate the three AI workloads and the compliance trust moment on
the synthetic demo data, asserting the headline claims from
``documentation/work/08-demo-script.md``.
"""

import unittest

import novasteel_demo as nd


class TestSyntheticData(unittest.TestCase):
    def test_telemetry_shape_and_determinism(self):
        a = nd.generate_furnace_telemetry()
        b = nd.generate_furnace_telemetry()
        self.assertEqual(len(a), 110)
        self.assertEqual(a, b)  # deterministic for a fixed seed
        for row in a:
            self.assertIn("thermal_gradient", row)
            self.assertIn("vibration", row)
        # Wear is monotonically increasing in the true signal.
        wear = [r["wear_true"] for r in a]
        self.assertTrue(all(y >= x - 1e-9 for x, y in zip(wear, wear[1:])))

    def test_sop_corpus(self):
        corpus = nd.generate_sop_corpus()
        self.assertTrue(any(d["id"] == "SOP-101" for d in corpus))
        self.assertTrue(all({"id", "title", "text", "status"} <= set(d) for d in corpus))


class TestFurnaceRUL(unittest.TestCase):
    def setUp(self):
        self.telemetry = nd.generate_furnace_telemetry()

    def test_21_day_alert_fires_at_demo_today(self):
        result = nd.assess_furnace(self.telemetry, as_of_day=84)
        self.assertTrue(result["alert"])
        self.assertIsNotNone(result["predicted_rul_days"])
        self.assertTrue(18 <= result["predicted_rul_days"] <= 24)
        # Uncertainty band brackets the point estimate.
        self.assertLessEqual(result["rul_low_days"], result["predicted_rul_days"])
        self.assertGreaterEqual(result["rul_high_days"], result["predicted_rul_days"])

    def test_drivers_present(self):
        drivers = nd.assess_furnace(self.telemetry, as_of_day=84)["drivers"]
        names = " ".join(d["name"] for d in drivers)
        self.assertIn("Thermal gradient", names)
        self.assertIn("Wear-rate proxy", names)
        self.assertAlmostEqual(sum(d["contribution_pct"] for d in drivers), 100.0, delta=0.2)

    def test_no_alert_early_in_campaign(self):
        result = nd.assess_furnace(self.telemetry, as_of_day=40)
        self.assertFalse(result["alert"])
        self.assertGreater(result["predicted_rul_days"], 21)


class TestEnergyOptimizer(unittest.TestCase):
    def test_meets_cost_and_carbon_targets(self):
        r = nd.optimize_dispatch()
        # Target is -14% energy cost / -22% CO2 (illustrative demo estimate).
        self.assertTrue(-15.0 <= r["cost_delta_pct"] <= -13.0)
        self.assertTrue(-23.5 <= r["carbon_delta_pct"] <= -21.0)

    def test_energy_is_conserved(self):
        r = nd.optimize_dispatch()
        self.assertAlmostEqual(sum(r["baseline_load"]), sum(r["optimized_load"]), places=6)

    def test_load_shifts_into_cleanest_window(self):
        r = nd.optimize_dispatch()
        night = next(i for i, b in enumerate(r["blocks"]) if b.startswith("Night"))
        self.assertGreater(r["optimized_load"][night], r["baseline_load"][night])


class TestKnowledgeAssistant(unittest.TestCase):
    def setUp(self):
        self.assistant = nd.KnowledgeAssistant()

    def test_grounded_answer_with_citations(self):
        result = self.assistant.answer(
            "How do we stabilise surface quality on grade X during a cold start?"
        )
        self.assertTrue(result["grounded"])
        ids = [c["id"] for c in result["citations"]]
        self.assertIn("SOP-101", ids)
        self.assertIn("SOP-101", result["answer"])

    def test_refuses_when_not_grounded(self):
        result = self.assistant.answer("What is the company share price today?")
        self.assertFalse(result["grounded"])
        self.assertEqual(result["citations"], [])

    def test_interview_capture_then_retrieve(self):
        before = len(self.assistant.corpus)
        record = self.assistant.capture_tip(
            "Stabilising grade Z restart",
            "On a grade Z restart, hold a slower zelthar preheat ramp and re-sample chemistry.",
        )
        self.assertEqual(record["status"], "pending metallurgist review")
        self.assertEqual(len(self.assistant.corpus), before + 1)
        # The newly captured tip is now retrievable (unique keyword).
        result = self.assistant.answer("How to handle a grade Z restart zelthar ramp?")
        self.assertTrue(result["grounded"])
        self.assertIn(record["id"], [c["id"] for c in result["citations"]])

    def test_capture_requires_content(self):
        with self.assertRaises(ValueError):
            self.assistant.capture_tip("", "")


class TestAuditLog(unittest.TestCase):
    def test_chain_and_tamper_detection(self):
        log = nd.AuditLog()
        log.record("rul-model", "prediction", "A", "RUL 21d")
        log.record("energy-optimizer", "recommendation", "B", "shift load")
        log.record("operator", "approval", "B", "confirmed")
        self.assertEqual(len(log.records), 3)
        self.assertTrue(log.verify())
        # Tamper with a record's content; the chain must no longer verify.
        log.records[1].summary = "shift MORE load"
        self.assertFalse(log.verify())


class TestWebPages(unittest.TestCase):
    def test_pages_render(self):
        state = nd._DemoState()
        self.assertIn(nd.SYNTHETIC_DATA_LABEL, nd.page_overview())
        self.assertIn("21-day advance alert", nd.page_scene_a(84, state.audit))
        self.assertIn("energy shifted to clean/cheap windows", nd.page_scene_b(state.audit))
        self.assertIn("Procedure library", nd.page_scene_c(state.assistant, state.audit))
        self.assertIn("Lineage verified", nd.page_trust(state.audit))
        self.assertIn("the ask", nd.page_close())


if __name__ == "__main__":
    unittest.main()
