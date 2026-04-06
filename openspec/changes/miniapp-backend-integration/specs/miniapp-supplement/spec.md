## ADDED Requirements

### Requirement: User can record supplements
The system SHALL allow users to record nutritional supplements with custom names.

#### Scenario: Open supplement modal
- **WHEN** user taps supplement button
- **THEN** system shows modal with input field and list

#### Scenario: Add supplement name
- **WHEN** user types name and taps add button
- **THEN** name is added to the list with checkmark selected
- **AND** input field is cleared

#### Scenario: Add duplicate name
- **WHEN** user tries to add a name that already exists
- **THEN** system shows "该营养品已添加" error toast

#### Scenario: Toggle supplement selection
- **WHEN** user taps an item in the list
- **THEN** item selection is toggled

#### Scenario: Confirm supplement record
- **WHEN** user has selected items and taps confirm
- **THEN** system creates medication record with all selected names
- **AND** modal closes

#### Scenario: Confirm without selection
- **WHEN** user taps confirm without any selected items
- **THEN** system shows "请至少选择一个营养品" error toast

### Requirement: Supplement record is mapped to backend format
The system SHALL convert supplement records to medication format.

#### Scenario: Supplement conversion
- **WHEN** recording supplements
- **THEN** system sends type: "medication"
- **AND** details.name contains supplement names
- **AND** details.dosage is optional