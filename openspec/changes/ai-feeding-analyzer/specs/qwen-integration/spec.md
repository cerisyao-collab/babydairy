## ADDED Requirements

### Requirement: Qwen API integration

The system SHALL integrate with Alibaba Cloud Qwen (通义千问) API.

#### Scenario: Initialize Qwen client
- **WHEN** LLMService is instantiated
- **THEN** system initializes dashscope client with API key from environment

#### Scenario: Generate text
- **WHEN** generate_analysis_text is called with analysis result
- **THEN** system calls Qwen API and returns generated text

### Requirement: Prompt management

The system SHALL manage prompts for consistent output.

#### Scenario: System prompt for feeding analysis
- **WHEN** generating feeding analysis text
- **THEN** system uses predefined system prompt instructing: use gentle tone, avoid medical diagnosis, provide actionable suggestions

#### Scenario: User prompt construction
- **WHEN** generating response
- **THEN** system constructs user prompt with baby info, feeding data, and standard values

### Requirement: Response validation

The system SHALL validate LLM output format.

#### Scenario: Validate response content
- **WHEN** LLM returns response
- **THEN** system validates response is non-empty and contains expected content type

#### Scenario: Handle malformed response
- **WHEN** LLM returns empty or invalid response
- **THEN** system falls back to rule-based default response

### Requirement: Error handling and retry

The system SHALL handle API errors gracefully.

#### Scenario: API timeout
- **WHEN** Qwen API times out
- **THEN** system retries up to 3 times with exponential backoff

#### Scenario: API rate limit
- **WHEN** rate limit is hit
- **THEN** system returns cached response or graceful error message

#### Scenario: API key invalid
- **WHEN** API key is invalid or expired
- **THEN** system logs error and returns fallback response

### Requirement: Cost optimization

The system SHALL optimize LLM API costs.

#### Scenario: Cache identical requests
- **WHEN** same analysis is requested within 1 hour
- **THEN** system returns cached response without API call

#### Scenario: Use appropriate model
- **WHEN** generating feeding analysis
- **THEN** system uses qwen-turbo for cost efficiency (not qwen-max)

### Requirement: Environment configuration

The system SHALL support Qwen configuration via environment.

#### Scenario: API key configuration
- **WHEN** DASHSCOPE_API_KEY environment variable is set
- **THEN** system uses this key for Qwen API authentication

#### Scenario: Model selection
- **WHEN** QWEN_MODEL environment variable is set
- **THEN** system uses specified model (default: qwen-turbo)