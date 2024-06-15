"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""
"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""
import speech_recognition as sr

import pyttsx3
engine = pyttsx3.init()

import os

import google.generativeai as genai

genai.configure(api_key="AIzaSyCk24LgF1T9VW4fqltn8rubr2wYFFmJpEk")

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "hello",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Hello! How can I help you today? \n",
      ],
    },
  ]
)

#response = chat_session.send_message("Explain about andhra pradesh")

#print(response.text)
#engine.say(response.text)
#engine.runAndWait()


def recognize_speech_from_mic(duration=5):
  recognizer = sr.Recognizer()
  microphone = sr.Microphone()

  print("Ajusting for ambient noise... Please wait...")
  with microphone as source:
    recognizer.adjust_for_ambient_noise(source)
    print("Listening for speech...")
    audio = recognizer.listen(source, timeout=duration)

  print("Recognizing speech...")
  try:
    transcription = recognizer.recognize_google(audio)
    print("You said: " + transcription)

    response = chat_session.send_message(f"Limit to 200 words \n {transcription}")

    print(response.text)
    engine.say(response.text)
    engine.runAndWait()
  except sr.RequestError:
    print("API was unreachable or unresponsive")
  except sr.UnknownValueError:
    print("Unable to recognize speech")

if __name__ == "__main__":
    recognize_speech_from_mic()