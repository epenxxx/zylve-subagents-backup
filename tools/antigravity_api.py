#!/usr/bin/env python3
"""
Antigravity OpenAI-Compatible API Server
Provides /v1/chat/completions and /v1/models endpoints powered directly by Antigravity (agy).
"""

import os
import sys
import time
import json
import uuid
import asyncio
import argparse
from typing import List, Dict, Any, Optional, Union

import uvicorn
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI(
    title="Antigravity API Server",
    description="Standalone OpenAI-compatible API endpoint for Antigravity (Chat Only)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_MODELS = [
    "gemini-3.8-flash-high",
    "gemini-3.8-flash-medium",
    "gemini-3.8-flash-low",
    "gemini-3.7-flash-high",
    "gemini-3.7-flash-medium",
    "gemini-3.7-flash-low",
    "gemini-3.6-flash-high",
    "gemini-3.6-flash-medium",
    "gemini-3.6-flash-low",
    "gemini-3.1-pro-high",
    "gemini-3.1-pro-low",
    "claude-sonnet-4-6",
    "claude-opus-4-6-thinking",
    "gpt-oss-120b-medium",
]

DEFAULT_MODEL = "claude-sonnet-4-6"


class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]], Any]


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = DEFAULT_MODEL
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

    model_config = ConfigDict(extra="allow")


def extract_text_content(content: Union[str, List[Dict[str, Any]], Any]) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(content) if content is not None else ""


def build_chat_prompt(messages: List[ChatMessage]) -> str:
    if len(messages) == 1 and messages[0].role.lower() == "user":
        return extract_text_content(messages[0].content)

    prompt_lines = []
    for msg in messages:
        role = msg.role.lower()
        text = extract_text_content(msg.content).strip()
        if not text:
            continue
        if role in {"system", "developer"}:
            prompt_lines.append(f"Instructions: {text}")
        elif role == "user":
            prompt_lines.append(f"User: {text}")
        elif role == "assistant":
            prompt_lines.append(f"Assistant: {text}")
        else:
            prompt_lines.append(f"{role.capitalize()}: {text}")

    # Prompt completion trigger
    prompt_lines.append("Assistant:")
    return "\n\n".join(prompt_lines)


def resolve_model_name(model_name: Optional[str]) -> str:
    if not model_name:
        return DEFAULT_MODEL
    cleaned = model_name.strip()
    if cleaned.startswith("antigravity/"):
        cleaned = cleaned[len("antigravity/"):]
    elif cleaned.startswith("ag/"):
        cleaned = cleaned[len("ag/"):]

    if cleaned in SUPPORTED_MODELS:
        return cleaned

    # Fuzzy or fallback match
    for m in SUPPORTED_MODELS:
        if m in cleaned or cleaned in m:
            return m

    return DEFAULT_MODEL


@app.get("/")
async def root():
    return {
        "service": "Antigravity API Server",
        "status": "online",
        "version": "1.0.0",
        "endpoints": [
            "/v1/models",
            "/v1/chat/completions"
        ]
    }


@app.get("/v1/models")
@app.get("/models")
async def list_models():
    now = int(time.time())
    models_data = []
    # Add raw models and prefixed models
    for m in SUPPORTED_MODELS:
        models_data.append({
            "id": m,
            "object": "model",
            "created": now,
            "owned_by": "antigravity"
        })
        models_data.append({
            "id": f"antigravity/{m}",
            "object": "model",
            "created": now,
            "owned_by": "antigravity"
        })
        models_data.append({
            "id": f"ag/{m}",
            "object": "model",
            "created": now,
            "owned_by": "antigravity"
        })
    return {
        "object": "list",
        "data": models_data
    }


@app.post("/v1/chat/completions")
@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Messages list cannot be empty"
        )

    resolved_model = resolve_model_name(request.model)
    prompt = build_chat_prompt(request.messages)
    req_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created_ts = int(time.time())

    cmd = [
        "agy",
        "-p", prompt,
        "--model", resolved_model,
        "--disable-slash-commands",
        "--output-format", "stream-json" if request.stream else "json"
    ]

    if not request.stream:
        # Non-streaming response
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute Antigravity CLI: {str(e)}"
            )

        if proc.returncode != 0:
            err_msg = stderr.decode(errors="replace").strip() or "Unknown CLI error"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Antigravity CLI exited with code {proc.returncode}: {err_msg}"
            )

        try:
            result_data = json.loads(stdout.decode())
            response_text = result_data.get("response", "")
            usage_data = result_data.get("usage", {})
            input_tokens = usage_data.get("input_tokens", 0)
            output_tokens = usage_data.get("output_tokens", 0)
        except Exception as e:
            response_text = stdout.decode(errors="replace").strip()
            input_tokens = len(prompt) // 4
            output_tokens = len(response_text) // 4

        return {
            "id": req_id,
            "object": "chat.completion",
            "created": created_ts,
            "model": request.model or resolved_model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }
        }

    # Streaming response (SSE)
    async def sse_generator():
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Send initial role delta
            first_chunk = {
                "id": req_id,
                "object": "chat.completion.chunk",
                "created": created_ts,
                "model": request.model or resolved_model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": ""},
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(first_chunk)}\n\n"

            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                line_str = line.decode(errors="replace").strip()
                if not line_str:
                    continue
                try:
                    event_data = json.loads(line_str)
                    event_type = event_data.get("event")
                    if event_type == "step_update":
                        step = event_data.get("step_update", {})
                        delta_text = step.get("text_delta")
                        if delta_text:
                            chunk = {
                                "id": req_id,
                                "object": "chat.completion.chunk",
                                "created": created_ts,
                                "model": request.model or resolved_model,
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {"content": delta_text},
                                        "finish_reason": None
                                    }
                                ]
                            }
                            yield f"data: {json.dumps(chunk)}\n\n"
                    elif event_type == "result":
                        break
                except Exception:
                    continue

            await proc.wait()

            # Finish chunk
            final_chunk = {
                "id": req_id,
                "object": "chat.completion.chunk",
                "created": created_ts,
                "model": request.model or resolved_model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }
                ]
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            err_chunk = {
                "error": {
                    "message": str(e),
                    "type": "server_error"
                }
            }
            yield f"data: {json.dumps(err_chunk)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream"
    )


def main():
    parser = argparse.ArgumentParser(description="Antigravity OpenAI-compatible API Server")
    parser.add_argument("--host", type=str, default=os.getenv("HOST", "0.0.0.0"), help="Host to bind to")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 8008)), help="Port to listen on")
    args = parser.parse_args()

    print(f"Starting Antigravity API Server on http://{args.host}:{args.port}")
    print(f"Default model: {DEFAULT_MODEL}")
    print(f"Models endpoint: http://{args.host}:{args.port}/v1/models")
    print(f"Chat completions: http://{args.host}:{args.port}/v1/chat/completions")

    uvicorn.run(app, host=args.host, port=args.port, access_log=False)


if __name__ == "__main__":
    main()
