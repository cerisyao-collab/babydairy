## ADDED Requirements

### Requirement: System generates thumbnails for record list display
The system SHALL generate small thumbnails for images when displaying a list of records.

#### Scenario: Generate thumbnail for record with images
- **WHEN** listing records that have image attachments
- **THEN** system generates and displays a small thumbnail (max 100x100) for each image

#### Scenario: Thumbnail cache usage
- **WHEN** a thumbnail has been previously generated for an image
- **THEN** system uses the cached thumbnail instead of regenerating

### Requirement: Thumbnails are stored in a cache directory
The system SHALL store generated thumbnails in a dedicated cache directory under the images folder.

#### Scenario: Create thumbnail cache directory
- **WHEN** the thumbnail cache directory does not exist
- **THEN** system creates the directory automatically on first use

#### Scenario: Store thumbnail with consistent naming
- **WHEN** generating a thumbnail for an image
- **THEN** system stores it with the naming convention `<original_name>_thumb.<ext>`

### Requirement: Thumbnail generation handles errors gracefully
The system SHALL handle thumbnail generation failures without breaking the record list display.

#### Scenario: Image file missing
- **WHEN** the source image file is missing during thumbnail generation
- **THEN** system displays a placeholder icon and continues rendering other records

#### Scenario: Unsupported image format
- **WHEN** the image format cannot be processed for thumbnail generation
- **THEN** system displays the original image path as text and continues
