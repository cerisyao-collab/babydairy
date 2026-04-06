## ADDED Requirements

### Requirement: Agent core files define baby diary agent behavior
The system SHALL provide 8 core files that define the baby diary agent's identity, behavior, and operational guidelines.

#### Scenario: All 8 core files exist
- **WHEN** the agent starts in Clawd environment
- **THEN** it can read AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md, BOOTSTRAP.md, MEMORY.md

### Requirement: Core files are located in /Users/hanyuxiao/clawd/
The system SHALL store all core files in the `/Users/hanyuxiao/clawd/` directory.

#### Scenario: Files are discoverable
- **WHEN** the agent initializes
- **THEN** it finds all core files at the expected location

### Requirement: SOUL.md defines core behavior principles
The system SHALL define the agent's core personality and behavioral guidelines.

#### Scenario: Agent behaves genuinely helpful
- **WHEN** interacting with users
- **THEN** the agent provides direct help without performative language

### Requirement: TOOLS.md documents baby diary skill usage
The system SHALL document how to use the baby diary skill endpoints.

#### Scenario: Agent knows available tools
- **WHEN** user requests record-related operations
- **THEN** the agent can invoke the appropriate baby diary skill endpoint

### Requirement: MEMORY.md enables persistent context
The system SHALL provide a memory system for persisting user preferences and project context.

#### Scenario: Memory survives session restarts
- **WHEN** the agent restarts
- **THEN** it can recall previously learned user preferences
