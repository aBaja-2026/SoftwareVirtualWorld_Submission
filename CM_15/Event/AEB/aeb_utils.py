"""
aeb_utils.py
Utility classes for AEB logging and metrics.
"""

import os
import csv
import time
import math

import config as cfg


class AEBLogger:
    """CSV logger for AEB run data."""

    COLUMNS = [
        "sim_time_s", "wall_time_s", "state",
        "speed_ms", "speed_kph", "accel_ms2",
        "radar_dist_m", "traffic_dist_m", "traffic_vel_ms",
        "ttc_s", "brake_cmd", "gas_cmd",
        "yaw_rate_rads"
    ]

    def __init__(self):
        os.makedirs(cfg.LOG_DIR, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(cfg.LOG_DIR, f"aeb_run_{ts}.csv")
        self._file = open(path, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(self.COLUMNS)
        print(f"[LOG] Logging to {path}")

    def log(self, sim_time, state, speed, accel, radar_dist,
            traffic_dist, traffic_vel, ttc, brake_cmd, gas_cmd, yaw_rate):
        self._writer.writerow([
            f"{sim_time:.3f}",
            f"{time.time():.3f}",
            cfg.STATE_NAMES.get(state, "UNKNOWN"),
            f"{speed:.4f}",
            f"{speed * 3.6:.2f}",
            f"{accel:.4f}",
            f"{radar_dist:.3f}",
            f"{traffic_dist:.3f}",
            f"{traffic_vel:.3f}",
            f"{ttc:.3f}",
            f"{brake_cmd:.4f}",
            f"{gas_cmd:.4f}",
            f"{yaw_rate:.5f}"
        ])

    def close(self):
        if self._file:
            self._file.close()
            self._file = None


class TTCCalculator:
    """Time-to-collision calculator."""

    def __init__(self):
        self.ttc = float("inf")

    def update(self, ego_speed, target_dist, target_vel=0.0):
        """
        Calculate time-to-collision.

        Args:
            ego_speed: Ego vehicle speed [m/s]
            target_dist: Distance to target [m]
            target_vel: Target vehicle speed [m/s] (0 = stationary)

        Returns:
            TTC in seconds (inf if no collision risk)
        """
        closing_speed = ego_speed - target_vel
        if closing_speed <= 0.01:
            self.ttc = float("inf")
        else:
            effective_gap = target_dist - cfg.STOP_DISTANCE_M
            if effective_gap <= 0:
                self.ttc = 0.0
            else:
                self.ttc = effective_gap / closing_speed
        return self.ttc


class StopDistanceCalculator:
    """
    Compute required braking force to stop at exactly STOP_DISTANCE_M
    from the target, given current speed and distance.
    """

    @staticmethod
    def compute_brake(ego_speed, target_dist):
        """
        Distance-proportional braking with derivative damping.

        Args:
            ego_speed: Ego vehicle speed [m/s]
            target_dist: Distance to target [m]

        Returns:
            Brake pedal command [0.0 - 1.0]
        """
        gap = target_dist - cfg.STOP_DISTANCE_M
        if gap <= 0:
            return cfg.MAX_BRAKE

        # Proportional term: closer = harder braking
        # Uses kinematic equation: v² = 2*a*d → a = v² / (2*d)
        # Normalize to [0,1] assuming max decel ~8 m/s²
        required_decel = (ego_speed ** 2) / (2.0 * gap) if gap > 0.1 else 10.0
        brake_p = required_decel / 8.0  # 8 m/s² ≈ 0.8g reference decel

        # Derivative term: faster closing = more brake
        brake_d = cfg.BRAKE_KD * (ego_speed / max(gap, 0.5))

        brake_cmd = brake_p + brake_d
        brake_cmd = max(cfg.MIN_BRAKE, min(cfg.MAX_BRAKE, brake_cmd))

        return brake_cmd
