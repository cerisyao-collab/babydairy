## ADDED Requirements

### Requirement: User can create illness records
The system SHALL allow users to create illness records to track baby's health conditions.

#### Scenario: Create illness record with symptoms
- **WHEN** user provides symptom description
- **THEN** system creates an illness record with the symptom field

#### Scenario: Create illness record with full details
- **WHEN** user provides symptom, cause, diagnosis, treatment, and severity
- **THEN** system creates a complete illness record with all provided fields

### Requirement: Illness record supports flexible fields
The system SHALL support the following fields for illness records:
- symptom (required): 症状描述
- cause (optional): 可能病因
- diagnosis (optional): 医生诊断
- treatment (optional): 治疗方案
- severity (optional): 严重程度 (轻/中/重)
- temperature (optional): 体温
- hospital_visit (optional): 是否就医
- notes (optional): 其他备注

#### Scenario: Create minimal illness record
- **WHEN** user provides only symptom field
- **THEN** system creates a valid illness record

#### Scenario: Create illness record with temperature
- **WHEN** user provides symptom and temperature
- **THEN** system records both fields accurately

#### Scenario: Create illness record with hospital visit flag
- **WHEN** user marks hospital_visit as true
- **THEN** system records that medical attention was sought

### Requirement: Illness records can be queried and listed
The system SHALL support querying illness records by date range and filtering by illness type.

#### Scenario: Query illness records by date
- **WHEN** user queries records with record_type="illness"
- **THEN** system returns only illness records

#### Scenario: List today's illness records
- **WHEN** user calls record_list for today
- **THEN** system includes any illness records created today

### Requirement: Illness records support image attachments
The system SHALL allow attaching images to illness records (e.g., rash photos, medical reports).

#### Scenario: Create illness record with photo
- **WHEN** user provides images array with record creation
- **THEN** system associates images with the illness record
