from __future__ import annotations

import shutil
import tempfile
import unittest
from unittest.mock import patch

from gaia_iot.config import IoTConfig
from gaia_iot.entrypoint import GaiaIoTNode
from gaia_iot.sensors.adapters import TerraAdapter, AquaAdapter, AeroAdapter, VitaAdapter
from gaia_iot.power.manager import PowerManager
from gaia_core.grounding.environment import classify_freshness


class TestGaiaIoTBoot(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="gaia-iot-test-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _config(self):
        return IoTConfig(
            node_id="test-edge",
            state_root=self.tmpdir,
            buffer_path=f"{self.tmpdir}/buffer.jsonl",
            enabled_domains=["TERRA", "AQUA", "AERO", "VITA"],
            uplink_enabled=False,
        )

    def test_substrate_boots_eight_cores(self):
        node = GaiaIoTNode(self._config())
        node.boot()
        self.assertEqual(len(node.substrate.registry.names()), 8)
        self.assertIn("ATLAS", node.substrate.registry.names())
        node.shutdown()

    def test_sensor_manager_registers_all_domains(self):
        node = GaiaIoTNode(self._config())
        node.boot()
        self.assertEqual(node.sensors.adapter_count(), 4)
        node.shutdown()

    def test_sensor_collect_returns_readings(self):
        node = GaiaIoTNode(self._config())
        node.boot()
        readings = node.sensors.collect()
        self.assertEqual(len(readings), 4)
        domains = {r["domain"] for r in readings}
        self.assertIn("TERRA", domains)
        self.assertIn("AERO", domains)
        node.shutdown()

    def test_fusion_engine_processes_readings(self):
        node = GaiaIoTNode(self._config())
        node.boot()
        raw = node.sensors.collect()
        fused = node.fusion.process(raw)
        self.assertGreater(len(fused), 0)
        node.shutdown()


class TestPowerManager(unittest.TestCase):
    def _config(self):
        return IoTConfig()

    def test_default_mode_is_balanced(self):
        pm = PowerManager(self._config())
        self.assertEqual(pm.current_mode(), "balanced")

    def test_battery_low_triggers_low_power(self):
        pm = PowerManager(self._config())
        pm.update_from_battery(0.15)
        self.assertEqual(pm.current_mode(), "low-power")

    def test_battery_critical_triggers_sleep(self):
        pm = PowerManager(self._config())
        pm.update_from_battery(0.03)
        self.assertEqual(pm.current_mode(), "sleep")

    def test_sleep_mode_limits_active_sensors(self):
        pm = PowerManager(self._config())
        pm.set_mode("sleep")
        self.assertTrue(pm.is_sensor_active("TERRA"))
        self.assertFalse(pm.is_sensor_active("VITA"))

    def test_poll_interval_scales_with_mode(self):
        pm = PowerManager(self._config())
        base = 60.0
        pm.set_mode("low-power")
        self.assertAlmostEqual(pm.poll_interval(base), 180.0)


class TestAdapters(unittest.TestCase):
    def test_terra_adapter_read(self):
        a = TerraAdapter(node_id="test")
        a.open()
        r = a.read()
        self.assertEqual(r["domain"], "TERRA")
        self.assertIn("temperature_c", r["payload"])
        self.assertIn("wildfire_risk", r["payload"])

    def test_aero_adapter_read(self):
        a = AeroAdapter(node_id="test")
        a.open()
        r = a.read()
        self.assertEqual(r["domain"], "AERO")
        self.assertIn("pm25_ug_m3", r["payload"])

    def test_freshness_classification(self):
        self.assertEqual(classify_freshness(60), "URT")
        self.assertEqual(classify_freshness(900), "RT")
        self.assertEqual(classify_freshness(7200), "NRT")


if __name__ == "__main__":
    unittest.main()
