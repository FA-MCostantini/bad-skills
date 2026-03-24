# EARS Patterns — Full Reference

Source: Alistair Mavin, Rolls-Royce PLC — RE 2009
Reference: https://alistairmavin.com/ears/

---

## Pattern 1: Ubiquitous

**Use when:** The behavior is always active. No condition, no trigger.
Typically used for non-functional requirements, invariants, and
constraints that must hold throughout the entire system lifetime.

**Template:**
```
The <system name> shall <system response>.
```

**Examples:**
```
The authentication service shall encrypt all passwords using bcrypt
with a minimum cost factor of 12.

The mobile application shall have a binary size of no more than 50 MB.

The API shall be versioned using semantic versioning (MAJOR.MINOR.PATCH).
```

**Anti-examples (do not write like this):**
```
❌ The system should be fast.                 → vague, no measurable response
❌ Data will be stored securely.              → passive voice, hidden actor
❌ The app shall be user-friendly and fast.   → compound, two behaviors
```

---

## Pattern 2: State-Driven

**Use when:** The behavior is active *continuously* as long as a
specified state persists. The system is *in* a condition, not reacting
to a single event.

**Template:**
```
While <precondition(s)>, the <system name> shall <system response>.
```

**Key distinction from Event-Driven:**
- `While` = sustained condition (the system *is* in a state)
- `When` = instantaneous trigger (something *happens*)

**Examples:**
```
While the user session is active, the payment service shall refresh
the authentication token every 15 minutes.

While the database connection pool is exhausted, the API gateway shall
return HTTP 503 with a Retry-After header set to 30 seconds.

While the aircraft is on the ground, the engine control system shall
limit thrust to taxi power settings.
```

**Multiple preconditions** (joined with `and`/`or`):
```
While the vehicle is stationary and the parking brake is engaged,
the infotainment system shall enable full touchscreen interaction.
```

---

## Pattern 3: Event-Driven

**Use when:** The behavior is triggered by a discrete, instantaneous
event. The system must respond *when* something happens.

**Template:**
```
When <trigger>, the <system name> shall <system response>.
```

**Examples:**
```
When the user submits the registration form, the identity service shall
send an email verification link to the provided address within 30 seconds.

When a payment transaction exceeds €10,000, the fraud detection system
shall flag the transaction for manual review and suspend processing.

When the CPU utilisation exceeds 90% for more than 60 seconds, the
autoscaler shall provision one additional compute instance.
```

**Response with timing constraint:**
```
When the user selects "Logout", the session manager shall invalidate
the session token and redirect the user to the login page within 500ms.
```

---

## Pattern 4: Optional Feature

**Use when:** The requirement applies only to products or configurations
that include a specific optional feature, hardware component, or
licensed capability.

**Template:**
```
Where <feature is included>, the <system name> shall <system response>.
```

**Examples:**
```
Where the premium subscription is active, the reporting module shall
export data in XLSX, CSV, and PDF formats.

Where the hardware security module (HSM) is installed, the key management
service shall store all private keys exclusively within the HSM boundary.

Where two-factor authentication is enabled, the login service shall
prompt the user for a TOTP code after successful password verification.
```

**Note:** `Where` describes a *static configuration* or *product variant*,
not a runtime state. For runtime conditions, use `While` or `When`.

---

## Pattern 5: Unwanted Behavior

**Use when:** Specifying the system's required response to an error,
failure, exception, or any undesired situation. This pattern makes
error handling explicit and testable.

**Template:**
```
If <trigger>, then the <system name> shall <system response>.
```

**Key distinction from Event-Driven:**
- `When` = expected, normal trigger in the happy path
- `If … then` = undesired, exceptional, or error condition

**Examples:**
```
If the external payment provider returns an error code, then the
checkout service shall display an error message to the user and
preserve the cart contents for at least 24 hours.

If the uploaded file exceeds 10 MB, then the file service shall
reject the upload and return HTTP 413 with a descriptive error body.

If the database write fails after three retry attempts, then the
order service shall publish a dead-letter event to the audit queue
and return HTTP 500 to the caller.

If an invalid API key is presented, then the gateway shall return
HTTP 401 and log the source IP address without disclosing the
authentication mechanism.
```

---

## Pattern 6: Complex

**Use when:** The behavior requires *both* a sustained precondition
(`While`) *and* a discrete trigger (`When`). Use this pattern only
when both elements are genuinely necessary — do not default to it.

**Template:**
```
While <precondition(s)>, when <trigger>, the <system name> shall <system response>.
```

**Examples:**
```
While the aircraft is in flight, when the autopilot disengage button
is pressed, the flight control system shall transfer control authority
to the pilot and activate the autopilot disengaged audio alert.

While the maintenance window is active, when a new deployment is
initiated, the CI/CD pipeline shall skip the production smoke tests
and notify the on-call engineer via PagerDuty.

While a database migration is in progress, when a write request is
received, the API shall queue the request and return HTTP 202 Accepted
with an estimated completion timestamp.
```

**Warning:** Complex requirements are harder to validate. If the
precondition and trigger are always paired, consider whether the state
implies the trigger or vice versa, and simplify to a single-pattern
requirement.

---

## Pattern Combination Reference

```
[While <state>] [When/If <trigger>] the <system> shall <response>.
    ^                 ^                    ^              ^
    |                 |                    |              |
 0..N times        0..1 times          Required       Required
 (State-Driven)  (Event/Unwanted)    (System Name)  (1+ responses)
```

### Decision Tree

```
Does the behavior depend on a condition?
├── No  → Ubiquitous
└── Yes → Is it a runtime system state (continuous)?
          ├── Yes → State-Driven (While) or Complex (While + When)
          │         Is there also a discrete trigger?
          │         ├── No  → State-Driven (While)
          │         └── Yes → Complex (While + When)
          └── No  → Is the trigger expected (happy path)?
                    ├── Yes → Event-Driven (When)
                    └── No  → Is it a product/config variant?
                              ├── Yes → Optional Feature (Where)
                              └── No  → Unwanted Behavior (If…then)
```
