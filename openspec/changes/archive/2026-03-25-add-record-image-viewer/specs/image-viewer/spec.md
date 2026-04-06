## ADDED Requirements

### Requirement: User can view a single image in full-screen
The system SHALL allow users to view a single image attachment from a baby record in full-screen mode within the Claude Code interface.

#### Scenario: View image by record ID and image index
- **WHEN** user requests to view an image from a specific record
- **THEN** system displays the image inline in the chat using markdown image syntax

#### Scenario: Image not found handling
- **WHEN** the requested image file does not exist at the stored path
- **THEN** system displays an error message indicating the image is missing

#### Scenario: Unsupported format handling
- **WHEN** the image file has an unsupported format
- **THEN** system displays a message indicating the format is not supported

### Requirement: User can list all images for a record
The system SHALL provide a command to list all images attached to a specific record with thumbnails.

#### Scenario: List images for a record
- **WHEN** user requests to see images for a specific record
- **THEN** system displays all attached images as thumbnails with their filenames

#### Scenario: Record has no images
- **WHEN** the requested record has no images attached
- **THEN** system displays a message indicating no images are attached

### Requirement: User can navigate between images in a record
The system SHALL allow users to navigate between multiple images in a record sequentially.

#### Scenario: Navigate to next image
- **WHEN** user requests to see the next image
- **THEN** system displays the next image in the record's image list

#### Scenario: Navigate to previous image
- **WHEN** user requests to see the previous image
- **THEN** system displays the previous image in the record's image list
