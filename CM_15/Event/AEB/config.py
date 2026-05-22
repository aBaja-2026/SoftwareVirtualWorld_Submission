"""
config.py
Centralized configuration for the AEB (Automatic Emergency Braking) system.
Single source of truth for all tunable parameters.
"""

# ── CONTROL LOOP ───────────────────────────────────────────────────────────
CONTROL_HZ = 50                  # Control loop frequency [Hz]

# ── AEB SCENARIO PARAMETERS ───────────────────────────────────────────────
TARGET_SPEED_KPH = 30.0                           # Cruise speed [km/h]
TARGET_SPEED_MS = TARGET_SPEED_KPH / 3.6          # Cruise speed [m/s]  ≈ 8.33
STOP_DISTANCE_M = 6.0                             # Desired gap at full stop [m]
SPEED_TOLERANCE_MS = 0.5                           # Consider target reached within ± [m/s]
FULL_STOP_SPEED_MS = 0.1                           # Speed below which = stopped [m/s]

# ── ACCELERATION PHASE ─────────────────────────────────────────────────────
ACCEL_GAS_PEDAL = 0.4            # Gas pedal position during acceleration [0-1]
CRUISE_GAS_PEDAL = 0.15          # Light throttle to maintain cruise speed

# ── BRAKING CONTROLLER ─────────────────────────────────────────────────────
# Proportional braking: brake = Kp * (1 / (distance - stop_gap))
# Capped to [0, 1] and ramped for comfort
BRAKE_KP = 2.5                   # Proportional gain for distance-based braking
BRAKE_KD = 0.3                   # Derivative gain (rate of distance closure)
MAX_BRAKE = 1.0                  # Maximum brake pedal value [0-1]
MIN_BRAKE = 0.05                 # Minimum brake application when decelerating
BRAKE_RATE_LIMIT = 0.15          # Max brake change per control cycle [0-1]

# ── DETECTION & DECISION THRESHOLDS ───────────────────────────────────────
RADAR_DETECTION_RANGE_M = 150.0  # Max radar range [m]
AEB_TRIGGER_DISTANCE_M = 50.0   # Start braking when object closer than this [m]
TTC_THRESHOLD_S = 3.0            # Time-to-collision threshold to trigger AEB [s]
EMERGENCY_DISTANCE_M = 10.0      # Full brake below this distance [m]

# ── VEHICLE PARAMETERS ─────────────────────────────────────────────────────
WHEELBASE_M = 2.8                # Front-to-rear axle [m]
VEHICLE_LENGTH_M = 4.5           # Approximate vehicle length [m]

# ── DVA QUANTITY NAMES ─────────────────────────────────────────────────────
# Vehicle dynamics
VEHICLE_SPEED = "Car.v"                            # Vehicle speed [m/s]
VEHICLE_AX = "Car.ax"                              # Longitudinal acceleration [m/s²]
VEHICLE_AY = "Car.ay"                              # Lateral acceleration [m/s²]
YAW_RATE = "Car.YawRate"                           # Yaw rate [rad/s]
VEHICLE_DISTANCE = "Car.Distance"                  # Odometer distance [m]
SIM_TIME = "Time"                                  # Simulation time [s]

# Driver model control (brake & gas)
DM_BRAKE = "DM.Brake"                             # Brake pedal [0-1]
DM_GAS = "DM.Gas"                                 # Gas pedal [0-1]
DM_LONG_SOURCE = "DM.Long.Source"                  # 0=Driver, 1=External

# Radar sensor — object-level (front radar, relevant target)
RADAR_OBJ_DIST = "Sensor.Object.RadarL.relvTgt.NearPnt.ds_p"  # Distance to nearest point [m]

# Traffic ahead (CarMaker built-in)
TRAFFIC_AHEAD_DIST = "Traffic.Ahead.Dist"          # Distance to vehicle ahead [m]
TRAFFIC_AHEAD_VEL = "Traffic.Ahead.Vel"            # Velocity of vehicle ahead [m/s]

# ── AEB STATE MACHINE ─────────────────────────────────────────────────────
# States
STATE_ACCELERATING = 0
STATE_CRUISING = 1
STATE_BRAKING = 2
STATE_STOPPED = 3

STATE_NAMES = {
    STATE_ACCELERATING: "ACCELERATING",
    STATE_CRUISING: "CRUISING",
    STATE_BRAKING: "BRAKING",
    STATE_STOPPED: "STOPPED"
}

# ── LOGGING ────────────────────────────────────────────────────────────────
LOG_DIR = r"C:\IPG2026\CM_Projects\CM_15\Event\AEB\Logs"
PRINT_TELEMETRY = True
PRINT_EVERY_N_TICKS = 25         # Print every N control ticks
