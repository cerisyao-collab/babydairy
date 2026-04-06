## 1. Project Setup

- [x] 1.1 Create `src/baby-diary/` directory structure
- [x] 1.2 Create `src/baby-diary/records/` data directory
- [x] 1.3 Create `src/baby-diary/records/images/` images directory

## 2. Data Model Implementation

- [x] 2.1 Define TypeScript interfaces for record types (FeedingDetails, BowelDetails, etc.)
- [x] 2.2 Define main Record interface with common fields (id, type, timestamp, date, details, images)
- [x] 2.3 Create type guard functions for record type validation

## 3. File Storage Implementation

- [x] 3.1 Implement directory creation on startup
- [x] 3.2 Implement monthly file path resolution (YYYY-MM.json)
- [x] 3.3 Implement JSON read/write utilities for records
- [x] 3.4 Implement image save function with record_id naming
- [x] 3.5 Implement data persistence with error handling

## 4. Query Implementation

- [x] 4.1 Implement date range parsing utilities
- [x] 4.2 Implement query by date function
- [x] 4.3 Implement query by date range function
- [x] 4.4 Implement query by type function
- [x] 4.5 Implement combined query (date range + type)

## 5. OpenClaw Skill Implementation

- [x] 5.1 Create Skill manifest with proper metadata
- [x] 5.2 Implement `record_create` skill endpoint
- [x] 5.3 Implement `record_query` skill endpoint
- [x] 5.4 Implement `record_list` skill endpoint
- [x] 5.5 Implement response formatter for human-readable output

## 6. Testing

- [x] 6.1 Test record creation for each type (feeding, bowel, bathing, sleep, growth)
- [x] 6.2 Test image attachment and storage
- [x] 6.3 Test query by single date
- [x] 6.4 Test query by date range
- [x] 6.5 Test query with type filter
- [x] 6.6 Test data persistence across restarts
- [x] 6.7 Test OpenClaw skill invocation

## 7. Documentation

- [x] 7.1 Create README with usage instructions
- [x] 7.2 Document record types and details fields
- [x] 7.3 Document OpenClaw skill endpoints
