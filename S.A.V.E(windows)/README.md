# S.A.V.E: Suicide Alert via Vision and Emotion

S.A.V.E is a multimodal suicide risk detection application that evaluates user input across text, speech, and video in real time. Designed for educational and research purposes, the system demonstrates how AI can help flag early warning signs of mental distress.

## 🔍 Overview

This advanced system provides tools to help identify potential suicide risk indicators through multiple modalities including text, speech, and video analysis.

Currently, the app supports:

✓ Text-based suicide risk detection  
✓ Realtime Speech input analysis  
✓ Realtime Video emotional monitoring  

If a message is classified as suicidal, the system can be extended to notify an authorized contact via email for timely intervention.

**IMPORTANT:** This system is designed for educational and research purposes only. It is not a substitute for professional mental health assessment. Always consult qualified mental health professionals for concerns about suicide risk.

## 💡 Features

- Text classification using trained `.pkl` model  
- Realtime microphone-based speech recognition and analysis  
- Realtime video-based emotion detection using webcam  
- Integration with Google Gemini API for advanced suicide risk inference  
- Email alert system using Resend API  
- Interactive GUI using Tkinter  
- Modular and scalable architecture  

## ⚙️ Technologies and Libraries Used

- os  
- sys  
- numpy  
- threading  
- sounddevice  
- queue  
- tkinter  
- ttk  
- filedialog  
- scrolledtext  
- matplotlib  
- matplotlib.backends.backend_tkagg  
- speech_recognition  
- requests  
- json  
- wave  
- tempfile  
- cv2  
- datetime  
- PIL (Image, ImageTk)  
- emotion_detections.zeye_tracking (for text_based_scan and send_alert_email functions)  


## 🔭 Future Scope

In the future, this system will integrate with social media platforms such as Twitter, Instagram, and messaging services to monitor real-time user activity. This integration will allow for early detection of concerning language and provide immediate support or escalate to professionals when needed.

## ⚠️ Disclaimer

This system is designed strictly for educational and research purposes.

- It does not replace professional psychological evaluation.  
- Any detected risk should be verified by licensed mental health professionals.  
- Always seek qualified help in cases of mental distress or emergency.  

## 🤝 Acknowledgements

- Resend for email integration  
- OpenCV and PIL for real-time emotion tracking  
- Open-source libraries and research communities  
