# Requirements Clarifications - 2026-03-18

Source: User clarifications provided on 2026-03-18.  
Priority: Documentation is source of truth over current code.

## Clarified Decisions

1. Quality thresholds for processing:
- Use strong quality gates suitable for production.
- Validate image size and face visibility.
- Ensure key face landmarks/features are clearly visible before processing.

2. Recognition threshold:
- Current match threshold: `> 0.8`
- Must remain configurable in config file.

3. Attendance window configuration:
- Dynamic and user-configurable via database settings.
- Refer to DB design for structure.

4. Entry/exit and attendance calculation:
- Store all entry/exit records.
- Attendance evaluation uses configured `MIN_TIME`.
- Effective worked duration = difference between first entry and last exit (for now).

5. Data retention:
- Keep relevant records/data for up to 35 days (current policy).

6. Camera ingestion assumptions:
- Continuous ceiling/top camera: 5 FPS stream, but process 1 frame per second for recognition.
- Wall camera: same frame sampling rule, plus face area must be `> 50%` of frame.

7. Scale expectation handling:
- Expected face base: 10,000-50,000 persons (average around 500 in typical active context).
- System design should account for this without additional user-provided TPS/RPS numbers for now.

8. Storage architecture direction:
- Build a storage interface abstraction.
- Support plugin-like add/remove storage backends.
- Recognition/image retrieval should work through this pluggable storage layer.

9. External integration priority:
- No priority right now; do not focus on it currently.

## Open Clarification Status

- No blocking doubts remain from these points.
- If needed later, define exact numeric quality-gate values (minimum resolution, blur threshold, minimum inter-eye distance, illumination bounds) in a dedicated quality policy document.

