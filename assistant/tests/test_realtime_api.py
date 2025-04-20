# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.realtime_session_create_request import RealtimeSessionCreateRequest  # noqa: F401
from assistant.models.realtime_session_create_response import RealtimeSessionCreateResponse  # noqa: F401
from assistant.models.realtime_transcription_session_create_request import RealtimeTranscriptionSessionCreateRequest  # noqa: F401
from assistant.models.realtime_transcription_session_create_response import RealtimeTranscriptionSessionCreateResponse  # noqa: F401


def test_create_realtime_session(client: TestClient):
    """Test case for create_realtime_session

    Create an ephemeral API token for use in client-side applications with the Realtime API. Can be configured with the same session parameters as the `session.update` client event.  It responds with a session object, plus a `client_secret` key which contains a usable ephemeral API token that can be used to authenticate browser clients for the Realtime API. 
    """
    realtime_session_create_request = {"voice":"ash","instructions":"instructions","input_audio_format":"pcm16","input_audio_noise_reduction":{"type":"near_field"},"input_audio_transcription":{"model":"model","language":"language","prompt":"prompt"},"turn_detection":{"silence_duration_ms":1,"create_response":1,"interrupt_response":1,"prefix_padding_ms":6,"eagerness":"auto","threshold":0.8008281904610115,"type":"server_vad"},"tools":[{"name":"name","description":"description","type":"function","parameters":"{}"},{"name":"name","description":"description","type":"function","parameters":"{}"}],"modalities":["text","text"],"max_response_output_tokens":5,"output_audio_format":"pcm16","temperature":5.962133916683182,"tool_choice":"auto","model":"gpt-4o-realtime-preview"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/realtime/sessions",
    #    headers=headers,
    #    json=realtime_session_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_realtime_transcription_session(client: TestClient):
    """Test case for create_realtime_transcription_session

    Create an ephemeral API token for use in client-side applications with the Realtime API specifically for realtime transcriptions.  Can be configured with the same session parameters as the `transcription_session.update` client event.  It responds with a session object, plus a `client_secret` key which contains a usable ephemeral API token that can be used to authenticate browser clients for the Realtime API. 
    """
    realtime_transcription_session_create_request = {"input_audio_format":"pcm16","include":["include","include"],"modalities":["text","text"],"input_audio_noise_reduction":{"type":"near_field"},"input_audio_transcription":{"model":"gpt-4o-transcribe","language":"language","prompt":"prompt"},"turn_detection":{"silence_duration_ms":1,"create_response":1,"interrupt_response":1,"prefix_padding_ms":6,"eagerness":"auto","threshold":0.8008281904610115,"type":"server_vad"}}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/realtime/transcription_sessions",
    #    headers=headers,
    #    json=realtime_transcription_session_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

