import os
import struct
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TTSGenerator:
    def __init__(self, model_name="gemini-2.5-flash-preview-tts"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def _parse_audio_mime_type(self, mime_type: str) -> dict:
        """Parses bits per sample and rate from an audio MIME type string."""
        bits_per_sample = 16
        rate = 24000

        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass

        return {"bits_per_sample": bits_per_sample, "rate": rate}

    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """Generates a WAV file header and prepends it to the audio data."""
        parameters = self._parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            chunk_size,
            b"WAVE",
            b"fmt ",
            16,
            1,
            num_channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b"data",
            data_size
        )
        return header + audio_data

    def generate_audio(self, text, voice_name="Zephyr"):
        """
        Generates audio from text and returns it as bytes.
        """
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=text),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            ),
        )

        all_audio_data = b""
        mime_type = None

        try:
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=generate_content_config,
            ):
                if (chunk.candidates and 
                    chunk.candidates[0].content and 
                    chunk.candidates[0].content.parts):
                    
                    part = chunk.candidates[0].content.parts[0]
                    
                    if part.inline_data and part.inline_data.data:
                        all_audio_data += part.inline_data.data
                        # Capture mime_type from the first chunk that has it
                        if not mime_type:
                            mime_type = part.inline_data.mime_type

            if all_audio_data:
                if mime_type and "wav" not in mime_type:
                     final_audio = self._convert_to_wav(all_audio_data, mime_type if mime_type else "audio/L16;rate=24000")
                else:
                     final_audio = all_audio_data

                return final_audio
            else:
                raise RuntimeError("No audio data received from TTS service.")

        except Exception as e:
            raise RuntimeError(f"Error during TTS generation: {e}")

if __name__ == "__main__":
    # Test the TTS Generator
    tts = TTSGenerator()
    test_text = "Привет! Как дела?"
    try:
        audio = tts.generate_audio(test_text)
        print(f"Generated {len(audio)} bytes of audio.")
    except Exception as e:
        print(e)
