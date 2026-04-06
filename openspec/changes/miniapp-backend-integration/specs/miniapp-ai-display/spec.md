## ADDED Requirements

### Requirement: Home page shows AI analysis status
The system SHALL display AI-generated feeding status on the home page.

#### Scenario: Normal status display
- **WHEN** AI analysis indicates normal feeding status
- **THEN** system shows green status indicator
- **AND** displays "喂养正常" message

#### Scenario: Low status display
- **WHEN** AI analysis indicates low feeding
- **THEN** system shows yellow/orange warning indicator
- **AND** displays specific issue description

#### Scenario: High status display
- **WHEN** AI analysis indicates over-feeding
- **THEN** system shows appropriate indicator
- **AND** displays relevant information

### Requirement: Home page shows AI recommendations
The system SHALL display personalized AI recommendations on the home page.

#### Scenario: Show recommendations
- **WHEN** there are AI-generated recommendations
- **THEN** system shows top 1-2 recommendations in a card
- **AND** user can tap to see all recommendations

#### Scenario: No issues
- **WHEN** feeding status is normal with no issues
- **THEN** system shows encouraging message like "喂养情况良好，继续保持"

### Requirement: Home page shows next feeding suggestion
The system SHALL display suggested next feeding time from AI analysis.

#### Scenario: Show next feeding time
- **WHEN** AI analysis provides next_feeding_suggestion
- **THEN** system displays "建议下次喂养: HH:MM"
- **AND** time is formatted in user-friendly way

### Requirement: User can request detailed AI analysis
The system SHALL allow user to view full AI analysis.

#### Scenario: View detailed analysis
- **WHEN** user taps on AI status card
- **THEN** system shows detailed analysis page
- **AND** displays all metrics, issues, and recommendations

### Requirement: AI analysis requires baby config
The system SHALL prompt user to set baby info if not configured.

#### Scenario: Missing birth date
- **WHEN** baby birth_date is not set
- **THEN** AI analysis shows lower confidence
- **AND** prompts user to set birth date in settings