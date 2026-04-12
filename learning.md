User verse learning system for scripture memorization.

This module models a structured repetition-based learning strategy for
memorizing Bible verses. Each user progresses through a series of learning
phases based on how many times they have recited a verse (tracked via a tally).

## Learning Strategy

The system is built on a repetition schedule:

- Days 1–5 (Active phase):
  High repetition per day:
  Day 1 → 25
  Day 2 → 20
  Day 3 → 15
  Day 4 → 10
  Day 5 → 5
  Total tally after completion: 75

- Days 6–50 (Daily phase):
  One repetition per day for 45 days
  Total tally after completion: 120

- Weeks 8–14 (Weekly phase):
  One repetition per week for 7 weeks
  Total tally after completion: 127

- Ongoing (Monthly phase):
  One repetition per month indefinitely
  Total tally: 128+

Phases are derived from the cumulative tally:

    not_started   → tally = 0
    active        → tally 1–75
    daily         → tally 76–120
    weekly        → tally 121–127
    monthly       → tally 128+

## UserVerse Model

Represents a user's relationship with a specific memory verse.

It tracks:

- The user and the verse
- Queue ordering for learning priority
- The cumulative tally of recitations

## Ordering

The `order` field controls the position of a verse in the user's queue.

- Add to end: order = max(user orders) + 1
- Learn next: order = min(user orders) - 1

Ordering values are not required to be contiguous or positive. The frontend
simply sorts by this value.

## Uniqueness

Each user can only have one record per memory verse. This is enforced via
a database-level unique constraint on (user, memory_verse).
