## ADDED Requirements

### Requirement: User can view daily report
The system SHALL provide access to daily feeding report with AI summary.

#### Scenario: View today's report
- **WHEN** user navigates to daily report
- **THEN** system fetches GET /api/summary/daily/ai
- **AND** displays AI-generated summary

#### Scenario: View historical report
- **WHEN** user selects a past date
- **THEN** system fetches report for that date
- **AND** displays historical data

### Requirement: Daily report shows feeding summary
The system SHALL display feeding data summary in daily report.

#### Scenario: Display feeding data
- **WHEN** daily report is shown
- **THEN** system displays total milk volume for the day
- **AND** displays feeding count
- **AND** displays average interval if available

### Requirement: Daily report shows AI analysis
The system SHALL display AI analysis in daily report.

#### Scenario: Display AI analysis
- **WHEN** daily report is shown
- **THEN** system displays AI-generated summary text
- **AND** displays any identified issues
- **AND** displays recommendations

### Requirement: Daily report handles no data
The system SHALL handle cases where no records exist.

#### Scenario: No records for date
- **WHEN** selected date has no records
- **THEN** system shows "今日无记录" message
- **AND** suggests user to add records