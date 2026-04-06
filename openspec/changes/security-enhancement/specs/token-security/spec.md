## ADDED Requirements

### Requirement: Mini-program SHALL encrypt stored tokens
JWT tokens SHALL be encrypted before storing in wx.storage.

#### Scenario: Encrypt token on login
- **WHEN** user successfully logs in
- **THEN** system generates random AES key
- **AND** encrypts JWT token with AES key
- **AND** stores encrypted token in wx.storage

#### Scenario: Decrypt token for request
- **WHEN** mini-program makes API request
- **THEN** system retrieves AES key from wx.storage
- **AND** decrypts JWT token
- **AND** includes token in Authorization header

### Requirement: Token SHALL be bound to device
Tokens SHALL be associated with specific device to prevent token theft.

#### Scenario: Bind token to device
- **WHEN** user logs in on new device
- **THEN** system generates device fingerprint (openid hash + device info)
- **AND** associates token with device fingerprint
- **AND** stores device fingerprint locally

#### Scenario: Detect token device mismatch
- **WHEN** decrypted token is used from different device
- **THEN** backend detects device mismatch
- **AND** rejects request with 401 error
- **AND** prompts user to re-login

### Requirement: System SHALL use short-lived access tokens with refresh tokens
Access tokens SHALL have short expiration (15 minutes) with refresh tokens for renewal.

#### Scenario: Access token expires
- **WHEN** access token is older than 15 minutes
- **THEN** backend rejects request with 401
- **AND** returns token_expired error code

#### Scenario: Refresh access token
- **WHEN** mini-program receives token_expired error
- **THEN** system sends refresh token to /api/auth/refresh
- **AND** backend issues new access token
- **AND** mini-program stores new encrypted token

#### Scenario: Refresh token expires
- **WHEN** refresh token is older than 7 days
- **THEN** backend rejects refresh request
- **AND** user must re-login with wx.login()