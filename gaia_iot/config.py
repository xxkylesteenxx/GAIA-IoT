from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class IoTConfig:
    # identity
    node_id: str = "gaia-iot-node-01"
    cluster_id: str = "gaia-cluster-main"
    deployment_zone: str = "edge-zone-01"

    # sensor domains enabled on this node
    enabled_domains: List[str] = field(
        default_factory=lambda: ["TERRA", "AQUA", "AERO", "VITA"]
    )

    # sensor polling
    poll_interval_seconds: float = 60.0
    sensor_timeout_seconds: float = 10.0
    max_adversarial_suspicion: float = 0.5   # discard observations above this
    min_quality_score: float = 0.4           # discard observations below this

    # freshness requirements
    require_freshness_class: str = "RT"      # RT or better preferred
    permit_nrt_with_warning: bool = True

    # local buffer
    buffer_max_events: int = 10_000
    buffer_flush_interval_seconds: float = 30.0

    # uplink to GAIA-Server
    uplink_enabled: bool = True
    uplink_endpoint: str = "gaia-server:50051"
    uplink_batch_size: int = 50
    uplink_retry_max: int = 5
    uplink_retry_backoff_seconds: float = 2.0

    # planetary-state publishing
    planetary_publish_enabled: bool = True
    planetary_snapshot_interval_s: float = 60.0  # publish cadence in seconds

    # power management
    power_mode: str = "balanced"  # full | balanced | low-power | sleep
    battery_threshold_low: float = 0.20
    battery_threshold_critical: float = 0.05

    # state paths
    state_root: str = ".gaia_iot_state"
    buffer_path: str = ".gaia_iot_state/buffer.jsonl"

    # security
    pqc_enabled: bool = True
    tls_min_version: str = "TLSv1.3"


DEFAULT_IOT_CONFIG = IoTConfig()
