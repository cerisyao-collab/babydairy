## ADDED Requirements

### Requirement: User can record breastfeeding
The system SHALL allow users to record breastfeeding sessions with one tap.

#### Scenario: Quick record breastfeeding
- **WHEN** user taps breastfeeding button
- **THEN** system creates feeding record with type "breast"
- **AND** timestamp is set to current time
- **AND** success toast is shown

#### Scenario: Record with error
- **WHEN** record creation fails
- **THEN** system shows error message
- **AND** user can retry

### Requirement: User can record formula feeding
The system SHALL allow users to record formula feeding with amount selection.

#### Scenario: Open formula modal
- **WHEN** user taps formula button
- **THEN** system shows modal with amount slider
- **AND** default amount is 150ml

#### Scenario: Select formula amount
- **WHEN** user adjusts slider
- **THEN** displayed amount updates in real-time
- **AND** range is 50ml to 300ml in 10ml steps

#### Scenario: Confirm formula record
- **WHEN** user taps confirm in modal
- **THEN** system creates feeding record with type "formula" and amount
- **AND** modal closes
- **AND** success toast shows amount

### Requirement: Feeding records are mapped to backend format
The system SHALL convert frontend record types to backend format correctly.

#### Scenario: Breastfeeding conversion
- **WHEN** recording breastfeeding
- **THEN** system sends type: "feeding" with feeding_type: "breast"

#### Scenario: Formula conversion
- **WHEN** recording formula
- **THEN** system sends type: "feeding" with feeding_type: "formula" and amount_ml

### Requirement: Recent feeding is displayed on home
The system SHALL show the most recent feeding record on the home page.

#### Scenario: Display recent feeding
- **WHEN** there is at least one feeding record today
- **THEN** system shows the most recent feeding with time and type

#### Scenario: No feeding records
- **WHEN** there are no feeding records today
- **THEN** system shows placeholder text