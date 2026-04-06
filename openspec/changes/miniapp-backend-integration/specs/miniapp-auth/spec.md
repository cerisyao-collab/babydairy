## ADDED Requirements

### Requirement: User can login via WeChat
The system SHALL provide WeChat login functionality using wx.login API.

#### Scenario: Successful login
- **WHEN** user opens the app for the first time
- **THEN** system calls wx.login to get code
- **AND** system sends code to backend POST /api/auth/login
- **AND** system receives JWT token and stores it
- **AND** system displays the main page

#### Scenario: Token expired
- **WHEN** user makes an API request with expired token
- **THEN** backend returns 401 error
- **AND** system automatically triggers re-login
- **AND** user session is restored without manual intervention

### Requirement: Token is stored securely
The system SHALL store JWT token in WeChat storage for persistent sessions.

#### Scenario: Token persistence
- **WHEN** user closes and reopens the app
- **THEN** system retrieves token from wx.getStorageSync
- **AND** user remains logged in

#### Scenario: Token removal on logout
- **WHEN** user explicitly logs out
- **THEN** system removes token from storage
- **AND** user is redirected to login page

### Requirement: Login state is accessible globally
The system SHALL provide global access to login state and user info.

#### Scenario: Check login status
- **WHEN** any page needs to check if user is logged in
- **THEN** system provides isLoggedIn helper function
- **AND** function returns true if valid token exists

#### Scenario: Get user info
- **WHEN** page needs user information
- **THEN** system provides getUserInfo helper function
- **AND** function returns user object or null