## ADDED Requirements

### Requirement: User can set baby's birth date
The system SHALL allow users to set and update baby's birth date for age calculation.

#### Scenario: Set birth date
- **WHEN** user selects birth date in settings
- **THEN** system sends PUT /api/config/baby with birth_date
- **AND** baby age is calculated for AI analysis

#### Scenario: View current age
- **WHEN** birth date is set
- **THEN** system displays baby's age in days on home page

### Requirement: User can set baby's gender
The system SHALL allow users to set baby's gender.

#### Scenario: Set gender
- **WHEN** user selects gender (male/female/unknown)
- **THEN** system sends PUT /api/config/baby with gender
- **AND** selection is persisted

### Requirement: User can set feeding type
The system SHALL allow users to set primary feeding type.

#### Scenario: Set feeding type
- **WHEN** user selects feeding type (breast/formula/mixed)
- **THEN** system sends PUT /api/config/baby with feeding_type
- **AND** AI analysis uses this for recommendations

### Requirement: User can set birth weight
The system SHALL allow users to set baby's birth weight.

#### Scenario: Set birth weight
- **WHEN** user enters birth weight in kg
- **THEN** system sends PUT /api/config/baby with birth_weight
- **AND** weight is stored for growth tracking

### Requirement: Baby config is loaded on app start
The system SHALL load baby configuration when app initializes.

#### Scenario: Load config
- **WHEN** app starts with valid token
- **THEN** system fetches GET /api/config/baby
- **AND** config is cached for subsequent use