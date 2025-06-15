#!/usr/bin/env python3
"""
Real-time Speech Risk Detection System
Combines audio capture, transcription, and risk analysis
"""

import os
import sys
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import time
import json
import requests
import wave
import tempfile
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class SpeechRiskDetector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Speech Risk Detection System")
        self.root.geometry("900x700")
        
        # Groq API settings
        self.groq_api_key = "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"
        self.groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_duration = 5  # seconds
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        # Initialize GUI
        self.setup_gui()
        
        print("Speech Risk Detection System initialized.")
    
    def setup_gui(self):
        """Setup the main GUI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Speech Risk Detection System", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start/Stop button
        self.control_btn = ttk.Button(control_frame, text="Start Listening", 
                                     command=self.toggle_listening)
        self.control_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to start")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=20)
        
        # Real-time transcription
        transcript_frame = ttk.LabelFrame(main_frame, text="Live Transcription", padding="10")
        transcript_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.transcript_text = scrolledtext.ScrolledText(transcript_frame, height=8, wrap=tk.WORD)
        self.transcript_text.pack(fill=tk.BOTH, expand=True)
        
        # Risk analysis display
        risk_frame = ttk.LabelFrame(main_frame, text="Risk Analysis", padding="10")
        risk_frame.pack(fill=tk.BOTH, expand=True)
        
        # Risk level display
        risk_info_frame = ttk.Frame(risk_frame)
        risk_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(risk_info_frame, text="Risk Level:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.risk_level_var = tk.StringVar(value="Not analyzed")
        self.risk_label = ttk.Label(risk_info_frame, textvariable=self.risk_level_var, 
                                   font=("Arial", 10, "bold"))
        self.risk_label.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(risk_info_frame, text="Confidence:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 0))
        self.confidence_var = tk.StringVar(value="0%")
        ttk.Label(risk_info_frame, textvariable=self.confidence_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Risk meter
        self.setup_risk_meter(risk_frame)
    
    def setup_risk_meter(self, parent):
        """Setup the risk visualization meter"""
        self.risk_figure = Figure(figsize=(8, 2), dpi=100)
        self.risk_ax = self.risk_figure.add_subplot(111)
        
        # Create risk meter
        self.risk_ax.set_xlim(0, 10)
        self.risk_ax.set_ylim(-0.5, 0.5)
        self.risk_ax.set_xticks([0, 2.5, 5, 7.5, 10])
        self.risk_ax.set_xticklabels(['Minimal', 'Low', 'Medium', 'High', 'Severe'])
        self.risk_ax.set_yticks([])
        self.risk_ax.set_title('Risk Level Indicator')
        
        # Color gradient background
        colors = ['green', 'yellow', 'orange', 'red', 'darkred']
        for i, color in enumerate(colors):
            self.risk_ax.axvspan(i*2, (i+1)*2, alpha=0.3, color=color)
        
        # Risk indicator (initially at 0)
        self.risk_indicator = self.risk_ax.axvline(x=0, color='black', linewidth=3, label='Current Risk')
        
        self.risk_canvas = FigureCanvasTkAgg(self.risk_figure, parent)
        self.risk_canvas.get_tk_widget().pack(fill=tk.X, expand=True)
        self.risk_canvas.draw()
    
    def update_risk_meter(self, risk_level, confidence):
        """Update the risk meter visualization"""
        # Map risk levels to positions on meter
        risk_positions = {
            'minimal': 1,
            'low': 3,
            'medium': 5,
            'high': 7,
            'error': 0,
            'unknown': 0
        }
        
        position = risk_positions.get(risk_level, 0)
        
        # Update indicator position
        self.risk_indicator.set_xdata([position, position])
        
        # Update colors based on risk level
        colors = {
            'minimal': 'green',
            'low': 'yellow', 
            'medium': 'orange',
            'high': 'red',
            'error': 'gray',
            'unknown': 'gray'
        }
        
        self.risk_indicator.set_color(colors.get(risk_level, 'gray'))
        self.risk_canvas.draw()
        
        # Update risk label color
        self.risk_label.configure(foreground=colors.get(risk_level, 'black'))
    
    def analyze_text_with_groq(self, text):
        """Send text to Groq API for suicide risk analysis"""
        if not text.strip():
            return {"risk_level": "unknown", "confidence": 0.0, "transcription": ""}
        
        headers = {
            "Authorization": f"Bearer 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",
            "Content-Type": "application/json"
        }
        
        system_prompt = (
            "You are a mental health risk detection assistant. Analyze the following text and determine whether "
            "it indicates suicidal thoughts or intentions. Return only a JSON with two keys: 'risk_level' (one of "
            "'suicide', 'medium_risk', 'low_risk', or 'non_suicide') and 'confidence' (a float between 0 and 1 "
            "indicating likelihood of suicide risk). Be nuanced in your assessment."
        )
        
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(self.groq_endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            output = response.json()['choices'][0]['message']['content']
            
            # Parse the JSON response
            result = json.loads(output)
            
            # Map the risk levels to our application's format
            risk_mapping = {
                "suicide": "high",
                "medium_risk": "medium", 
                "low_risk": "low",
                "non_suicide": "minimal"
            }
            
            return {
                "risk_level": risk_mapping.get(result["risk_level"], "unknown"),
                "confidence": result["confidence"],
                "transcription": text
            }
            
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return {"risk_level": "error", "confidence": 0.0, "transcription": text}
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"risk_level": "error", "confidence": 0.0, "transcription": text}
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {"risk_level": "error", "confidence": 0.0, "transcription": text}
    
    def record_and_transcribe(self):
        """Record audio for 5 seconds and transcribe"""
        try:
            self.status_var.set("Recording...")
            
            # Record audio
            recording = sd.rec(int(self.chunk_duration * self.sample_rate), 
                             samplerate=self.sample_rate, 
                             channels=1, 
                             dtype='float64')
            sd.wait()
            
            self.status_var.set("Processing...")
            
            # Check if audio level is sufficient
            audio_level = np.abs(recording).mean()
            if audio_level < 0.001:
                self.status_var.set("Audio too quiet, continuing...")
                return ""
            
            # Save as temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_path = temp_wav.name
            
            try:
                # Convert to WAV format
                with wave.open(temp_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    audio_int16 = np.clip(recording.flatten() * 32767, -32768, 32767).astype(np.int16)
                    wf.writeframes(audio_int16.tobytes())
                
                # Transcribe using speech recognition
                with sr.AudioFile(temp_path) as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.record(source)
                
                text = self.recognizer.recognize_google(audio, language='en-US')
                self.status_var.set("Analyzing...")
                return text
                
            except sr.UnknownValueError:
                self.status_var.set("Could not understand audio")
                return ""
            except sr.RequestError as e:
                self.status_var.set(f"Speech recognition error: {e}")
                return ""
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            self.status_var.set(f"Recording error: {e}")
            return ""
    
    def listening_loop(self):
        """Main listening loop that runs in a separate thread"""
        while self.is_listening:
            try:
                # Record and transcribe
                text = self.record_and_transcribe()
                
                if text.strip():
                    # Update transcription display
                    timestamp = time.strftime("%H:%M:%S")
                    self.transcript_text.insert(tk.END, f"[{timestamp}] {text}\n")
                    self.transcript_text.see(tk.END)
                    
                    # Analyze with Groq
                    result = self.analyze_text_with_groq(text)
                    
                    # Update risk display
                    self.risk_level_var.set(result["risk_level"].title())
                    self.confidence_var.set(f"{result['confidence']*100:.1f}%")
                    
                    # Update risk meter
                    self.update_risk_meter(result["risk_level"], result["confidence"])
                    
                    self.status_var.set("Listening...")
                
                # Small delay between recordings
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error in listening loop: {e}")
                self.status_var.set(f"Error: {e}")
                time.sleep(1)
    
    def toggle_listening(self):
        """Start or stop the listening process"""
        if not self.is_listening:
            # Start listening
            self.is_listening = True
            self.control_btn.configure(text="Stop Listening")
            self.status_var.set("Starting...")
            
            # Start listening thread
            self.listening_thread = threading.Thread(target=self.listening_loop, daemon=True)
            self.listening_thread.start()
            
        else:
            # Stop listening
            self.is_listening = False
            self.control_btn.configure(text="Start Listening")
            self.status_var.set("Stopped")
    
    def run(self):
        """Start the GUI application"""
        try:
            # Test internet connection
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=5)
            print("✓ Internet connection OK")
        except Exception as e:
            messagebox.showwarning("Connection Warning", 
                                 f"Internet connection may be limited: {e}\n"
                                 "Speech recognition requires internet access.")
        
        # Test audio devices
        try:
            devices = sd.query_devices()
            input_devices = [i for i, dev in enumerate(devices) if dev['max_input_channels'] > 0]
            if not input_devices:
                messagebox.showerror("Audio Error", "No input devices found!")
                return
            print(f"Found {len(input_devices)} input device(s)")
        except Exception as e:
            messagebox.showerror("Audio Error", f"Audio system error: {e}")
            return
        
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = SpeechRiskDetector()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")

if __name__ == "__main__":
    main()