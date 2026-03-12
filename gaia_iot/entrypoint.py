from __future__ import annotations

import logging
import signal
import time
from pathlib import Path

from gaia_core.bootstrap import build_default_gaia
from gaia_iot.config import IoTConfig, DEFAULT_IOT_CONFIG
from gaia_iot.sensors.manager import SensorManager
from gaia_iot.fusion.engine import FusionEngine
from gaia_iot.uplink.uplink import EdgeUplink
from gaia_iot.power.manager import PowerManager
from gaia_iot.planetary.publisher import PlanetaryStatePublisher

logger = logging.getLogger(__name__)


class GaiaIoTNode:
    """
    GAIA IoT edge node.

    Boot order:
      1. Load config
      2. Bootstrap GAIA-Core substrate (8 cores, identity, memory, workspace)
      3. Start power manager
      4. Start sensor manager
      5. Start fusion engine
      6. Start edge uplink
      7. Start planetary-state publisher
      8. Run sensor-fuse-uplink-publish loop
    """

    def __init__(self, config: IoTConfig = DEFAULT_IOT_CONFIG) -> None:
        self.config = config
        self.substrate = None
        self.sensors = None
        self.fusion = None
        self.uplink = None
        self.power = None
        self.planetary = None
        self._running = False
        self._last_snapshot_time: float = 0.0

    def boot(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        logger.info("GAIA-IoT booting. node=%s zone=%s",
                    self.config.node_id, self.config.deployment_zone)

        # 1. Bootstrap GAIA-Core substrate
        logger.info("Bootstrapping GAIA-Core substrate...")
        self.substrate = build_default_gaia(Path(self.config.state_root))
        logger.info("Substrate ready. cores=%s", self.substrate.registry.names())

        # 2. Power manager
        self.power = PowerManager(self.config)
        logger.info("Power mode: %s", self.power.current_mode())

        # 3. Sensor manager
        self.sensors = SensorManager(self.config)
        self.sensors.start()
        logger.info("SensorManager started. domains=%s", self.config.enabled_domains)

        # 4. Fusion engine
        self.fusion = FusionEngine(self.substrate, self.config)
        logger.info("FusionEngine ready.")

        # 5. Uplink
        self.uplink = EdgeUplink(self.substrate, self.config)
        self.uplink.start()
        logger.info("EdgeUplink started. endpoint=%s", self.config.uplink_endpoint)

        # 6. Planetary publisher
        self.planetary = PlanetaryStatePublisher(self.config)
        logger.info("PlanetaryStatePublisher ready.")

        self._running = True
        logger.info("GAIA-IoT ready. identity=%s",
                    self.substrate.identity.public_fingerprint)

    def run(self) -> None:
        """Main sensor-fuse-uplink-publish loop."""
        while self._running:
            try:
                # Collect raw observations from all sensors
                raw = self.sensors.collect()

                # Fuse and quality-gate observations
                fused = self.fusion.process(raw)

                # Dispatch fused observations into GAIA-Core ATLAS
                for obs in fused:
                    self.substrate.dispatch("ATLAS", {
                        "kind": "ingest_observation",
                        "payload": {
                            "source_id":             obs.source_id,
                            "domain":                obs.domain,
                            "payload":               obs.payload,
                            "quality_score":         obs.quality_score,
                            "freshness_class":       obs.freshness_class,
                            "adversarial_suspicion": obs.adversarial_suspicion,
                            "source_class":          obs.source_class.value,
                        },
                    })

                # Queue fused observations for uplink
                self.uplink.enqueue(fused)

                # Publish planetary-state snapshot at configured cadence
                now = time.time()
                interval = self.config.planetary_snapshot_interval_s
                if self.config.planetary_publish_enabled and (
                    now - self._last_snapshot_time >= interval
                ):
                    snapshot = self.planetary.build_snapshot(fused)
                    self.uplink.enqueue_snapshot(snapshot)
                    self._last_snapshot_time = now

            except Exception as exc:
                logger.error("IoT loop error: %s", exc)

            # Respect power mode poll interval
            interval = self.power.poll_interval(self.config.poll_interval_seconds)
            time.sleep(interval)

    def shutdown(self) -> None:
        logger.info("GAIA-IoT shutting down...")
        self._running = False
        if self.sensors:
            self.sensors.stop()
        if self.uplink:
            self.uplink.stop()
        logger.info("GAIA-IoT shutdown complete.")


def main() -> None:
    node = GaiaIoTNode()
    node.boot()

    def _handler(sig, frame):
        node.shutdown()

    signal.signal(signal.SIGTERM, _handler)
    signal.signal(signal.SIGINT, _handler)
    node.run()


if __name__ == "__main__":
    main()
