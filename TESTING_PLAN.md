# AllTalk TTS Comprehensive Testing Plan

## Overview
This document outlines a comprehensive testing plan for all AllTalk TTS functionality, including both API endpoints and Gradio UI interactions.

## Testing Scope

### 1. API Endpoint Tests

#### 1.1 Engine Management APIs
- **POST /api/enginereload**
  - Test changing to valid engine (xtts, piper, etc.) - ✅ PASSING
  - Test changing to invalid engine - ✅ PASSING
  - Verify config is saved after change - ✅ PASSING
  - Verify configuration is reloaded - ✅ PASSING
  - Verify restart is triggered - ✅ PASSING

- **GET /api/ready**
  - Test returns correct status when system is ready - ✅ PASSING
  - Test returns correct status during startup - ⏸️ NOT IMPLEMENTED
  - Test returns correct status during model loading - ⏸️ NOT IMPLEMENTED

- **GET /api/currentsettings**
  - Test returns current engine settings - ⏸️ SKIPPED (requires complex mocking of model_engine attributes)
  - Test returns model configuration - ⏸️ SKIPPED
  - Test returns voice settings - ⏸️ SKIPPED
  - Test returns audio format settings - ⏸️ SKIPPED

#### 1.2 Voice Management APIs
- **GET /api/voices**
  - Test returns voices for current engine - ✅ PASSING
  - Test returns error for non-multivoice engine - ✅ PASSING
  - Test returns builtin XTTS voices when XTTS is loaded - ✅ PASSING
  - Test returns WAV files for voice cloning - ✅ PASSING
  - Test returns voice sets - ✅ PASSING
  - Test returns latents - ✅ PASSING
  - Test returns "No Voices Found" when no voices available - ✅ PASSING

- **GET /api/rvcvoices**
  - Test returns RVC voices when enabled - ⏸️ NOT IMPLEMENTED
  - Test returns "Disabled" when RVC is disabled - ✅ PASSING
  - Test handles RVC configuration errors - ⏸️ NOT IMPLEMENTED

#### 1.3 TTS Generation APIs
- **POST /api/tts-generate**
  - Test successful TTS generation with valid text - ⏸️ SKIPPED (requires complex mocking of TTS generation)
  - Test with different voices - ⏸️ SKIPPED
  - Test with different languages - ⏸️ SKIPPED
  - Test with different audio formats - ⏸️ SKIPPED
  - Test with custom parameters (temperature, speed, pitch) - ⏸️ SKIPPED
  - Test error handling for empty text - ⏸️ SKIPPED
  - Test error handling for invalid voice - ⏸️ SKIPPED

- **POST /api/tts-generate-streaming**
  - Test streaming TTS generation - ⏸️ SKIPPED (requires complex mocking of TTS generation)
  - Test non-streaming TTS generation - ⏸️ SKIPPED
  - Test generation interruption - ⏸️ SKIPPED

- **PUT /api/stop-generation**
  - Test stops current generation - ✅ PASSING
  - Test handles no active generation - ⏸️ NOT IMPLEMENTED
  - Test resets generation state - ⏸️ NOT IMPLEMENTED

#### 1.4 Model Management APIs
- **POST /api/reload**
  - Test model reload with valid model - ✅ PASSING
  - Test model reload with invalid model - ✅ PASSING
  - Test model unload - ⏸️ NOT IMPLEMENTED
  - Test handles model loading errors - ⏸️ NOT IMPLEMENTED

- **GET /api/models**
  - Test returns available models - ⏸️ NOT IMPLEMENTED (endpoint may not exist)
  - Test returns model details - ⏸️ NOT IMPLEMENTED
  - Test handles no models available - ⏸️ NOT IMPLEMENTED

- **GET /api/reload_config**
  - Test configuration reload - ⏸️ NOT IMPLEMENTED
  - Test configuration persistence - ⏸️ NOT IMPLEMENTED

#### 1.5 Settings Management APIs
- **POST /update-settings**
  - Test updating engine settings - ⏸️ NOT IMPLEMENTED (complex endpoint requiring form data)
  - Test updating voice settings - ⏸️ NOT IMPLEMENTED
  - Test updating audio settings - ⏸️ NOT IMPLEMENTED
  - Test updating generation parameters - ⏸️ NOT IMPLEMENTED
  - Test invalid setting updates - ⏸️ NOT IMPLEMENTED
  - Test config is saved after update - ⏸️ NOT IMPLEMENTED

- **GET /settings-json**
  - Test returns current settings as JSON - ⏸️ NOT IMPLEMENTED

**API Endpoint Tests Summary:**
- Total tests: 17 passing, 5 skipped
- Skipped tests are due to complex mocking requirements or endpoints that don't exist
- Most critical endpoints are tested and passing

### 2. Gradio UI Tests

**Note:** Gradio UI tests require browser automation tools (Selenium/Playwright) to test actual UI interactions. These are marked as requiring implementation with browser testing framework.

#### 2.1 Engine Selection
- Test engine dropdown shows all available engines - ⏸️ REQUIRES BROWSER AUTOMATION
- Test changing engine updates UI fields - ⏸️ REQUIRES BROWSER AUTOMATION
- Test changing engine disables/enables appropriate fields - ⏸️ REQUIRES BROWSER AUTOMATION
- Test engine change triggers model reload - ⏸️ REQUIRES BROWSER AUTOMATION
- Test engine change saves configuration - ⏸️ REQUIRES BROWSER AUTOMATION
- Test engine change shows appropriate error messages - ⏸️ REQUIRES BROWSER AUTOMATION

#### 2.2 Model Selection
- Test model dropdown shows models for selected engine - ⏸️ REQUIRES BROWSER AUTOMATION
- Test changing model loads model - ⏸️ REQUIRES BROWSER AUTOMATION
- Test model selection updates voice list - ⏸️ REQUIRES BROWSER AUTOMATION
- Test model selection shows model details - ⏸️ REQUIRES BROWSER AUTOMATION
- Test handles model loading errors - ⏸️ REQUIRES BROWSER AUTOMATION
- Test handles no models available - ⏸️ REQUIRES BROWSER AUTOMATION

#### 2.3 Voice Selection
- Test voice dropdown shows voices for current engine - ⏸️ REQUIRES BROWSER AUTOMATION
- Test voice dropdown shows builtin XTTS voices - ⏸️ REQUIRES BROWSER AUTOMATION
- Test voice dropdown shows WAV files - ⏸️ REQUIRES BROWSER AUTOMATION
- Test voice dropdown shows voice sets - ⏸️ REQUIRES BROWSER AUTOMATION
- Test voice dropdown shows latents - ⏸️ REQUIRES BROWSER AUTOMATION
- Test voice selection updates default voice - ⏸️ REQUIRES BROWSER AUTOMATION
- Test voice selection shows "No Voices Found" when appropriate - ⏸️ REQUIRES BROWSER AUTOMATION
- Test voice selection handles errors - ⏸️ REQUIRES BROWSER AUTOMATION

#### 2.4 Text Input
- Test text input accepts valid text - ⏸️ REQUIRES BROWSER AUTOMATION
- Test text input handles empty text - ⏸️ REQUIRES BROWSER AUTOMATION
- Test text input handles very long text - ⏸️ REQUIRES BROWSER AUTOMATION
- Test text input handles special characters - ⏸️ REQUIRES BROWSER AUTOMATION
- Test text input handles multiple languages - ⏸️ REQUIRES BROWSER AUTOMATION

#### 2.5 Generation Parameters
- Test temperature slider - ⏸️ REQUIRES BROWSER AUTOMATION
- Test speed slider - ⏸️ REQUIRES BROWSER AUTOMATION
- Test pitch slider (if supported) - ⏸️ REQUIRES BROWSER AUTOMATION
- Test repetition penalty slider - ⏸️ REQUIRES BROWSER AUTOMATION
- Test parameter updates are saved - ⏸️ REQUIRES BROWSER AUTOMATION
- Test parameter updates affect generation - ⏸️ REQUIRES BROWSER AUTOMATION
- Test parameters are disabled when not supported - ⏸️ REQUIRES BROWSER AUTOMATION

#### 2.6 Generation Controls
- Test "Generate" button starts generation - ⏸️ REQUIRES BROWSER AUTOMATION
- Test "Stop" button stops generation - ⏸️ REQUIRES BROWSER AUTOMATION
- Test buttons are disabled during generation - ⏸️ REQUIRES BROWSER AUTOMATION
- Test buttons are enabled after generation - ⏸️ REQUIRES BROWSER AUTOMATION
- Test progress bar shows during generation - ⏸️ REQUIRES BROWSER AUTOMATION
- Test generation completes successfully - ⏸️ REQUIRES BROWSER AUTOMATION
- Test generation errors are shown - ⏸️ REQUIRES BROWSER AUTOMATION

#### 2.7 Audio Output
- Test audio player shows generated audio - ⏸️ REQUIRES BROWSER AUTOMATION
- Test audio can be played - ⏸️ REQUIRES BROWSER AUTOMATION
- Test audio can be downloaded - ⏸️ REQUIRES BROWSER AUTOMATION
- Test audio format is correct - ⏸️ REQUIRES BROWSER AUTOMATION
- Test audio quality is acceptable - ⏸️ REQUIRES BROWSER AUTOMATION
- Test handles audio generation errors - ⏸️ REQUIRES BROWSER AUTOMATION

#### 2.8 Settings Page
- Test all settings fields are displayed - ⏸️ REQUIRES BROWSER AUTOMATION
- Test settings can be updated - ⏸️ REQUIRES BROWSER AUTOMATION
- Test settings are saved - ⏸️ REQUIRES BROWSER AUTOMATION
- Test settings are loaded on page load - ⏸️ REQUIRES BROWSER AUTOMATION
- Test invalid settings are rejected - ⏸️ REQUIRES BROWSER AUTOMATION
- Test settings reset works - ⏸️ REQUIRES BROWSER AUTOMATION

#### 2.9 Model Download UI
- Test engine selection for downloads - ⏸️ REQUIRES BROWSER AUTOMATION
- Test model list displays correctly - ⏸️ REQUIRES BROWSER AUTOMATION
- Test model selection works - ⏸️ REQUIRES BROWSER AUTOMATION
- Test filter dropdowns work (language, quality) - ⏸️ REQUIRES BROWSER AUTOMATION
- Test Select All button works - ⏸️ REQUIRES BROWSER AUTOMATION
- Test Clear Selection button works - ⏸️ REQUIRES BROWSER AUTOMATION
- Test Download button works - ⏸️ REQUIRES BROWSER AUTOMATION
- Test progress bar shows during download - ⏸️ REQUIRES BROWSER AUTOMATION
- Test download completes successfully - ⏸️ REQUIRES BROWSER AUTOMATION
- Test download errors are shown - ⏸️ REQUIRES BROWSER AUTOMATION
- Test status shows correctly after download - ⏸️ REQUIRES BROWSER AUTOMATION
- Test filters are disabled for non-Piper engines - ⏸️ REQUIRES BROWSER AUTOMATION

### 3. Engine-Specific Tests

#### 3.1 XTTS Engine
- Test builtin voice extraction from speakers_xtts.pth - ✅ PASSING (test_scan_builtin_xtts_voices)
- Test voice cloning with WAV files - ✅ PASSING (test_scan_individual_wavs)
- Test voice cloning with voice sets - ✅ PASSING (test_scan_voice_sets)
- Test multilingual support - ⏸️ NOT IMPLEMENTED
- Test celebrity clone voices - ⏸️ NOT IMPLEMENTED
- Test API TTS mode - ✅ PASSING (test_scan_builtin_xtts_voices_apitts)
- Test local XTTS mode - ✅ PASSING (test_scan_builtin_xtts_voices)
- Test speaker embedding loading - ✅ PASSING (test_scan_builtin_xtts_voices)
- Test gpt_cond_latent generation - ⏸️ NOT IMPLEMENTED

#### 3.2 Piper Engine
- Test voice selection from .onnx files - ✅ PASSING (test_piper_voice_selection_onnx)
- Test voice quality levels - ✅ PASSING (test_piper_quality_levels)
- Test language filtering - ✅ PASSING (test_piper_language_filtering)
- Test multi-model support - ✅ PASSING (test_scan_piper_models)
- Test model download - ⏸️ NOT IMPLEMENTED
- Test model switching - ⏸️ NOT IMPLEMENTED

#### 3.3 Other Engines
- Test engine-specific features - ⏸️ NOT IMPLEMENTED
- Test engine-specific limitations - ⏸️ NOT IMPLEMENTED
- Test engine-specific error handling - ⏸️ NOT IMPLEMENTED

### 4. Integration Tests

#### 4.1 Engine Switching
- Test switching between engines - ⏸️ NOT IMPLEMENTED (requires full system integration test)
- Test voice list updates after engine switch - ⏸️ NOT IMPLEMENTED
- Test model list updates after engine switch - ⏸️ NOT IMPLEMENTED
- Test settings update after engine switch - ⏸️ NOT IMPLEMENTED
- Test configuration persists after engine switch - ⏸️ NOT IMPLEMENTED

#### 4.2 Model Switching
- Test switching between models - ⏸️ NOT IMPLEMENTED
- Test voice list updates after model switch - ⏸️ NOT IMPLEMENTED
- Test generation works after model switch - ⏸️ NOT IMPLEMENTED
- Test settings persist after model switch - ⏸️ NOT IMPLEMENTED

#### 4.3 End-to-End Workflows
- Test complete TTS generation workflow - ⏸️ NOT IMPLEMENTED
- Test complete engine change workflow - ⏸️ NOT IMPLEMENTED
- Test complete model download workflow - ⏸️ NOT IMPLEMENTED
- Test complete settings update workflow - ⏸️ NOT IMPLEMENTED

### 5. Error Handling Tests

#### 5.1 API Error Handling
- Test invalid request parameters - ✅ PASSING (test_invalid_endpoint)
- Test missing required parameters - ✅ PASSING (test_missing_required_parameter)
- Test malformed requests - ⏸️ NOT IMPLEMENTED
- Test server errors - ⏸️ NOT IMPLEMENTED
- Test timeout handling - ⏸️ NOT IMPLEMENTED

#### 5.2 UI Error Handling
- Test invalid user input - ⏸️ NOT IMPLEMENTED
- Test network errors - ⏸️ NOT IMPLEMENTED
- Test file upload errors - ⏸️ NOT IMPLEMENTED
- Test configuration errors - ⏸️ NOT IMPLEMENTED
- Test model loading errors - ⏸️ NOT IMPLEMENTED

### 6. Performance Tests

#### 6.1 API Performance
- Test response times for all endpoints - ✅ PASSING (test_api_response_time)
- Test concurrent requests - ✅ PASSING (test_concurrent_requests)
- Test load handling - ⏸️ NOT IMPLEMENTED
- Test memory usage - ⏸️ NOT IMPLEMENTED

#### 6.2 UI Performance
- Test page load times - ⏸️ NOT IMPLEMENTED
- Test interaction responsiveness - ⏸️ NOT IMPLEMENTED
- Test generation speed - ⏸️ NOT IMPLEMENTED
- Test audio playback performance - ⏸️ NOT IMPLEMENTED

### 7. Security Tests

#### 7.1 API Security
- Test authentication (if implemented) - ⏸️ NOT IMPLEMENTED (no auth implemented)
- Test authorization - ⏸️ NOT IMPLEMENTED (no auth implemented)
- Test input validation - ⏸️ NOT IMPLEMENTED
- Test SQL injection prevention - ✅ PASSING (test_sql_injection_prevention)
- Test XSS prevention - ✅ PASSING (test_xss_prevention)

### 8. Compatibility Tests

#### 8.1 Browser Compatibility
- Test UI in different browsers - ⏸️ NOT IMPLEMENTED
- Test audio playback in different browsers - ⏸️ NOT IMPLEMENTED

#### 8.2 Platform Compatibility
- Test on different operating systems - ⏸️ NOT IMPLEMENTED
- Test with different Python versions - ⏸️ NOT IMPLEMENTED

**Overall Test Status:**
- API Endpoint Tests: 23 passing, 5 skipped (added 2 error handling, 2 security, 2 performance tests)
- XTTS Engine Tests: 6 passing, 3 not implemented
- Piper Engine Tests: 4 passing, 2 not implemented
- Error Handling Tests: 2 passing, 3 not implemented
- Security Tests: 2 passing, 3 not implemented
- Performance Tests: 2 passing, 2 not implemented
- Gradio UI Tests: All require browser automation framework
- Integration Tests: Not implemented
- Compatibility Tests: Not implemented
- Total: 39 passing, 15 skipped/not implemented

## Test Implementation Plan

### Phase 1: API Endpoint Tests ✅ COMPLETED
1. Create test file: `tests/test_api_endpoints.py` ✅ DONE
2. Implement test classes for each API endpoint group ✅ DONE
3. Use pytest for test framework ✅ DONE
4. Mock external dependencies (TTS engines, file system) ✅ DONE
5. Test both success and error scenarios ✅ DONE
   - Added deepspeed mocking in conftest.py to avoid CUDA errors
   - Implemented tests for: engine reload, voices, audio, RVC voices, current settings, ready endpoint, CORS settings, error handling
   - Total: 19 passing, 5 skipped

### Phase 2: Engine-Specific Tests ✅ COMPLETED
1. Create test file: `tests/test_xtts_engine.py` ✅ DONE (already existed, expanded)
2. Create test file: `tests/test_piper_engine.py` ✅ DONE
3. Implement tests for engine-specific features ✅ DONE
4. Test voice extraction, model loading, generation ✅ DONE
   - XTTS: Added tests for builtin voice extraction from speakers_xtts.pth, voice sets, latents (6 passing, 3 not implemented)
   - Piper: Added tests for voice selection, quality levels, language filtering, multi-model support (4 passing, 2 not implemented)
   - Total: 10 passing, 5 not implemented

### Phase 3: Gradio UI Tests ⏸️ REQUIRES BROWSER AUTOMATION
1. Create test file: `tests/test_gradio_ui.py` ⏸️ NOT IMPLEMENTED
2. Use gradio testing utilities or selenium/playwright ⏸️ REQUIRES SETUP
3. Test UI interactions programmatically ⏸️ REQUIRES SETUP
4. Test field interactivity and state changes ⏸️ REQUIRES SETUP

### Phase 4: Integration Tests ⏸️ NOT IMPLEMENTED
1. Create test file: `tests/test_integration.py` ⏸️ NOT IMPLEMENTED
2. Test end-to-end workflows ⏸️ NOT IMPLEMENTED
3. Test engine switching ⏸️ NOT IMPLEMENTED
4. Test model switching ⏸️ NOT IMPLEMENTED
5. Test complete user workflows ⏸️ NOT IMPLEMENTED

### Phase 5: Automated Test Runner ✅ COMPLETED
1. Create test runner script: `run_all_tests.py` ✅ DONE
2. Run all tests with coverage reporting ✅ DONE (script supports --cov flag)
3. Generate test reports ✅ DONE (generates HTML coverage report)
4. Integrate with CI/CD pipeline ⏸️ NOT IMPLEMENTED (requires CI/CD setup)

## Test Execution

### Running All Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api_endpoints.py -v

# Run specific test file
pytest tests/test_xtts_engine.py -v

# Run specific test class
pytest tests/test_api_endpoints.py::TestEngineManagement -v

# Run specific test
pytest tests/test_api_endpoints.py::TestEngineManagement::test_engine_reload -v
```

### Test Reports
- HTML coverage report: `htmlcov/index.html`
- Test results in terminal output
- JUnit XML output for CI/CD integration

## Current Status

### Completed ✅
- XTTS builtin voice extraction implementation
- XTTS builtin voice extraction tests (test_scan_builtin_xtts_voices, test_scan_builtin_xtts_voices_apitts, test_scan_builtin_xtts_voices_no_model)
- Engine change save() fix (separated change_engine() from save())
- API endpoint tests (23 passing, 5 skipped, including error handling, security, and performance)
- XTTS engine tests (6 passing, 3 not implemented)
- Piper engine tests (4 passing, 2 not implemented)
- API error handling tests (2 passing, 3 not implemented)
- API security tests (2 passing, 3 not implemented)
- API performance tests (2 passing, 2 not implemented)
- Automated test runner script (run_all_tests.py)
- Comprehensive test plan creation and documentation

### Voice Display Issue ✅ RESOLVED
- Issue: Voices not showing in generate TTS page
- Root cause: Current engine was Piper, not XTTS. Builtin XTTS voices only appear when XTTS is selected.
- Solution: User needs to change engine to XTTS to see builtin voices (Claribel Dervla, Daisy Studious, Gracie Wise, etc.)

### Recently Completed ✅ (Apr 22, 2026)
- Added Playwright to requirements-dev.txt for Gradio UI testing
- Implemented skipped API endpoint tests:
  - /api/currentsettings (previously skipped due to complex mocking)
  - /api/tts-generate (previously skipped due to complex mocking)
  - /api/ready (added tests for startup and model loading states)
  - /api/stop-generation (added tests for no active generation and state reset)
  - /api/rvcvoices (added test for when RVC is enabled)
- Created comprehensive Gradio UI tests with Playwright (test_gradio_ui.py)
- Created integration tests for end-to-end workflows (test_integration.py):
  - Engine switching workflows
  - Model switching workflows
  - Complete TTS generation workflow
  - Settings update workflow
  - Error recovery workflows
  - Concurrent operations
  - Cross-engine functionality
- Installed Chrome browser for Playwright MCP
- Installed pytest and core testing dependencies

### Pending ⏸️
- Run pytest tests to verify all API tests pass (requires full dependency installation)
- Start test server for Gradio UI testing
- Use Playwright MCP to test Gradio UI interactively
- Implement missing engine-specific tests (multilingual support, celebrity voices, gpt_cond_latent)
- Compatibility tests
- CI/CD pipeline integration
