## Why

Currently, baby records (feeding, diaper, bath, etc.) can store images but there's no built-in way to view them within the app. Users need to navigate to the Documents folder manually to view attached images. This change adds in-app image viewing functionality for a seamless user experience.

## What Changes

- Add image viewer component to display record attachments
- Enable image viewing directly from the record detail screen
- Support common image formats (JPEG, PNG, HEIC) stored in Documents
- Add thumbnail preview in record list items
- Implement image zoom and pan gestures

## Capabilities

### New Capabilities
- `image-viewer`: Full-screen image viewer with zoom, pan, and dismiss gestures
- `record-gallery`: Grid view for multiple images attached to a single record
- `thumbnail-preview`: Thumbnail generation and display in record lists

### Modified Capabilities
- None

## Impact

- Frontend: New image viewer UI components
- Storage: Read access to Documents/babyjour/records/\*\*/images/
- Existing record detail screen will be modified to include image preview
- No breaking changes to data models or APIs
