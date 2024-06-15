import os
import speech_recognition as sr
import pyttsx3
import requests
import google.generativeai as genai
import cv2

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Configure Google Generative AI with API key
api_key = "AIzaSyCk24LgF1T9VW4fqltn8rubr2wYFFmJpEk"  # Replace with your actual API key
if not api_key:
    raise ValueError("API key for Google Generative AI is not set in the environment variables")

genai.configure(api_key=api_key)

# OpenWeatherMap API key
weather_api_key = "500e0494f975ccb2509cf51e9fee6476"  # Replace with your actual API key

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

chat_session = model.start_chat(
    history=[
        {"role": "user", "parts": ["hello\n"]},
        {"role": "model", "parts": ["Hello! How can I help you today?\n"]},
    ]
)

def get_weather_data(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "q=" + city_name + "&appid=" + api_key + "&units=metric"

    response = requests.get(complete_url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None

def get_temperature(weather_data):
    if weather_data:
        return weather_data['main']['temp']
    return None

def get_description(weather_data):
    if weather_data:
        return weather_data['weather'][0]['description']
    return None

def recognize_speech_from_mic(duration=5):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Adjusting for ambient noise... Please wait.")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for speech...")
        audio = recognizer.listen(source, timeout=duration)

    print("Recognizing speech...")
    try:
        transcription = recognizer.recognize_google(audio)
        print("You said: " + transcription)

        if "weather" in transcription.lower():
            speak("Which city's weather would you like to know?")
            print("Listening for the city name...")
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=duration)
                city_name = recognizer.recognize_google(audio)
            print("You said: " + city_name)
            speak(f"Fetching weather for {city_name}.")
            weather_data = get_weather_data(city_name, weather_api_key)
            if weather_data:
                temperature = get_temperature(weather_data)
                description = get_description(weather_data)
                if temperature is not None and description is not None:
                    weather_report = f"The weather in {city_name} is {description} with a temperature of {temperature:.1f} degrees Celsius."
                    print(weather_report)
                    speak(weather_report)
                else:
                    print("Error: Could not retrieve complete weather information.")
                    speak("Error: Could not retrieve complete weather information.")
            else:
                print(f"Error: Could not retrieve weather data for {city_name}.")
                speak(f"Error: Could not retrieve weather data for {city_name}.")

        elif "camera" in transcription.lower():
            speak("Accessing the camera.")
            capture_image()

        else:
            response = chat_session.send_message(f"limit 100 words\n{transcription}")
            print(response.text)

            # Get the list of available voices
            voices = engine.getProperty('voices')
            # Set the desired voice (example: the first voice in the list)
            engine.setProperty('voice', voices[1].id)

            # Say the response text
            engine.say(response.text)
            engine.runAndWait()

    except sr.RequestError:
        print("API was unreachable or unresponsive")
    except sr.UnknownValueError:
        print("Unable to recognize speech")

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        speak("Error: Could not open camera.")
        return

    print("Press 's' to save the image or 'q' to quit without saving.")
    speak("Press 's' to save the image or 'q' to quit without saving.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            speak("Error: Failed to capture image.")
            break

        cv2.imshow('Camera', frame)

        key = cv2.waitKey(1)
        if key == ord('s'):
            file_path = "captured_image.jpg"
            cv2.imwrite(file_path, frame)
            print(f"Image saved as {file_path}")
            speak(f"Image saved as {file_path}")
            break
        elif key == ord('q'):
            print("Quitting without saving the image.")
            speak("Quitting without saving the image.")
            break

    cap.release()
    cv2.destroyAllWindows()

def speak(text):
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    recognize_speech_from_mic()
