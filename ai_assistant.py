import ssl
import certifi
import assemblyai as aai
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import ollama
ssl._create_default_https_context = ssl._create_unverified_context

class AI_Assistant:
    def __init__(self) -> None:
        aai.settings.api_key = "" #removed for github
        self.client = ElevenLabs(
            api_key = "" #removed for github
        )

        self.transcriber = None

        self.full_transcript = [
            {
                "role":"system", "content":"You are designed to act like JARVIS, ironman's personal AI assistant from the Marvel Movies. Answer in short sentences but act like ironman's assistant JARVIS."
            }]
        print("AI_Assistant initialized")     

# From Assembly API

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        return


    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            print(transcript.text, end="\r\n")
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")


    def on_error(self, error: aai.RealtimeError):
        #print("An error occured:", error)
        return

    def on_close(self, event=None):
        print("Session closed")
        return

    def start_transcription(self):
        print("Starting transcription...")
        try:
            self.transcriber = aai.RealtimeTranscriber(
                sample_rate=16_000,
                on_data=self.on_data,
                on_error=self.on_error,
                on_open=self.on_open,
                on_close=self.on_close,
            )
            self.transcriber.connect()
            print("Transcriber connected")
            microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
            self.transcriber.stream(microphone_stream)
        except Exception as e:
            print("Error starting transcription:", e)

    def close_transcription(self):
        print("Closing transcription...")
        if self.transcriber:
            try:
                self.transcriber.close()
                print("Transcriber closed")
                self.transcriber = None
            except Exception as e:
                print("Error closing transcription:", e)

    def generate_ai_response(self, transcript):
        print("Generating AI response for:", transcript.text)
        self.close_transcription()
        self.full_transcript.append({"role": "user", "content": transcript.text})
        print(f"User: {transcript.text}")

        try:
            # Correctly specify the model using 'model'
            ollama_stream = ollama.chat(
                model="llama3",  # Use the correct argument name
                messages=self.full_transcript,
                stream=True,
            )

            print("Llama 3 response stream started")

            full_text = ""
            for chunk in ollama_stream:
                #access the 'message' key instead of 'messages'
                if 'message' in chunk:
                    full_text += chunk['message']['content']
                
                #check if the response is complete
                if chunk.get('done', False):
                    break
            
            if full_text:
                print("AI response generated:", full_text)
                self.full_transcript.append({"role": "assistant", "content": full_text})
                
                audio_stream = self.client.generate(
                    text=full_text,
                    modal="eleven_turbo_v2",
                    stream=True
                )
                print("Streaming audio...")
                stream(audio_stream)
            else:
                print("No valid AI response was generated.")

        except Exception as e:
            #print("Error generating AI response:", e)
            self.start_transcription()

ai_assistant = AI_Assistant()
ai_assistant.start_transcription()
