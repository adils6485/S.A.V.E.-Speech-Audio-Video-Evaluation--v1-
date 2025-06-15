#!/usr/bin/env python3
"""
Audio Diagnostic Script for Linux Speech Recognition Issues
Run this script to diagnose audio capture and speech recognition problems
"""

import os
import sys
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import wave
import tempfile
import time

def check_system_audio():
    """Check system audio configuration"""
    print("=== SYSTEM AUDIO CHECK ===")
    
    # Check PulseAudio
    try:
        os.system("pulseaudio --check -v")
        print("✓ PulseAudio is running")
    except:
        print("✗ PulseAudio check failed")
    
    # Check ALSA
    try:
        os.system("aplay -l > /dev/null 2>&1")
        print("✓ ALSA devices available")
    except:
        print("✗ ALSA check failed")

def list_audio_devices():
    """List all available audio devices"""
    print("\n=== AUDIO DEVICES ===")
    try:
        devices = sd.query_devices()
        print(f"Default input device: {sd.default.device[0]}")
        print(f"Default output device: {sd.default.device[1]}")
        
        print("\nAll devices:")
        for i, device in enumerate(devices):
            device_type = []
            if device['max_input_channels'] > 0:
                device_type.append(f"IN({device['max_input_channels']})")
            if device['max_output_channels'] > 0:
                device_type.append(f"OUT({device['max_output_channels']})")
            
            print(f"  {i:2d}: {device['name']} [{', '.join(device_type)}] - {device['default_samplerate']}Hz")
        
        return devices
    except Exception as e:
        print(f"Error listing devices: {e}")
        return []

def test_audio_recording(device_id=None, duration=3):
    """Test audio recording with specified device"""
    print(f"\n=== RECORDING TEST (Device: {device_id}) ===")
    
    try:
        if device_id is not None:
            sd.default.device[0] = device_id
            
        print(f"Recording for {duration} seconds... Please speak clearly!")
        
        # Record audio
        sample_rate = 16000
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1, 
                          dtype='float64')
        sd.wait()
        
        # Analyze recording
        audio_level = np.abs(recording).mean()
        max_level = np.abs(recording).max()
        rms_level = np.sqrt(np.mean(recording**2))
        
        print(f"Audio Analysis:")
        print(f"  Mean level: {audio_level:.6f}")
        print(f"  Max level:  {max_level:.6f}")
        print(f"  RMS level:  {rms_level:.6f}")
        
        # Quality assessment
        if audio_level < 0.001:
            print("  Status: ✗ VERY LOW - Possible microphone issue")
            return None
        elif audio_level < 0.01:
            print("  Status: ⚠ LOW - May have recognition issues")
        else:
            print("  Status: ✓ GOOD - Audio level looks fine")
            
        return recording
        
    except Exception as e:
        print(f"Recording test failed: {e}")
        return None

def test_speech_recognition(audio_data, sample_rate=16000):
    """Test speech recognition with the recorded audio"""
    print("\n=== SPEECH RECOGNITION TEST ===")
    
    if audio_data is None:
        print("No audio data to test")
        return
    
    # Save as temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
        temp_path = temp_wav.name
    
    try:
        # Save audio as WAV
        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            # Convert to 16-bit integer
            audio_int16 = np.clip(audio_data.flatten() * 32767, -32768, 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())
        
        print(f"WAV file created: {temp_path}")
        
        # Test with different recognizer settings
        recognizer = sr.Recognizer()
        
        test_configs = [
            {"name": "Default", "energy_threshold": 300, "dynamic": False},
            {"name": "Sensitive", "energy_threshold": 100, "dynamic": True},
            {"name": "Very Sensitive", "energy_threshold": 50, "dynamic": True},
        ]
        
        for config in test_configs:
            print(f"\nTesting with {config['name']} settings:")
            print(f"  Energy threshold: {config['energy_threshold']}")
            print(f"  Dynamic threshold: {config['dynamic']}")
            
            recognizer.energy_threshold = config['energy_threshold']
            recognizer.dynamic_energy_threshold = config['dynamic']
            
            try:
                with sr.AudioFile(temp_path) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.record(source)
                
                # Try recognition
                text = recognizer.recognize_google(audio, language='en-US')
                print(f"  Result: ✓ '{text}'")
                
            except sr.UnknownValueError:
                print("  Result: ✗ Could not understand audio")
            except sr.RequestError as e:
                print(f"  Result: ✗ Request error: {e}")
            except Exception as e:
                print(f"  Result: ✗ Error: {e}")
    
    finally:
        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass

def test_internet_connection():
    """Test internet connection for Google Speech API"""
    print("\n=== INTERNET CONNECTION TEST ===")
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✓ Internet connection OK")
        return True
    except Exception as e:
        print(f"✗ Internet connection failed: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("Linux Audio & Speech Recognition Diagnostic Tool")
    print("=" * 50)
    
    # Check system audio
    check_system_audio()
    
    # List devices
    devices = list_audio_devices()
    
    # Test internet
    if not test_internet_connection():
        print("⚠ Speech recognition requires internet connection!")
        return
    
    # Find input devices
    input_devices = [i for i, dev in enumerate(devices) if dev['max_input_channels'] > 0]
    
    if not input_devices:
        print("✗ No input devices found!")
        return
    
    print(f"\nFound {len(input_devices)} input device(s)")
    
    # Test each input device
    for device_id in input_devices[:3]:  # Test up to 3 devices
        device_name = devices[device_id]['name']
        print(f"\n" + "="*50)
        print(f"TESTING DEVICE {device_id}: {device_name}")
        print("="*50)
        
        # Record audio
        audio_data = test_audio_recording(device_id, duration=3)
        
        # Test recognition
        if audio_data is not None:
            test_speech_recognition(audio_data)
        
        input("Press Enter to test next device (or Ctrl+C to exit)...")
    
    print("\nDiagnostic complete!")
    print("\nIf all tests failed:")
    print("1. Check microphone permissions")
    print("2. Try: sudo apt install pulseaudio-utils alsa-utils")
    print("3. Try: pulseaudio --start")
    print("4. Check system sound settings")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDiagnostic interrupted by user")
    except Exception as e:
        print(f"Diagnostic error: {e}")