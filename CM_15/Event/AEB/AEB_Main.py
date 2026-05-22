"""
AEB_Main.py
Automatic Emergency Braking — main control loop.

State machine:
  ACCELERATING → CRUISING → BRAKING → STOPPED

Connects to a running CarMaker GUI via APO (SimControlInteractive).
Reads radar + traffic DVA quantities, writes brake/gas commands.

Usage:
  1. Start CarMaker GUI & load a TestRun with a stationary target vehicle.
  2. Press Start & Connect (Applications), then Start (simulation).
  3. Run:  python AEB_Main.py
"""

import sys
import os
import time
import math
import asyncio
import numpy as np

# --- CarMaker API path setup ---
_carMakerApiPaths = [
    r"C:\CarMakerOffice-win-15.0\IPGCarMakerPythonApiAddOn-15.0-win64\Python",
    r"C:\IPG\carmaker\win64-15.0\Python",
    r"C:\IPG\carmaker\win64-15.0\Python\IPGRoad",
    r"C:\Program Files\IPG\CarMaker-15.0\python"
]
for _path in _carMakerApiPaths:
    if os.path.isdir(_path) and _path not in sys.path:
        sys.path.insert(0, _path)

_parent = os.path.dirname(r"C:\IPG\carmaker\win64-15.0\Python")
if _parent not in sys.path:
    sys.path.insert(0, _parent)

try:
    import cmapi
    from cmapi import SimControlInteractive, DVADuration, ApoServer
    print("[API] CarMaker API imported successfully.")
except ImportError as e:
    print(f"[ERROR] cmapi not available: {e}")
    sys.exit(1)

import config as cfg
from aeb_utils import AEBLogger, TTCCalculator, StopDistanceCalculator

# ── Brake rate limiter ─────────────────────────────────────────────────────
_prev_brake = 0.0

def rate_limit_brake(new_val: float, prev_val: float) -> float:
    delta = np.clip(new_val - prev_val, -cfg.BRAKE_RATE_LIMIT, cfg.BRAKE_RATE_LIMIT)
    return float(np.clip(prev_val + delta, 0.0, cfg.MAX_BRAKE))


# ── MAIN ───────────────────────────────────────────────────────────────────

async def run():
    global _prev_brake

    # ── 1. Load project and connect to already-running CarMaker GUI via APO ─
    sim_control = None
    simio = None
    try:
        import pathlib
        cmapi.Project.load(pathlib.Path(r"C:\IPG2026\CM_Projects\CM_15"))

        servers = cmapi.query_aposerverinfos("localhost")
        if not servers:
            print("[ERROR] No running CarMaker instance found.")
            print("[ERROR] Start CarMaker GUI and load a TestRun first.")
            return
        print(f"[API] Found {len(servers)} CarMaker server(s) on localhost")

        master = ApoServer()
        master.set_sinfo(cmapi.ApoServerInfo())
        master.set_host("localhost")

        sim_control = await SimControlInteractive.create_with_master(master)
        await sim_control.connect()
        simio = sim_control.get_simio()
        print("[API] APO connected. DVA access ready.")
    except Exception as e:
        print(f"[ERROR] APO connection failed: {e}")
        return

    print("[API] Please start the simulation from CarMaker GUI if not already running.")

    # ── 3. Take longitudinal control ───────────────────────────────────────
    try:
        simio.dva_write_absolute_value(cfg.DM_LONG_SOURCE, 1, DVADuration.permanent)
        print("[CONTROL] Longitudinal source set to External.")
    except Exception as e:
        print(f"[WARNING] Could not set DM.Long.Source: {e}")
        print("[WARNING] Falling back to direct brake/gas DVA writes.")

    # Release brake and set initial gas
    simio.dva_write_absolute_value(cfg.DM_BRAKE, 0.0, DVADuration.permanent)
    simio.dva_write_absolute_value(cfg.DM_GAS, cfg.ACCEL_GAS_PEDAL, DVADuration.permanent)

    print("\n" + "=" * 60)
    print("[AEB] CONTROL AUTHORITY ESTABLISHED")
    print(f"[AEB] Target speed: {cfg.TARGET_SPEED_KPH} km/h")
    print(f"[AEB] Stop distance: {cfg.STOP_DISTANCE_M} m from target")
    print("=" * 60 + "\n")

    # ── 4. Init helpers ────────────────────────────────────────────────────
    logger = AEBLogger()
    ttc_calc = TTCCalculator()
    brake_calc = StopDistanceCalculator()

    state = cfg.STATE_ACCELERATING
    tick = 0
    _prev_brake = 0.0

    try:
        while True:
            # ── READ SENSORS ───────────────────────────────────────────────
            try:
                (ego_speed, ego_ax, yaw_rate, sim_time,
                 radar_dist, traffic_dist, traffic_vel) = await simio.dva_read_async(
                    cfg.VEHICLE_SPEED,
                    cfg.VEHICLE_AX,
                    cfg.YAW_RATE,
                    cfg.SIM_TIME,
                    cfg.RADAR_OBJ_DIST,
                    cfg.TRAFFIC_AHEAD_DIST,
                    cfg.TRAFFIC_AHEAD_VEL,
                )
            except Exception as e:
                print(f"[ERROR] DVA read failed: {e}")
                await asyncio.sleep(1.0 / cfg.CONTROL_HZ)
                tick += 1
                continue

            ego_speed_kph = ego_speed * 3.6

            # Use best available distance (radar or traffic-ahead)
            # Radar returns 0 when no target → fall back to traffic quantity
            if radar_dist > 0.5:
                obj_dist = radar_dist
            elif traffic_dist > 0.5:
                obj_dist = traffic_dist
            else:
                obj_dist = cfg.RADAR_DETECTION_RANGE_M  # No object seen

            ttc = ttc_calc.update(ego_speed, obj_dist, traffic_vel)

            # ── STATE MACHINE ──────────────────────────────────────────────
            gas_cmd = 0.0
            brake_cmd = 0.0

            if state == cfg.STATE_ACCELERATING:
                # Accelerate until target speed reached
                gas_cmd = cfg.ACCEL_GAS_PEDAL
                brake_cmd = 0.0

                if ego_speed >= cfg.TARGET_SPEED_MS - cfg.SPEED_TOLERANCE_MS:
                    state = cfg.STATE_CRUISING
                    print(f"[AEB t={sim_time:.1f}s] Reached {ego_speed_kph:.1f} km/h → CRUISING")

                # Pre-empt: if object very close even during accel, brake
                if obj_dist < cfg.AEB_TRIGGER_DISTANCE_M and ttc < cfg.TTC_THRESHOLD_S:
                    state = cfg.STATE_BRAKING
                    print(f"[AEB t={sim_time:.1f}s] Object at {obj_dist:.1f}m during accel → BRAKING")

            elif state == cfg.STATE_CRUISING:
                # Maintain speed with light throttle
                if ego_speed < cfg.TARGET_SPEED_MS - cfg.SPEED_TOLERANCE_MS:
                    gas_cmd = cfg.CRUISE_GAS_PEDAL
                else:
                    gas_cmd = 0.05  # Coast

                # Check AEB trigger
                if obj_dist < cfg.AEB_TRIGGER_DISTANCE_M or ttc < cfg.TTC_THRESHOLD_S:
                    state = cfg.STATE_BRAKING
                    print(f"[AEB t={sim_time:.1f}s] Object detected at {obj_dist:.1f}m "
                          f"(TTC={ttc:.2f}s) → BRAKING")

            elif state == cfg.STATE_BRAKING:
                gas_cmd = 0.0
                brake_cmd = brake_calc.compute_brake(ego_speed, obj_dist)

                # Emergency full brake
                if obj_dist < cfg.EMERGENCY_DISTANCE_M:
                    brake_cmd = cfg.MAX_BRAKE

                # Check if stopped
                if ego_speed < cfg.FULL_STOP_SPEED_MS:
                    state = cfg.STATE_STOPPED
                    final_gap = obj_dist
                    print(f"\n[AEB t={sim_time:.1f}s] VEHICLE STOPPED")
                    print(f"[AEB] Final gap to target: {final_gap:.2f} m "
                          f"(desired: {cfg.STOP_DISTANCE_M} m, "
                          f"error: {final_gap - cfg.STOP_DISTANCE_M:+.2f} m)")

            elif state == cfg.STATE_STOPPED:
                gas_cmd = 0.0
                brake_cmd = cfg.MAX_BRAKE  # Hold brake

            # ── RATE LIMIT BRAKE ───────────────────────────────────────────
            brake_cmd = rate_limit_brake(brake_cmd, _prev_brake)
            _prev_brake = brake_cmd

            # ── WRITE COMMANDS ─────────────────────────────────────────────
            try:
                simio.dva_write_absolute_value(cfg.DM_GAS, gas_cmd, DVADuration.cycle)
                simio.dva_write_absolute_value(cfg.DM_BRAKE, brake_cmd, DVADuration.cycle)
            except Exception as e:
                print(f"[ERROR] DVA write failed: {e}")

            # ── LOGGING ────────────────────────────────────────────────────
            try:
                logger.log(
                    sim_time, state, ego_speed, ego_ax,
                    radar_dist, traffic_dist, traffic_vel,
                    ttc, brake_cmd, gas_cmd, yaw_rate
                )
            except Exception as e:
                print(f"[ERROR] Logging failed: {e}")

            # ── TELEMETRY ──────────────────────────────────────────────────
            if tick % cfg.PRINT_EVERY_N_TICKS == 0:
                state_name = cfg.STATE_NAMES.get(state, "?")
                print(
                    f"[AEB t={sim_time:.1f}s] "
                    f"{state_name:13s} | "
                    f"v={ego_speed_kph:5.1f} km/h | "
                    f"dist={obj_dist:6.1f} m | "
                    f"TTC={ttc:5.1f} s | "
                    f"gas={gas_cmd:.2f} | "
                    f"brake={brake_cmd:.2f}"
                )

            tick += 1

            # Stop the loop once vehicle is fully stopped for a few seconds
            if state == cfg.STATE_STOPPED and tick > 100:
                print("[AEB] Test complete.")
                break

            await asyncio.sleep(1.0 / cfg.CONTROL_HZ)

    except KeyboardInterrupt:
        print("\n[AEB] Stopped by user.")
    finally:
        # Release control back to driver model
        logger.close()
        try:
            simio.dva_write_absolute_value(cfg.DM_BRAKE, 0.0, DVADuration.permanent)
            simio.dva_write_absolute_value(cfg.DM_GAS, 0.0, DVADuration.permanent)
        except:
            pass
        try:
            simio.dva_write_absolute_value(cfg.DM_LONG_SOURCE, 0, DVADuration.permanent)
        except:
            pass
        try:
            await sim_control.disconnect()
        except:
            pass
        print(f"[AEB] Finished. Final state: {cfg.STATE_NAMES.get(state, '?')}")


if __name__ == "__main__":
    cmapi.Task.run_main_task(run())
