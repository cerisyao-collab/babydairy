## ADDED Requirements

### Requirement: File size monitoring
The system SHALL monitor daily file sizes to ensure they remain under 200KB.

#### Scenario: Daily file naturally stays under limit
- **WHEN** records are added throughout a day
- **THEN** the file size remains under 200KB (typical day: 2-10KB)

#### Scenario: Warning if file approaches limit
- **WHEN** a daily file exceeds 150KB (75% of limit)
- **THEN** the system logs a warning for investigation
