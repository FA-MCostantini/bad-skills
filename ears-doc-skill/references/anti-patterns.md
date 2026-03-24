# EARS Anti-Patterns — Requirements Defect Catalog

Reference: Mavin et al. (RE 2009), Jama Software EARS Guide,
Rolls-Royce internal defect taxonomy.

Each anti-pattern maps to one or more of the eight classical requirement
defects identified in the original EARS research.

---

## Defect 1: Ambiguity

**Definition:** The requirement has more than one valid interpretation.

### Anti-Pattern 1.1 — Ambiguous Pronoun
```
❌ When the user logs in, it shall display the dashboard.
   → What is "it"? The system? The browser? The API?
```
**Fix:** Name the system explicitly.
```
✅ When the user completes authentication, the web application shall
   render the user dashboard within 1 second.
```

### Anti-Pattern 1.2 — Ambiguous Scope of "and/or"
```
❌ The system shall validate the username and password or token.
   → Is it (username AND password) OR (token)? Or username AND (password OR token)?
```
**Fix:** Split into separate requirements.
```
✅ REQ-AUTH-001: The authentication service shall accept username and
   password as credentials.

   REQ-AUTH-002: Where API access is enabled, the authentication service
   shall accept a Bearer token as an alternative credential.
```

### Anti-Pattern 1.3 — Undefined Temporal Reference
```
❌ The system shall save data periodically.
   → How often? Under what conditions?
```
**Fix:** Quantify.
```
✅ While a user session is active, the editor shall auto-save the
   document every 60 seconds.
```

---

## Defect 2: Vagueness

**Definition:** The requirement uses imprecise language that cannot be
objectively measured or tested.

### Forbidden Qualifiers — Never Use These

| Forbidden | Replace with |
|---|---|
| quickly | within N milliseconds/seconds |
| efficiently | using no more than N% CPU / N MB memory |
| user-friendly | (specify the exact interaction behavior) |
| appropriate | (specify the exact value or rule) |
| adequate | (specify the minimum acceptable threshold) |
| reasonable | (specify the exact criterion) |
| robust | (specify the failure mode and recovery behavior) |
| flexible | (specify the exact variability required) |
| scalable | handles N concurrent users / N requests per second |
| secure | (specify the exact security control: encryption, auth, etc.) |
| reliable | available 99.9% of the time / MTBF > N hours |
| maintainable | (specify the structural or architectural constraint) |
| easy | (avoid — this is subjective; specify the interaction instead) |

### Anti-Pattern 2.1 — Vague Performance Target
```
❌ The API shall respond quickly to requests.
```
**Fix:**
```
✅ The API shall return a response to read requests within 200ms at the
   99th percentile under a load of 1,000 concurrent users.
```

### Anti-Pattern 2.2 — Vague Security Statement
```
❌ The system shall store data securely.
```
**Fix:**
```
✅ The database service shall encrypt all personally identifiable
   information (PII) at rest using AES-256-GCM.
```

---

## Defect 3: Duplication

**Definition:** The same behavioral requirement appears more than once,
possibly with slight wording differences, creating a maintenance and
consistency risk.

**Detection:** Cross-reference requirements by trigger and system response.
If two requirements activate under the same conditions and produce the
same response, one is a duplicate.

**Fix:** Assign a unique ID to each requirement and use references
instead of restating.

---

## Defect 4: Complexity

**Definition:** A single requirement statement describes multiple
distinct behaviors that should be independently testable.

### Anti-Pattern 4.1 — Compound Response
```
❌ When the order is placed, the order service shall deduct inventory,
   send a confirmation email, notify the warehouse, and update the
   user's order history.
```
**Fix:** One requirement per testable behavior.
```
✅ REQ-ORD-001: When an order is confirmed, the inventory service shall
   decrement the product stock count by the ordered quantity.

   REQ-ORD-002: When an order is confirmed, the notification service
   shall send an order confirmation email to the customer within 60 seconds.

   REQ-ORD-003: When an order is confirmed, the fulfillment service shall
   create a pick-list entry in the warehouse management system.

   REQ-ORD-004: When an order is confirmed, the account service shall
   append the order record to the user's order history.
```

### Anti-Pattern 4.2 — Compound Precondition Hiding Two Behaviors
```
❌ While logged in and on the checkout page, the cart service shall
   display items and calculate the total.
```
**Fix:**
```
✅ REQ-CART-001: While the user is on the checkout page, the cart service
   shall display all items in the active cart.

   REQ-CART-002: While the user is on the checkout page, the cart service
   shall display the calculated subtotal, applicable taxes, and order total.
```

---

## Defect 5: Omission

**Definition:** The requirement is missing information necessary to
implement or test it. Common omissions: missing trigger, missing
precondition, undefined system name, unspecified response.

### Anti-Pattern 5.1 — Missing Trigger
```
❌ The system shall display an error message.
   → When? Under what conditions?
```
**Fix:**
```
✅ If the login attempt fails due to invalid credentials, then the
   authentication service shall display the error message "Invalid
   username or password" without specifying which field is incorrect.
```

### Anti-Pattern 5.2 — Missing Quantification in Response
```
❌ When a new user registers, the system shall send a welcome email.
   → Within what time frame? To what address? With what content?
```
**Fix:**
```
✅ When a new user completes registration, the email service shall
   send a welcome email to the registered address within 5 minutes,
   containing the user's username and a link to the getting-started guide.
```

### Anti-Pattern 5.3 — Missing Error Path
Every happy-path `When` requirement should have a corresponding
`If … then` requirement for the failure case.
```
❌ When the user submits payment, the payment service shall process
   the transaction.
   → What if the payment fails? What if the network times out?
```
**Fix:** Add unwanted-behavior requirements.
```
✅ REQ-PAY-001: When the user submits payment, the payment service shall
   submit the transaction to the payment provider and display a processing
   indicator.

   REQ-PAY-002: If the payment provider returns a decline code, then the
   payment service shall display the message "Payment declined. Please
   check your card details or use a different payment method" and preserve
   the cart contents.

   REQ-PAY-003: If the payment provider does not respond within 10 seconds,
   then the payment service shall cancel the transaction attempt, display
   a timeout message, and preserve the cart contents.
```

---

## Defect 6: Wordiness

**Definition:** The requirement contains unnecessary prose that adds
length without adding meaning.

### Anti-Pattern 6.1 — Preamble and justification mixed in
```
❌ Due to the importance of data integrity and in order to ensure that
   users can always recover their work in the event of an unexpected
   interruption, the system shall implement an auto-save feature.
```
**Fix:** State the requirement. Put rationale in a separate `Rationale` field.
```
✅ While a document is open for editing, the editor shall auto-save
   the document to local storage every 30 seconds.

   Rationale: Preserves unsaved work in case of session interruption.
```

---

## Defect 7: Subjectivity

**Definition:** The requirement contains language that reflects an
opinion, assumption, or value judgment rather than an objective,
measurable criterion.

### Anti-Pattern 7.1 — Opinion-based quality
```
❌ The user interface shall be attractive and intuitive.
```
**Fix:** Specify the observable interaction behavior.
```
✅ The onboarding flow shall guide a first-time user to complete account
   setup in no more than 5 steps, each containing no more than one
   primary action.
```

### Anti-Pattern 7.2 — Assumed shared understanding
```
❌ The system shall follow industry best practices for security.
   → Which practices? Whose definition of "best"?
```
**Fix:**
```
✅ The application shall implement the OWASP Top 10 security controls
   as defined in the OWASP Application Security Verification Standard
   (ASVS) Level 2.
```

---

## Defect 8: Forward Reference

**Definition:** The requirement refers to a term, system, or behavior
defined elsewhere without an explicit link, making the requirement
incomprehensible in isolation.

### Anti-Pattern 8.1 — Undefined term
```
❌ The system shall process the event as specified.
   → Which event? Specified where?
```
**Fix:** Define the term in the glossary and reference it explicitly.
```
✅ When a PasswordResetEvent (see Glossary §3.4) is received, the
   identity service shall invalidate all active sessions for the
   associated user account.
```

### Anti-Pattern 8.2 — Dangling "as described above"
```
❌ The system shall handle errors as described above.
```
**Fix:** Cite the requirement ID.
```
✅ If a network error occurs during file upload, the storage service
   shall apply the retry policy defined in REQ-STOR-012.
```

---

## Quick Review Checklist

For each requirement being reviewed, verify:

- [ ] System name is explicit (not "it", "the system" without name, etc.)
- [ ] No forbidden vague qualifiers present
- [ ] Single behavior — not joined by `and` with multiple distinct responses
- [ ] Trigger is specified (for Event-Driven and Unwanted Behavior)
- [ ] Precondition is specified (for State-Driven and Complex)
- [ ] All numbers and thresholds are explicit
- [ ] Corresponding error-path requirements exist for each happy path
- [ ] All referenced terms are defined in the glossary
- [ ] Unique ID assigned
- [ ] No duplicate found in the requirement set
- [ ] Rationale is present and non-trivial
- [ ] At least one acceptance criterion exists
