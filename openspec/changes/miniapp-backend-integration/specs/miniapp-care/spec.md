## ADDED Requirements

### Requirement: User can record bathing
The system SHALL allow users to record bathing sessions.

#### Scenario: Record bathing
- **WHEN** user taps bathing button
- **THEN** system creates bathing record with current timestamp
- **AND** success toast is shown

### Requirement: User can record nail cutting
The system SHALL allow users to record nail cutting.

#### Scenario: Record nail cutting
- **WHEN** user taps nail cutting button
- **THEN** system creates bathing record with note "剪指甲"
- **AND** success toast is shown

### Requirement: Care records are mapped to backend format
The system SHALL convert care record types to backend format correctly.

#### Scenario: Bathing conversion
- **WHEN** recording bathing
- **THEN** system sends type: "bathing"

#### Scenario: Nail cutting conversion
- **WHEN** recording nail cutting
- **THEN** system sends type: "bathing" with details.notes: "剪指甲"