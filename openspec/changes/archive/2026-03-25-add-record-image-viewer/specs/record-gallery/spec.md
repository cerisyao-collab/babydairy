## ADDED Requirements

### Requirement: User can view a grid of multiple images for a record
The system SHALL display multiple images attached to a record in a grid layout for easy browsing.

#### Scenario: Display image grid for record with multiple images
- **WHEN** a record has 2 or more images attached
- **THEN** system displays images in a grid format (2-3 columns) with thumbnails

#### Scenario: Display single image without grid
- **WHEN** a record has only 1 image attached
- **THEN** system displays the single image without grid layout

### Requirement: User can select an image from the gallery to view full-screen
The system SHALL allow users to click on a thumbnail in the gallery to view the full-resolution image.

#### Scenario: Select thumbnail to view full-size
- **WHEN** user indicates they want to view a specific thumbnail from the gallery
- **THEN** system displays the selected image at full resolution

### Requirement: Gallery shows image count and position
The system SHALL display the total count of images and the current position when viewing.

#### Scenario: Show image position indicator
- **WHEN** viewing images in a gallery
- **THEN** system shows "Image X of Y" indicator
