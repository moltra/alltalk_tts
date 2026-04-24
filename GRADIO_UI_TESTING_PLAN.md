# Gradio UI Button Testing Plan

## Overview
This document outlines a comprehensive testing plan for all buttons and interactive elements in the AllTalk Gradio UI using Playwright for browser automation and Docker logs for verification.

## Testing Approach
- **Tool**: Playwright MCP for browser automation
- **Verification**: Docker container logs to verify backend operations
- **Test Environment**: http://localhost:7856 (Gradio UI)
- **API Endpoint**: http://localhost:7855 (Backend API)

## Test Categories

### 1. Generate TTS Tab - Core Buttons

#### 1.1 Swap TTS Engine Button
**Purpose**: Switch between different TTS engines (piper, xtts, etc.)

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click "Swap TTS Engine" button
3. Verify engine dropdown changes to next available engine
4. Verify UI shows "TTS Engine changed successfully!" message
5. Verify Docker logs show engine reload request
6. Verify API endpoint `/api/enginereload` was called
7. Verify voice dropdown updates with new engine's voices
8. Verify model dropdown updates with new engine's models

**Expected Results**:
- Engine switches successfully
- Voice list updates to match new engine
- Model list updates to match new engine
- No errors in Docker logs
- API returns success status

**Docker Log Verification**:
- Check for: "Changing model loaded. Please wait."
- Check for: "Engine reload request sent"
- Check for successful engine reload

#### 1.2 Load Different Model Button
**Purpose**: Switch between different models within the current engine

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click "Load Different Model" button
3. Verify model dropdown shows available models
4. Select a different model
5. Verify UI shows model change confirmation
6. Verify Docker logs show model reload request
7. Verify API endpoint `/api/reload` was called

**Expected Results**:
- Model switches successfully
- Voice list may update if model-specific
- No errors in Docker logs
- API returns success status

**Docker Log Verification**:
- Check for: "Model changed successfully"
- Check for: "Model reload request sent"

#### 1.3 Generate TTS Button
**Purpose**: Generate text-to-speech audio from input text

**Test Steps**:
1. Navigate to Generate TTS tab
2. Enter test text in Text Input field
3. Verify voice is selected (compatible with current engine)
4. Click "Generate TTS" button
5. Verify processing indicator appears
6. Verify audio output appears when complete
7. Verify Docker logs show TTS generation
8. Verify no errors in generation

**Expected Results**:
- Audio generation starts successfully
- Processing indicator shows progress
- Audio output appears when complete
- No voice file errors (like the XTTS/Piper mismatch bug)
- Docker logs show successful generation

**Docker Log Verification**:
- Check for: "AllTalk TTS: [text]"
- Check for successful audio generation
- Check for NO voice file errors

#### 1.4 Interupt TTS Generation Button
**Purpose**: Stop an in-progress TTS generation

**Test Steps**:
1. Navigate to Generate TTS tab
2. Enter long text to ensure generation takes time
3. Click "Generate TTS" button
4. Wait for processing to start
5. Click "Interupt TTS Generation" button
6. Verify UI shows "Cancelling current TTS generation"
7. Verify Docker logs show generation cancellation
8. Verify processing stops

**Expected Results**:
- Generation is cancelled
- UI shows cancellation message
- No new audio is generated
- Docker logs show cancellation

**Docker Log Verification**:
- Check for: "Cancelling current TTS generation"
- Check for generation stop

#### 1.5 Refresh Server Settings Button
**Purpose**: Refresh UI with latest server configuration

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click "Refresh Server Settings" button
3. Verify dropdowns refresh with current settings
4. Verify voice list is current
5. Verify engine list is current
6. Verify model list is current

**Expected Results**:
- All dropdowns refresh
- Settings match current server state
- No errors in refresh

#### 1.6 Light/Dark Mode Button
**Purpose**: Toggle between light and dark theme

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click "Light/Dark Mode" button
3. Verify theme toggles
4. Click again to toggle back
5. Verify theme toggles back

**Expected Results**:
- Theme toggles successfully
- UI remains functional in both modes

### 2. Voice Selection Dropdowns

#### 2.1 Character Voice Dropdown
**Purpose**: Select the main character voice for TTS

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click Character Voice dropdown
3. Verify list shows voices compatible with current engine
4. Select a different voice
5. Verify selection updates
6. Generate TTS with new voice
7. Verify Docker logs use correct voice

**Expected Results**:
- Voice list matches current engine
- Selection updates successfully
- TTS generation uses selected voice
- No voice file errors

**Docker Log Verification**:
- Check for correct voice being used in generation
- Check for NO voice file path errors

#### 2.2 Narrator Voice Dropdown
**Purpose**: Select narrator voice for narration mode

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click Narrator Voice dropdown
3. Verify list shows voices compatible with current engine
4. Select a different voice
5. Verify selection updates

**Expected Results**:
- Voice list matches current engine
- Selection updates successfully

#### 2.3 RVC Character Voice Dropdown
**Purpose**: Select RVC model for character voice conversion

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click RVC Character Voice dropdown
3. Verify list shows available RVC models or "Disabled"
4. Select a different option
5. Verify selection updates

**Expected Results**:
- List shows RVC models or "Disabled"
- Selection updates successfully

#### 2.4 RVC Narrator Voice Dropdown
**Purpose**: Select RVC model for narrator voice conversion

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click RVC Narrator Voice dropdown
3. Verify list shows available RVC models or "Disabled"
4. Select a different option
5. Verify selection updates

**Expected Results**:
- List shows RVC models or "Disabled"
- Selection updates successfully

### 3. Engine and Model Dropdowns

#### 3.1 TTS Engine Dropdown
**Purpose**: View and select available TTS engines

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click TTS Engine dropdown
3. Verify list shows available engines (piper, xtts, etc.)
4. Select a different engine
5. Verify selection updates (but engine not changed until button clicked)

**Expected Results**:
- List shows all available engines
- Selection updates in dropdown

#### 3.2 TTS Models Dropdown
**Purpose**: View and select available models for current engine

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click TTS Models dropdown
3. Verify list shows models for current engine
4. Select a different model
5. Verify selection updates (but model not changed until button clicked)

**Expected Results**:
- List shows models for current engine
- Selection updates in dropdown

### 4. Advanced Settings Sections

#### 4.1 Advanced Engine/Model Settings Accordion
**Purpose**: Access advanced engine and model settings

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click "Advanced Engine/Model Settings ▼" button
3. Verify accordion expands
4. Verify advanced settings are visible
5. Click again to collapse
6. Verify accordion collapses

**Expected Results**:
- Accordion toggles successfully
- Advanced settings are accessible

#### 4.2 Docker IP/URL for API Address Updater
**Purpose**: Update Docker IP/URL for API communication

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click "Docker IP/URL for API Address updater ▼" button
3. Verify accordion expands
4. Verify IP/URL input field is visible
5. Enter new IP/URL
6. Click update button
7. Verify setting is saved

**Expected Results**:
- Accordion toggles successfully
- IP/URL can be updated
- Setting persists

### 5. Help Sections

#### 5.1 TTS Generation Basics Help
**Purpose**: Display help for TTS generation basics

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click "HELP - 🎯 TTS Generation Basics ▼" button
3. Verify accordion expands
4. Verify help content is displayed
5. Click again to collapse
6. Verify accordion collapses

**Expected Results**:
- Accordion toggles successfully
- Help content is readable

#### 5.2 Advanced TTS Features Help
**Purpose**: Display help for advanced TTS features

**Test Steps**:
1. Navigate to Generate TTS tab
2. Click "HELP - ⚙️ Advanced TTS Features ▼" button
3. Verify accordion expands
4. Verify help content is displayed
5. Click again to collapse
6. Verify accordion collapses

**Expected Results**:
- Accordion toggles successfully
- Help content is readable

### 6. Tab Navigation

#### 6.1 Tab Switching
**Purpose**: Navigate between different Gradio tabs

**Test Steps**:
1. Click each tab in sequence:
   - AllTalk v2 Welcome page
   - Generate TTS
   - Voice2RVC
   - Transcribe
   - Dictate
   - TTS Generator
   - Global Settings
   - TTS Engines Settings
   - Model Downloads
   - Documentation
   - About this project
2. Verify each tab loads successfully
3. Verify content is displayed correctly
4. Verify no errors in UI

**Expected Results**:
- All tabs load successfully
- Content is displayed correctly
- No errors in navigation

### 7. Voice2RVC Tab Buttons

#### 7.1 Submit to RVC Button
**Purpose**: Submit audio for RVC voice conversion

**Test Steps**:
1. Navigate to Voice2RVC tab
2. Upload or select audio input
3. Select RVC voice
4. Adjust pitch if needed
5. Click "Submit to RVC" button
6. Verify processing starts
7. Verify converted audio appears
8. Verify Docker logs show RVC processing

**Expected Results**:
- RVC conversion starts successfully
- Converted audio appears
- Docker logs show RVC processing

**Docker Log Verification**:
- Check for RVC processing logs
- Check for successful conversion

### 8. Transcribe Tab Buttons

#### 8.1 Transcribe Button
**Purpose**: Transcribe audio to text

**Test Steps**:
1. Navigate to Transcribe tab
2. Upload audio file
3. Click transcribe button
4. Verify transcription starts
5. Verify text output appears
6. Verify Docker logs show transcription

**Expected Results**:
- Transcription starts successfully
- Text output appears
- Docker logs show transcription

**Docker Log Verification**:
- Check for transcription logs
- Check for successful transcription

### 9. Dictate Tab Buttons

#### 9.1 Dictate Controls
**Purpose**: Record and transcribe live audio

**Test Steps**:
1. Navigate to Dictate tab
2. Click record button
3. Speak into microphone
4. Click stop button
5. Verify transcription appears
6. Verify Docker logs show dictation

**Expected Results**:
- Recording starts/stops successfully
- Transcription appears
- Docker logs show dictation

**Docker Log Verification**:
- Check for dictation logs
- Check for successful transcription

### 10. Global Settings Tab Buttons

#### 10.1 Update Settings Buttons
**Purpose**: Update various global settings

**Test Steps**:
1. Navigate to Global Settings tab
2. Modify various settings
3. Click "Update Settings" button
4. Verify settings are saved
5. Verify Docker logs show setting updates

**Expected Results**:
- Settings save successfully
- Configuration persists
- Docker logs show updates

**Docker Log Verification**:
- Check for setting save logs
- Check for configuration updates

### 11. TTS Engines Settings Tab Buttons

#### 11.1 Engine-Specific Settings Buttons
**Purpose**: Update engine-specific settings

**Test Steps**:
1. Navigate to TTS Engines Settings tab
2. Select engine to configure
3. Modify engine-specific settings
4. Click update button
5. Verify settings are saved
6. Verify Docker logs show engine setting updates

**Expected Results**:
- Engine settings save successfully
- Configuration persists
- Docker logs show updates

**Docker Log Verification**:
- Check for engine setting logs
- Check for configuration updates

### 12. Model Downloads Tab Buttons

#### 12.1 Download Model Buttons
**Purpose**: Download new TTS models

**Test Steps**:
1. Navigate to Model Downloads tab
2. Select model to download
3. Click download button
4. Verify download starts
5. Verify progress indicator
6. Verify completion
7. Verify Docker logs show download

**Expected Results**:
- Download starts successfully
- Progress is shown
- Download completes successfully
- Docker logs show download

**Docker Log Verification**:
- Check for download logs
- Check for successful download

### 13. Critical Bug Regression Tests

#### 13.1 Engine Switching Voice File Bug
**Purpose**: Verify engine switching doesn't cause voice file path errors

**Test Steps**:
1. Start with Piper engine
2. Note current voice (e.g., en_US-amy-medium.onnx)
3. Click "Swap TTS Engine" to switch to XTTS
4. Verify voice dropdown updates to XTTS voices (e.g., builtin:Aaron Dreschner)
5. Select a valid XTTS voice
6. Enter test text
7. Click "Generate TTS"
8. Verify NO errors about opening Piper voice files
9. Verify Docker logs show XTTS generation with correct voice

**Expected Results**:
- NO "Error opening '/home/alltalk/voices/en_US-amy-medium.onnx'" errors
- XTTS voice is used (e.g., builtin:Claribel Dervla)
- Generation succeeds

**Docker Log Verification**:
- Check for NO voice file path errors
- Check for correct voice being used
- Check for successful generation

#### 13.2 Voice Compatibility Verification
**Purpose**: Ensure voices are compatible with current engine

**Test Steps**:
1. For each engine (piper, xtts, etc.):
   a. Switch to engine
   b. Verify voice list shows only compatible voices
   c. Select each voice
   d. Generate TTS
   e. Verify no voice file errors

**Expected Results**:
- Voice list shows only compatible voices
- All voices work with their respective engines
- No cross-engine voice file errors

**Docker Log Verification**:
- Check for NO voice file errors
- Check for successful generation with each voice

## Test Implementation Strategy

### Test File Structure
```
tests/
├── test_gradio_ui_buttons.py      # Main button tests
├── test_gradio_ui_tabs.py         # Tab navigation tests
├── test_gradio_ui_voice.py        # Voice selection tests
├── test_gradio_ui_engine.py       # Engine/model tests
├── test_gradio_ui_regression.py   # Regression tests
└── test_gradio_ui_integration.py  # End-to-end integration tests
```

### Test Utilities
- Docker log monitoring function
- Screenshot capture for visual verification
- API response verification
- Error detection and reporting

### Execution Order
1. Basic button functionality tests
2. Voice selection tests
3. Engine/model switching tests
4. Tab navigation tests
5. Regression tests
6. Integration tests

## Success Criteria
- All buttons are clickable and responsive
- All buttons trigger correct backend operations
- No voice file path errors after engine switching
- All dropdowns show correct options for current state
- Docker logs confirm expected operations
- API endpoints are called correctly
- No unexpected errors in UI or logs
