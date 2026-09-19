#!/usr/bin/env python3
"""
antigravity_bridge_daemon.py
Bridge lokal untuk Antigravity (agy CLI) dengan fungsi AGENTIC PENUH.
Menerima request Gemini REST API / OpenAI API dari agy di http://127.0.0.1:8085
dan meneruskannya ke OpenAI-compatible endpoint di http://40.50.60.2:20128/v1
dengan menyuntikkan Bearer API Key, menerjemahkan payload/SSE stream
TERMASUK function-calling/tools, dan mendukung pemilihan bebas model.
"""
import sys
import json
import re
import os
import time
import uuid
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

TARGET_URL = os.environ.get("ANTIGRAVITY_TARGET_URL", "http://40.50.60.2:20128/v1")
API_KEY = os.environ.get("ANTIGRAVITY_API_KEY", "sk-58cfc75c95fa1662-n3z136-0e8b36e4")
PORT = int(os.environ.get("ANTIGRAVITY_BRIDGE_PORT", "8085"))
LOG_REQ = os.environ.get("ANTIGRAVITY_LOG_REQUESTS", "1") == "1"

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

_cached_models = []
_last_fetch_time = 0

def fetch_available_models():
    global _cached_models, _last_fetch_time
    now = time.time()
    if _cached_models and (now - _last_fetch_time < 120):
        return _cached_models
    try:
        r = requests.get(f"{TARGET_URL}/models", headers={"Authorization": f"Bearer {API_KEY}"}, timeout=5)
        if r.status_code == 200:
            data = r.json().get("data", [])
            _cached_models = [m["id"] for m in data if "id" in m]
            _last_fetch_time = now
    except Exception:
        pass
    return _cached_models

def log_debug(msg, obj=None):
    if not LOG_REQ:
        return
    try:
        with open("/tmp/antigravity_bridge.log", "a") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            if obj is not None:
                f.write(json.dumps(obj)[:4000] + "\n")
    except Exception:
        pass

# ---------- Gemini -> OpenAI translation ----------

def normalize_json_schema(obj):
    """Normalize Gemini uppercase types to standard lowercase JSON schema."""
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if k == "type" and isinstance(v, str):
                new_dict[k] = v.lower()
            else:
                new_dict[k] = normalize_json_schema(v)
        return new_dict
    elif isinstance(obj, list):
        return [normalize_json_schema(item) for item in obj]
    return obj

def gemini_tools_to_openai(gemini_tools):
    """[{"functionDeclarations":[{name,description,parameters}]}] -> OpenAI tools list."""
    out = []
    if not gemini_tools:
        return out
    for t in gemini_tools:
        decls = t.get("functionDeclarations") or t.get("function_declarations") or []
        for d in decls:
            name = d.get("name", "")
            if not name:
                continue
            raw_params = d.get("parameters") or {"type": "object", "properties": {}}
            params = normalize_json_schema(raw_params)
            out.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": d.get("description", ""),
                    "parameters": params,
                },
            })
    return out

def gemini_contents_to_openai_messages(contents, system_parts=None):
    """
    Returns (messages, tool_id_map).
    Handles text, functionCall (assistant tool_calls), functionResponse (tool msgs).
    """
    messages = []
    if system_parts:
        sys_text = "\n".join(
            p.get("text", "") for p in system_parts
            if isinstance(p, dict) and p.get("text")
        ).strip()
        if sys_text:
            messages.append({"role": "system", "content": sys_text})

    tool_id_map = {}  # func name -> last tool_call id
    call_counter = [0]

    def new_id(name):
        call_counter[0] += 1
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", name)[:40]
        return f"call_{safe}_{call_counter[0]}"

    for item in (contents or []):
        role = item.get("role", "user")
        parts = item.get("parts", [])
        texts = []
        func_calls = []
        func_resps = []
        for p in parts:
            if not isinstance(p, dict):
                continue
            if "text" in p and isinstance(p["text"], str):
                texts.append(p["text"])
            elif "functionCall" in p or "functioncall" in p:
                fc = p.get("functionCall", p.get("functioncall", {}))
                func_calls.append(fc)
            elif "functionResponse" in p or "functionresponse" in p:
                fr = p.get("functionResponse", p.get("functionresponse", {}))
                func_resps.append(fr)
            # inlineData / others: skip

        text_joined = "\n".join(texts).strip()

        if func_resps:
            # tool result messages (role tool). Gemini bundles them under user role.
            if text_joined:
                messages.append({"role": "user", "content": text_joined})
            for fr in func_resps:
                fname = fr.get("name", "tool")
                resp = fr.get("response", {})
                tid = tool_id_map.get(fname)
                if not tid:
                    tid = new_id(fname)
                    tool_id_map[fname] = tid
                messages.append({
                    "role": "tool",
                    "tool_call_id": tid,
                    "name": fname,
                    "content": json.dumps(resp) if not isinstance(resp, str) else resp,
                })
            continue

        if func_calls:
            # assistant message with tool_calls
            tool_calls = []
            for fc in func_calls:
                fname = fc.get("name", "")
                args = fc.get("args", {})
                tid = new_id(fname)
                tool_id_map[fname] = tid
                tool_calls.append({
                    "id": tid,
                    "type": "function",
                    "function": {
                        "name": fname,
                        "arguments": json.dumps(args) if not isinstance(args, str) else args,
                    },
                })
            msg = {"role": "assistant", "content": text_joined or None,
                   "tool_calls": tool_calls}
            messages.append(msg)
            continue

        # plain text
        if role == "model":
            messages.append({"role": "assistant", "content": text_joined})
        else:
            messages.append({"role": "user", "content": text_joined})

    # OpenAI disallows content=None alongside tool_calls in some backends; normalize
    for m in messages:
        if m.get("content") is None:
            m["content"] = ""
    # drop empty leading/trailing empties but keep at least 1
    messages = [m for m in messages if (m.get("content") or m.get("tool_calls"))]
    if not messages:
        messages = [{"role": "user", "content": "hello"}]
    return messages, tool_id_map


class BridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path in ["/", "/health"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "service": "antigravity-bridge"}')
            return

        # Gemini ListModels -> sajikan daftar model remote dalam format Gemini
        if "models" in self.path and ("v1beta" in self.path or "v1/" in self.path or self.path.startswith("/models")):
            try:
                r = requests.get(f"{TARGET_URL}/models",
                                 headers={"Authorization": f"Bearer {API_KEY}"}, timeout=15)
                ids = [m["id"] for m in r.json().get("data", [])] if r.status_code == 200 else []
            except Exception:
                ids = []
            gem_list = {"models": [
                {"name": f"models/{mid}",
                 "displayName": mid,
                 "supportedGenerationMethods": ["generateContent", "streamGenerateContent"]}
                for mid in ids
            ]}
            body = json.dumps(gem_list).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        url = f"{TARGET_URL}{self.path if self.path.startswith('/v1') else '/v1' + self.path}"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        try:
            r = requests.get(url, headers=headers, timeout=30)
            self.send_response(r.status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(r.content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_POST(self):
        len_ = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(len_)
        try:
            req_body = json.loads(body_bytes.decode("utf-8")) if len_ > 0 else {}
        except Exception:
            req_body = {}

        if ":streamGenerateContent" in self.path or ":generateContent" in self.path:
            is_stream = ":streamGenerateContent" in self.path
            self.handle_gemini_request(req_body, is_stream)
        else:
            self.handle_openai_request(body_bytes)

    # ----- Gemini handler -----
    def handle_gemini_request(self, req_body, is_stream):
        model_match = re.search(r"/models/([^:]+):", self.path)
        model_name = model_match.group(1) if model_match else "ag/gemini-3.8-flash-medium"
        target_model = self.resolve_model(model_name)
        log_debug(f"GEMINI model_in_path={model_name} -> {target_model} stream={is_stream}",
                  {"tools_n": len(req_body.get("tools", [])), "contents_n": len(req_body.get("contents", []))})

        sys_parts = (req_body.get("systemInstruction") or {}).get("parts", [])
        messages, _ = gemini_contents_to_openai_messages(req_body.get("contents", []), sys_parts)
        oai_tools = gemini_tools_to_openai(req_body.get("tools"))

        gen_config = req_body.get("generationConfig", {}) or {}
        openai_req = {"model": target_model, "messages": messages, "stream": is_stream}
        if gen_config.get("temperature") is not None:
            openai_req["temperature"] = gen_config["temperature"]
        if gen_config.get("maxOutputTokens") is not None:
            openai_req["max_tokens"] = gen_config["maxOutputTokens"]
        if oai_tools:
            openai_req["tools"] = oai_tools
            openai_req["tool_choice"] = "auto"

        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        try:
            if is_stream:
                self.serve_gemini_stream(openai_req, headers, target_model)
            else:
                self.serve_gemini_oneshot(openai_req, headers, target_model)
        except BrokenPipeError:
            pass
        except Exception as e:
            try:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
            except Exception:
                pass

    def serve_gemini_stream(self, openai_req, headers, target_model):
        try:
            res = requests.post(f"{TARGET_URL}/chat/completions", json=openai_req,
                                headers=headers, stream=True, timeout=300)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
            return

        if res.status_code != 200:
            err_text = res.text[:800]
            log_debug(f"Upstream error {res.status_code}: {err_text}")
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            err_cand = {
                "candidates": [{
                    "content": {"parts": [{"text": f"⚠️ [Model Provider Error HTTP {res.status_code}]: {err_text}"}], "role": "model"},
                    "finishReason": "STOP",
                    "index": 0
                }]
            }
            self.wfile.write(f"data: {json.dumps(err_cand)}\n\n".encode())
            self.wfile.flush()
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        prompt_tokens = 0
        completion_tokens = 0
        # accumulate tool call fragments: index -> {id, name, args_str}
        tc_acc = {}

        def emit_chunk(parts, finish=None):
            cand = {"content": {"parts": parts, "role": "model"}, "index": 0}
            if finish:
                cand["finishReason"] = finish
                cand_chunk = {"candidates": [cand],
                              "usageMetadata": {
                                  "promptTokenCount": prompt_tokens or 10,
                                  "candidatesTokenCount": completion_tokens or 10,
                                  "totalTokenCount": (prompt_tokens + completion_tokens) or 20}}
            else:
                cand_chunk = {"candidates": [cand]}
            try:
                self.wfile.write(f"data: {json.dumps(cand_chunk)}\n\n".encode())
                self.wfile.flush()
            except BrokenPipeError:
                raise

        def emit_gemini_text(text):
            if not text:
                return
            emit_chunk([{"text": text}])

        def emit_gemini_toolcalls():
            if not tc_acc:
                return
            parts = []
            for idx in sorted(tc_acc):
                e = tc_acc[idx]
                if not e.get("name"):
                    continue
                try:
                    args = json.loads(e.get("arguments", "") or "{}")
                except Exception:
                    args = {"_raw": e.get("arguments", "")}
                parts.append({"functionCall": {"name": e.get("name", ""), "args": args}})
            if parts:
                emit_chunk(parts, finish="STOP")

        for line in res.iter_lines():
            if not line:
                continue
            try:
                line_str = line.decode("utf-8")
            except Exception:
                continue
            if not line_str.startswith("data: "):
                continue
            data_str = line_str[6:].strip()
            if data_str == "[DONE]":
                break
            try:
                ev = json.loads(data_str)
            except Exception:
                continue
            usage = ev.get("usage")
            if usage:
                prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
                completion_tokens = usage.get("completion_tokens", completion_tokens)
            for ch in ev.get("choices", []):
                delta = ch.get("delta", {})
                # text (content only; reasoning_content diabaikan biar tidak mengotori tool-call)
                c = delta.get("content")
                if c:
                    emit_gemini_text(c)
                # tool calls fragments
                for tc in (delta.get("tool_calls") or []):
                    idx = tc.get("index", 0)
                    acc = tc_acc.setdefault(idx, {"id": "", "name": "", "arguments": ""})
                    if tc.get("id"):
                        acc["id"] = tc["id"]
                    fn = tc.get("function", {}) or {}
                    if fn.get("name"):
                        acc["name"] = fn["name"]
                    if fn.get("arguments"):
                        acc["arguments"] += fn["arguments"]
                fr = ch.get("finish_reason")
                if fr == "tool_calls":
                    emit_gemini_toolcalls()
                    tc_acc = {}
                elif fr:
                    # upstream selesai (stop/length): tutup dengan STOP + teks kosong
                    emit_chunk([{"text": ""}], finish="STOP")

    def serve_gemini_oneshot(self, openai_req, headers, target_model):
        openai_req["stream"] = False
        try:
            res = requests.post(f"{TARGET_URL}/chat/completions", json=openai_req,
                                headers=headers, timeout=300)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
            return

        if res.status_code != 200:
            err_text = res.text[:800]
            log_debug(f"Upstream oneshot error {res.status_code}: {err_text}")
            out = {
                "candidates": [{
                    "content": {"parts": [{"text": f"⚠️ [Model Provider Error HTTP {res.status_code}]: {err_text}"}], "role": "model"},
                    "finishReason": "STOP",
                    "index": 0
                }],
                "modelVersion": target_model,
                "responseId": "err"
            }
            body = json.dumps(out).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            return

        try:
            data = res.json()
        except Exception:
            data = {}

        ch = (data.get("choices") or [{}])[0]
        msg = ch.get("message", {})
        parts = []
        if msg.get("content"):
            parts.append({"text": msg["content"]})
        for tc in (msg.get("tool_calls") or []):
            fn = tc.get("function", {})
            try:
                args = json.loads(fn.get("arguments", "") or "{}")
            except Exception:
                args = {"_raw": fn.get("arguments", "")}
            parts.append({"functionCall": {"name": fn.get("name", ""), "args": args}})
        usage = data.get("usage", {})
        out = {"candidates": [{"content": {"parts": parts, "role": "model"},
                               "finishReason": "STOP", "index": 0}],
               "usageMetadata": {"promptTokenCount": usage.get("prompt_tokens", 0),
                                 "candidatesTokenCount": usage.get("completion_tokens", 0),
                                 "totalTokenCount": usage.get("total_tokens", 0)},
               "modelVersion": target_model, "responseId": data.get("id", "")}
        body = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def handle_openai_request(self, body_bytes):
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        url = f"{TARGET_URL}{self.path if self.path.startswith('/v1') else '/v1' + self.path}"
        try:
            r = requests.post(url, data=body_bytes, headers=headers, stream=True, timeout=300)
            self.send_response(r.status_code)
            for k, v in r.headers.items():
                if k.lower() not in ["content-encoding", "transfer-encoding"]:
                    self.send_header(k, v)
            self.end_headers()
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except BrokenPipeError:
            pass
        except Exception as e:
            try:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
            except Exception:
                pass

    def resolve_model(self, m):
        env_override = os.environ.get("ANTIGRAVITY_MODEL_OVERRIDE") or os.environ.get("TARGET_MODEL")
        if env_override:
            return env_override

        models = fetch_available_models()

        # 1. Jika model persis ada di upstream (termasuk combo FREE atau Gemini), hormati pilihan user 1:1!
        if m in models:
            return m

        m_lower = m.lower()

        # model internal agy untuk judul percakapan -> model cepat yang valid
        if "flash-lite" in m_lower or "lite-preview" in m_lower:
            return "ag/gemini-3.8-flash-medium"

        for candidate in ["ag/", "kc/", "openrouter/", "gemini/"]:
            if (candidate + m) in models:
                return candidate + m

        for available in models:
            if available in ("FREE", "Gemini"):
                continue
            if m_lower in available.lower() or available.lower() in m_lower:
                return available

        if m.startswith("gemini-"):
            return f"ag/{m}"
        if m.startswith("claude-"):
            return f"ag/{m}"
        if "opus" in m_lower:
            return "ag/claude-opus-4-6-thinking"
        if "claude" in m_lower or "sonnet" in m_lower:
            return "ag/claude-sonnet-4-6"
        if "gpt" in m_lower:
            return "ag/gpt-oss-120b-medium"
        if "kilo" in m_lower:
            return "kc/kilo-auto/free"

        return "ag/gemini-3.8-flash-medium"

def run():
    fetch_available_models()
    server = ThreadedHTTPServer(("127.0.0.1", PORT), BridgeHandler)
    print(f"[*] Antigravity Bridge Daemon running on http://127.0.0.1:{PORT}")
    print(f"[*] Target Remote: {TARGET_URL}")
    server.serve_forever()

if __name__ == "__main__":
    run()
