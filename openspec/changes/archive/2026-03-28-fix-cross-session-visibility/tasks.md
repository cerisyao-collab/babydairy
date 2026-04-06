## 1. Cache Invalidation Implementation

- [x] 1.1 Add index_mtime global variable to track last load time
- [x] 1.2 Implement load_index() with mtime check
- [x] 1.3 Add refresh_index() function for manual cache invalidation

## 2. Index Auto-Refresh

- [x] 2.1 Update record_query to call load_index() (auto-refresh)
- [x] 2.2 Update record_list to call load_index() (auto-refresh)
- [x] 2.3 Ensure record_create updates index after write

## 3. Testing

- [x] 3.1 Test cross-session visibility with two Python processes
- [x] 3.2 Verify index refresh on data change
- [x] 3.3 Test refresh_index() function
