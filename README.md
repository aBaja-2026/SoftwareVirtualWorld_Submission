# aBAJA 2026 Tech Team — Submission

### aBAJA SAEINDIA 2026 | Software Virtual World Simulation

---

## Repository Structure

```
├── src/LKA/      ← Lane Keep Assist stack (perception, planning, control)
├── config/       ← Sensor configs, vehicle parameters
├── scenarios/    ← Scenario files (mandatory + self-created)
├── results/
│   ├── AEB/
│   ├── LKA/
│   ├── Endurance/
│   └── Self_Created/
├── docs/         ← Architecture doc, sensor config, hardware report
└── README.md
```

## Simulator & Setup Instructions

- **Simulator:** IPG CarMaker 15.0, with MovieNX rendering for camera-based sensing.
- **Camera sensor:** Camera RSI sensor delivering 640×480 RGB frames over TCP (port 2210) at ~30 Hz.
- **Scenario authoring:** Custom road and scenario environments built in RoadRunner, exported and loaded into CarMaker for simulation.
- **Data logging:** Vector loggers used to capture real-time vehicle navigation data during physical trials, for correlation against simulated LKA behavior; in-sim telemetry (steering angle, lateral error, speed) is also logged to CSV every tick by `Lka_utils.py`.
- **Target vehicle speed:** 30 km/h.
- **Control interface:** IPG CarMaker Python API (APO interface), used by `LKA_Main.py` to take over steering, gas, and brake and to read vehicle speed/yaw rate from the simulation.

**Setup steps:**
1. Install IPG CarMaker 15.0 and RoadRunner.
2. Clone this repository:
   ```bash
   git clone https://github.com/aBaja-2026/SoftwareVirtualWorld_Submission.git
   ```
3. Open the CarMaker project in `config/` and load the vehicle from `Data/Vehicle/Examples/Demo_IPG_CompanyCar_SensorGroundTruth_LanesAndRoots`.
4. **Camera exposure (important):** the default CarMaker exposure settings under-expose the scene by ~5 stops and will break lane detection. Set:
   | Parameter | Value |
   |---|---|
   | ISO | 800 |
   | F-Stop | 2.8 |
   | Shutter Speed | 250 Hz |
   | Tone Mapping | Filmic |
5. If exposure changes made in the vehicle editor don't appear to take effect, delete the vehicle's `.tmp` files and restart CarMaker — CarMaker caches edits there and won't reflect changes to the main vehicle file until the `.tmp` copies are cleared.
6. Load a scenario from `scenarios/` and run `LKA_Main.py` to start the control loop.


## System Overview

The Lane Keep Assist (LKA) stack implemented in `src/LKA/` performs:

- **Perception:** Bird's-Eye-View (BEV) transform + sliding window lane search (`sensor_fusion.py`), selected after evaluating and ruling out CLAHE + percentile thresholding, Hough Transform, adaptive thresholding, and Frangi ridge detection — each failed under the simulator's low-contrast camera output (raw pixel values of ~10–30/255) or on curved/dashed lane geometry. BEV removes perspective foreshortening, a bottom-half histogram initializes the search, and the sliding window tracks lanes upward frame-by-frame, naturally bridging dashed-line gaps (fit caching bridges up to 15 frames of dropout).
- **State estimation / lateral error:** Polynomial fitting to the lane pixels found by the sliding window, converted to a metric lateral offset via a BEV calibrated to meters (`sensor_fusion.py`).
- **Control:** Pure Pursuit + PID (`LKA_Main.py`). Pure Pursuit computes a baseline steering angle to follow an arc to a lookahead point 5.0 m ahead on the detected lane, using the vehicle wheelbase (2.622 m) and steering ratio (16:1) so the response scales naturally with vehicle speed and road curvature; a PID layer on top corrects residual steady-state error. Steering commands are rate-limited (0.03 rad/frame, ±0.524 rad max) before being sent back to CarMaker. A standalone PID (no geometric lookahead) was evaluated first but was prone to oscillation, integral windup during vision dropouts, and poor curve tracking — Pure Pursuit was added to address this.

**Module breakdown:**
| File | Role |
|---|---|
| `LKA_Main.py` | Main control loop; bridges perception and CarMaker via the APO interface, runs Pure Pursuit + PID, rate-limits and sends the final steering command. |
| `sensor_fusion.py` | Computer vision module: BEV warp, sliding window search, polynomial fitting for lane center and lateral deviation. |
| `config.py` | Centralizes tunable parameters (vehicle speed, PID gains, camera resolution) and CarMaker Data Variable Access (DVA) mappings. |
| `Lka_utils.py` | RMSE tracker for lane-centering performance, a DNF watchdog for lane-departure timeout, and a per-tick CSV telemetry logger. |

---

📋 See [Submission_Guidelines.md](./Submission_Guidelines.md) for full event rules, deliverables checklist, and scoring criteria.
