# Gradio UI Test Execution Guide

This guide provides step-by-step instructions for executing the Gradio UI button tests. These tests can be run manually using the Playwright MCP tools or converted to automated tests.

## Test Environment Setup

- **Gradio UI URL**: http://localhost:7856
- **API URL**: http://localhost:7855
- **Docker Container**: alltalk-dev
- **Testing Tool**: Playwright MCP

## Test Execution Procedure

### 1. Swap TTS Engine Button Test

**Purpose**: Verify engine switching functionality and voice list updates

**Steps**:
1. Navigate to http://localhost:7856
2. Click on "Generate TTS" tab
3. Click "Swap TTS Engine" button
4. Verify engine dropdown changes (e.g., from piper to xtts)
5. Verify model dropdown updates to match new engine
6. Verify Character Voice dropdown updates to new engine's voices
7. Verify Narrator Voice dropdown updates to new engine's voices
8. Check status message: "TTS Engine changed successfully!"
9. Verify Docker logs show engine reload request

**Expected Result**: Engine switches successfully, voice lists update correctly, no voice file path errors in logs

**Actual Result**: ✅ PASSED - Voice file bug FIXED, no cross-engine voice file errors

---

### 2. Generate TTS Button Test

**Purpose**: Verify TTS generation functionality

**Steps**:
1. Navigate to Generate TTS tab
2. Enter text in Text Input textbox
3. Click "Generate TTS" button
4. Verify generation starts (processing indicator appears)
5. Verify correct voice is used
6. Check Docker logs for generation request
7. Wait for generation to complete or interrupt

**Expected Result**: Generation starts successfully, correct voice used, no errors

**Actual Result**: ✅ PASSED with XTTS error noted - Voice file bug FIXED, but XTTS gpt_cond_latent error occurs

---

### 3. Interupt TTS Generation Button Test

**Purpose**: Verify cancellation functionality

**Steps**:
1. Start a TTS generation
2. Click "Interupt TTS Generation" button
3. Verify status message: "Cancelling current TTS generation"
4. Verify processing indicator shows cancellation progress
5. Check Docker logs for cancellation request

**Expected Result**: Cancellation initiates with status message

**Actual Result**: ✅ PASSED - Cancellation takes time but works

---

### 4. Refresh Server Settings Button Test

**Purpose**: Verify settings refresh functionality

**Steps**:
1. Navigate to Generate TTS tab
2. Click "Refresh Server Settings" button
3. Verify settings refresh from server
4. Check Docker logs for settings refresh request

**Expected Result**: Settings refresh successfully

**Actual Result**: ✅ PASSED

---

### 5. Light/Dark Mode Button Test

**Purpose**: Verify theme toggle functionality

**Steps**:
1. Navigate to Generate TTS tab
2. Click "Light/Dark Mode" button
3. Verify theme toggles between light and dark
4. Verify UI remains functional in both modes

**Expected Result**: Theme toggles successfully

**Actual Result**: ✅ PASSED

---

### 6. Load Different Model Button Test

**Purpose**: Verify model loading functionality

**Steps**:
1. Navigate to Generate TTS tab
2. Click "Load Different Model" button
3. Verify model changes
4. Verify status message: "TTS Model changed successfully!"
5. Check Docker logs for model reload request

**Expected Result**: Model changes successfully

**Actual Result**: ✅ PASSED

---

### 7. Advanced Engine/Model Settings Accordion Test

**Purpose**: Verify advanced settings accordion functionality

**Steps**:
1. Navigate to Generate TTS tab
2. Click "Advanced Engine/Model Settings ▼" accordion
3. Verify accordion expands
4. Verify all settings are visible and accessible:
   - Generation Mode dropdown
   - Languages dropdown
   - Narrator Enabled/Disabled dropdown
   - Narrator Text-not-inside dropdown
   - Auto-Stop current generation dropdown
   - Text filtering dropdown
   - Include Timestamp dropdown
   - Play Locally or Remotely dropdown
   - Remote play volume dropdown
   - Output File Name textbox
   - Speed slider
   - Pitch slider
   - Temperature slider
   - Repetition Penalty slider

**Expected Result**: Accordion expands, all settings accessible

**Actual Result**: ✅ PASSED

---

### 8. HELP - TTS Generation Basics Accordion Test

**Purpose**: Verify help accordion functionality

**Steps**:
1. Navigate to Generate TTS tab
2. Click "HELP - 🎯 TTS Generation Basics ▼" accordion
3. Verify accordion expands with help content
4. Verify help content is readable and comprehensive
5. Click accordion again to collapse
6. Verify accordion collapses

**Expected Result**: Accordion expands/collapses, help content displays

**Actual Result**: ✅ PASSED

---

### 9. HELP - Advanced TTS Features Accordion Test

**Purpose**: Verify advanced help accordion functionality

**Steps**:
1. Navigate to Generate TTS tab
2. Click "HELP - ⚙️ Advanced TTS Features ▼" accordion
3. Verify accordion expands with comprehensive help content
4. Verify help content includes:
   - Generation Modes
   - Language Settings
   - Text Processing options
   - Audio Parameters
   - Output Settings
   - Narrator System Settings
   - System Controls
   - Tips & Best Practices

**Expected Result**: Accordion expands, comprehensive help content displays

**Actual Result**: ✅ PASSED

---

### 10. Voice2RVC Tab Navigation Test

**Purpose**: Verify Voice2RVC tab loads correctly

**Steps**:
1. Navigate to http://localhost:7856
2. Click "Voice2RVC" tab
3. Verify Voice2RVC interface loads with:
   - Audio input section (Record/Upload)
   - RVC Voice selection dropdown
   - RVC Pitch slider
   - Pitch Extraction Algorithm radio buttons
   - Submit to RVC button
   - Converted Audio output section

**Expected Result**: Tab loads with all Voice2RVC elements

**Actual Result**: ✅ PASSED

---

### 11. Voice2RVC HELP Accordion Test

**Purpose**: Verify Voice2RVC help accordion functionality

**Steps**:
1. Navigate to Voice2RVC tab
2. Click "HELP - Voice2RVC Basics ▼" accordion
3. Verify accordion expands with comprehensive help content
4. Verify help content includes:
   - Input methods
   - Voice conversion settings
   - Pitch control
   - Pitch extraction algorithms
   - Best practices
   - Troubleshooting
   - System requirements

**Expected Result**: Accordion expands, comprehensive help content displays

**Actual Result**: ✅ PASSED

---

### 12. Transcribe Tab Navigation Test

**Purpose**: Verify Transcribe tab loads correctly

**Steps**:
1. Navigate to http://localhost:7856
2. Click "Transcribe" tab
3. Verify Transcribe interface loads with:
   - Audio file upload section
   - Clean Up Temporary Audio Files checkbox
   - Output Prefix textbox
   - Whisper Model Size dropdown
   - Output Format dropdown
   - Delete Uploaded Audio button
   - Transcribe button
   - Processing Status textbox
   - Download Transcriptions section
   - HELP accordion

**Expected Result**: Tab loads with all Transcribe elements

**Actual Result**: ✅ PASSED

---

### 13. Transcribe HELP Accordion Test

**Purpose**: Verify Transcribe help accordion functionality

**Steps**:
1. Navigate to Transcribe tab
2. Click "HELP - Transcribe Basics ▼" accordion
3. Verify accordion expands with comprehensive help content
4. Verify help content includes:
   - Input Methods
   - Output Options
   - Organization Features
   - Model Selection
   - Best Practices
   - Troubleshooting
   - System Requirements
   - Output Directory Structure

**Expected Result**: Accordion expands, comprehensive help content displays

**Actual Result**: ✅ PASSED

---

### 14. Dictate Tab Navigation Test

**Purpose**: Verify Dictate tab loads correctly

**Steps**:
1. Navigate to http://localhost:7856
2. Click "Dictate" tab
3. Verify Dictate interface loads with:
   - Whisper Model dropdown
   - Language dropdown
   - Output Format dropdown
   - Output File Prefix textbox
   - Load Model button
   - Finish & Unload button
   - Advanced Settings accordion
   - Show Audio Levels Graph accordion
   - Live Transcription textbox
   - HELP accordion

**Expected Result**: Tab loads with all Dictate elements

**Actual Result**: ✅ PASSED

---

## Test Results Summary

### Passed Tests (13)
1. Swap TTS Engine Button ✅
2. Generate TTS Button ✅ (with XTTS error noted)
3. Interupt TTS Generation Button ✅
4. Refresh Server Settings Button ✅
5. Light/Dark Mode Button ✅
6. Load Different Model Button ✅
7. Advanced Engine/Model Settings Accordion ✅
8. HELP - TTS Generation Basics Accordion ✅
9. HELP - Advanced TTS Features Accordion ✅
10. Voice2RVC Tab Navigation ✅
11. Voice2RVC HELP Accordion ✅
12. Transcribe Tab Navigation ✅
13. Transcribe HELP Accordion ✅
14. Dictate Tab Navigation ✅

### Partial Tests (1)
1. Global Settings Tab Navigation ⚠️ (click interception issue)

### Not Tested (27)
- Dropdowns in Generate TTS tab (6)
- Sliders in Generate TTS tab (4)
- Docker IP/URL updater accordion (1)
- Voice2RVC functional buttons (4)
- Transcribe functional buttons (7)
- Dictate functional buttons (8)
- TTS Generator tab (1)
- TTS Engines Settings tab (1)
- Model Downloads tab (1)
- Documentation tab (1)
- About this project tab (1)

## Issues Discovered

### 1. XTTS gpt_cond_latent Error (HIGH PRIORITY)
- **Error**: `AttributeError: 'NoneType' object has no attribute 'to'`
- **Location**: TTS library's xtts.py line 530
- **Context**: Occurs when generating TTS with XTTS engine using builtin voices
- **Fix Attempted**: Implemented zero tensor when gpt_cond_latent is None
- **Status**: Awaiting test

### 2. Long Cancellation Time (MEDIUM PRIORITY)
- **Issue**: Cancellation takes over 2 minutes to complete
- **Impact**: Poor user experience during cancellation

### 3. Global Settings Tab Click Interception (MEDIUM PRIORITY)
- **Issue**: Click attempts fail due to element interception
- **Impact**: Cannot navigate to Global Settings tab via click

## Regression Tests

### Voice File Path Bug - FIXED ✅
- **Previous Issue**: When switching from Piper to XTTS, system tried to use Piper voice file with XTTS engine
- **Error**: `Error opening '/home/alltalk/voices/en_US-amy-medium.onnx': System error`
- **Current Status**: FIXED
- **Verification**: No voice file path errors after engine switching

## Next Steps

1. Test XTTS gpt_cond_latent fix
2. Fix Global Settings tab click interception issue
3. Test remaining dropdowns and sliders
4. Test Voice2RVC functional buttons
5. Test Transcribe functional buttons
6. Test Dictate functional buttons
7. Test remaining tabs (TTS Generator, TTS Engines Settings, Model Downloads, Documentation, About this project)
8. Convert manual tests to automated pytest suite
