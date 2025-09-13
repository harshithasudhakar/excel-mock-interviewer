# Interactive Audio Features

## Overview
The Excel Mock Interviewer now supports interactive audio features for a more natural interview experience.

## Audio Features

### 🔊 Text-to-Speech (Questions & Feedback)
- **Auto-play**: Questions and feedback are automatically spoken when displayed
- **Repeat button**: Click the 🔊 button next to any question to hear it again
- **Summary reading**: Click "🔊 Read Summary" to hear the final assessment

### 🎤 Voice Input (Speech-to-Text)
- **Voice button**: Click the 🎤 button to start voice recording
- **Recording indicator**: Button turns red (🛑) and pulses while recording
- **Auto-append**: Spoken text is automatically added to the text box
- **Hybrid input**: You can use both voice and typing in the same answer

## Browser Compatibility

### Speech Recognition (Voice Input)
- ✅ Chrome/Edge (recommended)
- ✅ Safari (iOS/macOS)
- ❌ Firefox (limited support)

### Speech Synthesis (Text-to-Speech)
- ✅ All modern browsers
- ✅ Works offline

## Usage Tips

1. **Grant microphone permission** when prompted by your browser
2. **Speak clearly** and pause briefly before clicking stop
3. **Use text input as backup** if voice recognition fails
4. **Adjust browser volume** for comfortable audio playback
5. **Use headphones** to prevent audio feedback during recording

## Troubleshooting

### Voice Input Not Working
- Check microphone permissions in browser settings
- Try refreshing the page and granting permission again
- Switch to Chrome/Edge if using Firefox
- Ensure microphone is not being used by other applications

### Audio Playback Issues
- Check browser volume settings
- Ensure speakers/headphones are connected
- Try refreshing the page if audio stops working

### Performance Tips
- Close other tabs using microphone/audio
- Use a quiet environment for better voice recognition
- Speak at normal pace (not too fast or slow)

## Technical Details
- Uses Web Speech API (built into browsers)
- No additional downloads or plugins required
- Works entirely in the browser (no server-side audio processing)
- Supports multiple languages (configured for English by default)