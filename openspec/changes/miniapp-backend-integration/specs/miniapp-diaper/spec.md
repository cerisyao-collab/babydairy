## ADDED Requirements

### Requirement: User can record diaper change
The system SHALL allow users to record diaper changes with urine and/or stool selection.

#### Scenario: Open diaper modal
- **WHEN** user taps diaper button
- **THEN** system shows modal with urine and stool options
- **AND** both options are unselected by default

#### Scenario: Select urine only
- **WHEN** user taps urine option
- **THEN** urine option is highlighted
- **AND** stool option remains unselected

#### Scenario: Select stool only
- **WHEN** user taps stool option
- **THEN** stool option is highlighted
- **AND** urine option remains unselected

#### Scenario: Select both
- **WHEN** user taps both options
- **THEN** both options are highlighted

#### Scenario: Confirm without selection
- **WHEN** user taps confirm without selecting any option
- **THEN** system shows "请至少选择一个类型" error toast

#### Scenario: Confirm diaper record
- **WHEN** user selects option(s) and taps confirm
- **THEN** system creates record(s) with appropriate type(s)
- **AND** modal closes
- **AND** success toast shows selected type(s)

### Requirement: Diaper records are mapped to backend format
The system SHALL convert diaper record types to backend format correctly.

#### Scenario: Urine only conversion
- **WHEN** recording urine only
- **THEN** system sends type: "urine" with count: 1

#### Scenario: Stool only conversion
- **WHEN** recording stool only
- **THEN** system sends type: "bowel" with optional color field

#### Scenario: Both conversion
- **WHEN** recording both urine and stool
- **THEN** system creates two records: one "urine" and one "bowel"