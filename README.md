# aBAJA 2026 Tech Team — Submission

### aBAJA SAEINDIA 2026 | Software Virtual World Simulation

**Team:** [FILL IN — team name / ID, e.g. CM_15]
**Members:** [FILL IN — names / roles, e.g. Simulation Lead, Controls, Perception]

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

- **Simulator:** IPG CarMaker 
- **Scenario authoring:** Custom road and scenario environments built in RoadRunner, exported and loaded into CarMaker for simulation.
- **Data logging:** Vector loggers used to capture real-time vehicle navigation data during physical trials, for correlation against simulated LKA behavior.

**Setup steps:**
1. Install IPG CarMaker  and RoadRunner.
2. Clone this repository:
   ```bash
   git clone https://github.com//aBaja-2026/SoftwareVirtualWorld_Submission.git
   ```
3. Open the CarMaker project in `config/`.
4. Load a scenario from `scenarios/`.
5. Run the simulation and confirm outputs are written to the matching subfolder under `results/`.

## System Overview

The Lane Keep Assist (LKA) stack implemented in `src/LKA/` performs:

- **Perception:** [FILL IN — e.g. lane boundary detection method/sensor used in simulation]
- **State estimation:** [FILL IN — e.g. Kalman filter or other fusion approach used to track lane position]
- **Control:** [FILL IN — e.g. PID / MPC / state-space controller used to compute steering correction]

The controller was validated in closed-loop simulation in CarMaker against both the mandatory scenarios and self-created scenarios (see `scenarios/` and `results/LKA/`), then cross-checked against on-track Vector logger data from physical trials to confirm simulated and real-world LKA behavior aligned.

[FILL IN a short paragraph on architecture — how perception, state estimation, and control modules connect, and any key parameters/tuning notes worth documenting for judges.]

---

📋 See [Submission_Guidelines.md](./Submission_Guidelines.md) for full event rules, deliverables checklist, and scoring criteria.
