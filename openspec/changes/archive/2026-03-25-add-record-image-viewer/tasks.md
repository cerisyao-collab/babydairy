## 1. Setup and Dependencies

- [x] 1.1 Add Pillow dependency to skill requirements for image processing
- [x] 1.2 Add pillow-heif dependency for HEIC image support (optional)
- [x] 1.3 Create thumbnail cache directory structure under images/

## 2. Image Viewer Core Implementation

- [x] 2.1 Implement `image_view` function to display a single image by record ID
- [x] 2.2 Implement `list_images` function to list all images for a record
- [x] 2.3 Add image validation (file exists, supported format)
- [x] 2.4 Implement error handling for missing or corrupt images

## 3. Gallery View Implementation

- [x] 3.1 Implement `image_gallery` function to display multiple images in grid
- [x] 3.2 Add image navigation (next/previous) within a record
- [x] 3.3 Display image count and position indicator

## 4. Thumbnail Generation

- [x] 4.1 Implement `generate_thumbnail` function with max 100x100 size
- [x] 4.2 Add thumbnail caching logic (check cache before regenerating)
- [x] 4.3 Implement graceful error handling for unsupported formats
- [x] 4.4 Integrate thumbnails into record list display

## 5. User Interface Integration

- [x] 5.1 Add `/view-image <record-id> [image-index]` command
- [x] 5.2 Add `/list-images <record-id>` command
- [x] 5.3 Modify record display to show `[📷 N images]` indicator
- [x] 5.4 Update record list to show thumbnails for records with images

## 6. Testing and Documentation

- [x] 6.1 Test with sample images (JPEG, PNG, HEIC)
- [x] 6.2 Test edge cases (missing files, corrupt images, no images)
- [x] 6.3 Update README with new image viewing commands
- [x] 6.4 Add inline code documentation for new functions
