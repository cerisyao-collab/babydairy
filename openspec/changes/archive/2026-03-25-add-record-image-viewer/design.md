## Context

This project is a Claude Code skill for recording baby activities (feeding, diaper, bath, sleep, etc.). Records are stored as JSON files in `src/baby-diary/records/` with an `images/` subdirectory for attachments. Currently, images can be stored but there's no way to view them within the Claude Code interface.

The skill uses a conversational interface where users interact via natural language commands in Claude Code.

## Goals / Non-Goals

**Goals:**
- Enable users to view images attached to baby records directly in Claude Code
- Support viewing images from the Documents folder where records are stored by default
- Provide thumbnail previews when listing records
- Implement full-screen image viewer with basic zoom/pan

**Non-Goals:**
- Image editing or manipulation
- Support for external image URLs (only local files)
- Changing the existing record data model
- Web or mobile app UI (this is Claude Code only)

## Decisions

### 1. Image Storage Location
**Decision:** Images stored in `Documents/babyjour/records/<date>/<image_id>.<ext>`

**Rationale:**
- Documents folder is user-accessible and backup-friendly
- Aligns with existing file storage pattern in the codebase
- Date-based organization makes it easy to associate images with records

### 2. Image Viewer Implementation
**Decision:** Use Claude's native image rendering via markdown `![alt](path)` syntax

**Rationale:**
- Claude Code can display images natively in the chat interface
- No need for external dependencies or complex UI code
- Simplest implementation that provides immediate value

### 3. Thumbnail Generation
**Decision:** Generate thumbnails on-demand using PIL/Pillow when listing records

**Rationale:**
- Saves storage vs pre-generated thumbnails
- Python has mature image libraries (Pillow)
- Thumbnails only generated when user lists records with images

### 4. Image Format Support
**Decision:** Support JPEG, PNG, HEIC (convert to displayable format)

**Rationale:**
- JPEG/PNG are universally supported
- HEIC is common on iOS devices (where baby photos may come from)
- HEIC requires conversion using `pillow-heif` library

## Risks / Trade-offs

**Risk:** HEIC conversion adds dependency complexity
→ **Mitigation:** Make HEIC support optional; gracefully degrade if library unavailable

**Risk:** Large images may slow down record listing
→ **Mitigation:** Cache thumbnails; limit max thumbnail size

**Risk:** File path handling across platforms
→ **Mitigation:** Use `pathlib` for cross-platform path handling; test on macOS (primary target)

**Trade-off:** On-demand thumbnail generation vs storage
→ Chose on-demand to avoid stale thumbnails and save space; acceptable performance trade-off

## Migration Plan

1. Add Pillow dependency to skill requirements
2. Implement image viewer command (`/view-image <record-date> <image-id>`)
3. Modify record display to show `[📷 N images]` indicator
4. Add `/list-images <record-date>` command to show thumbnails
5. Test with existing records that have image attachments

**Rollback:** Disable image features via feature flag; no data model changes to revert

## Open Questions

1. Should images be embedded inline in record display or shown on demand?
2. What's the maximum number of images per record to display thumbnails?
