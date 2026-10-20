"""CyberMentor - FREE local server.  Run: python server.py  ->  http://localhost:5000
Providers:  gemini (free API key, online)  |  ollama (100% free, offline)
"""
import os, sys, json, datetime
import requests
from flask import Flask, request, Response, send_from_directory, jsonify

PROVIDER = os.getenv("PROVIDER", "ollama").lower()          # gemini | ollama
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = os.getenv("FAST_MODEL", "gemini-3.5-flash-lite" if PROVIDER == "gemini" else "llama3.2:3b")
OLLAMA = os.getenv("OLLAMA_URL", "http://localhost:11434")
WEB_SEARCH = os.getenv("WEB_SEARCH", "1") == "1"            # Gemini only

if PROVIDER == "gemini" and not GEMINI_KEY:
    sys.exit("Missing GEMINI_API_KEY. Get a FREE key at https://aistudio.google.com/apikey")

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, "curriculum.json"), encoding="utf-8") as f:
    CUR = json.load(f)
DAYS = {d["d"]: d for d in CUR["days"]}

TRUSTED = "\n".join(f"- {i['name']}" + (f" ({i['url']})" if i["url"] else "")
                    for g in CUR["resources"] for i in g["items"])

app = Flask(__name__, static_folder="static")

SYSTEM = """You are "CyberMentor", a personal mentor (Arabic, French, English) for cybersecurity, AI/LLM security, penetration testing and bug bounty hunting.
LANGUAGE: reply in the user's language unless told otherwise. Keep technical terms in English (XSS, SSRF, IDOR...) and explain them briefly the first time.
TEACHING: explain the why, then the how, then a hands-on lab. Use simple analogies, keep answers short, and end with one question to check understanding.
HONESTY: if you are not sure, say so. NEVER invent URLs, commands, CVE numbers or version numbers. Only recommend resources from the TRUSTED list below; you may name other well-known sites without a link.
ETHICS: support only legal, authorized testing (own labs, CTFs, in-scope bug bounty). Refuse attacks on unauthorized targets and malware for harmful use.
TRUSTED RESOURCES:
""" + TRUSTED


def lesson_context(n):
    d = DAYS.get(n)
    if not d:
        return ""
    res = "\n".join(f"- {n_}" + (f": https://{u}" if u else "") for n_, u in d["r"])
    tools = "\n".join(f"- {t}" for t in d.get("tools", []))
    return (f"\n\nTODAY'S LESSON (Day {d['d']} of {len(DAYS)}) | Phase: {d.get('phase','')}\nTopic: {d['t']}\nGoal: {d['g']}\n"
            f"Key concepts: {'; '.join(d['c'])}\nTools to teach:\n{tools}\nHands-on lab: {d['l']}\n"
            f"Resources (use ONLY these links):\n{res}\n\n"
            "HOW TO TEACH THIS LESSON: go in SMALL PARTS and STOP after each part, asking the user to reply 'next' (or ask questions) before continuing. "
            "Part 1: where this fits in the vulnerability-discovery workflow and why it matters. "
            "Part 2: the key concepts, simply, with an analogy. "
            "Part 3: for EACH tool, one at a time: what it is, how it works inside in simple words, when to use it, one beginner command or action to run ONLY on the user's own lab or an in-scope authorized target, how to read the output, and one common mistake. "
            "Part 4: the hands-on lab step by step. "
            "Part 5: a quiz of 3 short questions, one at a time. "
            "Start now with Part 1 only. Never invent options, flags or URLs you are not sure about; say so if unsure.")


def gemini_stream(system, msgs):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:streamGenerateContent?alt=sse"
    body = {"system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "model" if m["role"] == "assistant" else "user",
                          "parts": [{"text": m["content"]}]} for m in msgs]}
    for use_tools in ([True, False] if WEB_SEARCH else [False]):
        b = dict(body)
        if use_tools:
            b["tools"] = [{"google_search": {}}]
        r = requests.post(url, json=b, headers={"x-goog-api-key": GEMINI_KEY}, stream=True, timeout=120)
        r.encoding = "utf-8"
        if r.status_code in (400, 403, 429) and use_tools:
            continue
        if r.status_code != 200:
            hint = " (free-tier limit reached, wait a minute)" if r.status_code == 429 else ""
            yield f"⚠️ Gemini error {r.status_code}{hint}: {r.text[:300]}"
            return
        for line in r.iter_lines(decode_unicode=True):
            if line and line.startswith("data:"):
                try:
                    d = json.loads(line[5:])
                    for p in d["candidates"][0].get("content", {}).get("parts", []):
                        yield p.get("text", "")
                except (KeyError, IndexError, ValueError):
                    pass
        return


def ollama_stream(system, msgs):
    body = {"model": MODEL, "stream": True, "keep_alive": "5m", "options": {"num_ctx": 4096},
            "messages": [{"role": "system", "content": system}] + msgs}
    try:
        r = requests.post(f"{OLLAMA}/api/chat", json=body, stream=True, timeout=600)
    except requests.ConnectionError:
        yield "⚠️ Ollama is not running. Install it from https://ollama.com and start it."
        return
    if r.status_code != 200:
        yield f"⚠️ Ollama error {r.status_code}: {r.text[:300]} (did you run `ollama pull {MODEL}`?)"
        return
    for line in r.iter_lines():
        if line:
            yield json.loads(line).get("message", {}).get("content", "")


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/curriculum")
def curriculum():
    return jsonify(CUR)


@app.post("/api/chat")
def chat():
    data = request.get_json(force=True)
    msgs = data.get("messages", [])[-12:]
    system = SYSTEM + f"\nToday's date: {datetime.date.today().isoformat()}."
    if data.get("day"):
        system += lesson_context(int(data["day"]))
    if data.get("lang", "auto") != "auto":
        system += f"\nAlways reply in {data['lang']}."
    gen = gemini_stream if PROVIDER == "gemini" else ollama_stream

    def stream():
        try:
            yield from gen(system, msgs)
        except Exception as e:
            yield f"\n\n⚠️ Error: {e}"

    return Response(stream(), mimetype="text/plain; charset=utf-8",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    print(f"CyberMentor on http://localhost:5000 | provider={PROVIDER} | model={MODEL} | lessons={len(DAYS)}")
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", 5000)), debug=False, threaded=True)
