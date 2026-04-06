## ADDED Requirements

### Requirement: Feeding standards data structure

The system SHALL provide structured feeding standards data based on authoritative guidelines.

#### Scenario: Load feeding standards
- **WHEN** system initializes or requests feeding standards
- **THEN** system loads standards data from JSON file containing age-based recommendations for milk volume, feeding frequency, and intervals

#### Scenario: Get standards by age
- **WHEN** analyzer requests standards for a baby of specific age
- **THEN** system returns min/max/avg values for milk_volume_ml, feeding_times, and interval_hours

### Requirement: Age-based standard lookup

The system SHALL support looking up feeding standards by baby age (days or months).

#### Scenario: Lookup by day number
- **WHEN** baby age is 30 days
- **THEN** system returns standards for day_30 or nearest available day

#### Scenario: Interpolate missing days
- **WHEN** baby age falls between available standard entries
- **THEN** system interpolates values from nearest available days

### Requirement: Standard data sources

The system SHALL reference authoritative feeding guidelines.

#### Scenario: Standard data includes source attribution
- **WHEN** standards data is loaded
- **THEN** data includes source field referencing "中国居民膳食指南2022" and other authoritative sources

### Requirement: Standard data format

The system SHALL use consistent format for all standard metrics.

#### Scenario: Metric format
- **WHEN** any standard metric is returned
- **THEN** metric contains min, max, avg fields as numeric values

#### Scenario: Volume unit
- **WHEN** milk_volume_ml standard is returned
- **THEN** value is in milliliters (ml)

#### Scenario: Interval unit
- **WHEN** interval_hours standard is returned
- **THEN** value is in hours