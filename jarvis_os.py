# ==========================================
# 0. MUTE ALL DEVELOPER WARNINGS (MUST BE LINE 1)
# ==========================================
import os
import warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

import pygame
import math
import sys
import random
import threading
import time
import subprocess
import traceback
import sounddevice as sd
import numpy as np
import whisper
import uuid
import requests
import sqlite3
import psutil
import glob
from datetime import datetime
from groq import Groq

# Handle the DuckDuckGo package rename gracefully and silently
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS

# ==========================================
# 1. CONFIGURATION & AI SETUP
# ==========================================
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
groq_client = Groq(api_key=GROQ_API_KEY)

ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY_HERE"
ELEVENLABS_VOICE_ID = "YOUR_ELEVENLABS_VOICE_ID_HERE" 

current_state = "IDLE"  
last_spoken_text = "SYSTEM STANDBY. SAY 'WAKE UP, JARVIS'."

# ==========================================
# 2. UPGRADED SYSTEM & STORE SEARCH CONTROLS
# ==========================================
def execute_system_command(prompt):
    p_lower = prompt.lower()
    user_home = os.path.expanduser("~")
    
    if any(w in p_lower for w in ["play music", "pause music", "stop music", "resume"]):
        os.system("nircmd.exe mediaplay")
        return "Toggling media playback, sir."
    if "mute" in p_lower:
        os.system("nircmd.exe mutesysvolume 2")
        return "Toggling system mute."

    if "downloads" in p_lower:
        downloads_path = os.path.join(user_home, "Downloads")
        os.system(f'explorer "{downloads_path}"')
        return "Opening your Downloads folder, sir."
    if "documents" in p_lower:
        docs_path = os.path.join(user_home, "Documents")
        os.system(f'explorer "{docs_path}"')
        return "Opening your Documents folder, sir."
    if "desktop" in p_lower:
        desktop_path = os.path.join(user_home, "Desktop")
        os.system(f'explorer "{desktop_path}"')
        return "Opening your Desktop folder, sir."

    if "microsoft store" in p_lower or "store" in p_lower:
        try:
            if "instagram" in p_lower:
                subprocess.Popen(["start", "ms-windows-store://search/?query=Instagram"], shell=True)
                return "Opening the Microsoft Store and searching for Instagram, sir."
            elif "search for" in p_lower or "find" in p_lower:
                query = prompt.split("for")[-1].strip() if "for" in p_lower else "apps"
                subprocess.Popen([f"start ms-windows-store://search/?query={query}"], shell=True)
                return f"Searching the Microsoft Store for {query}, sir."
            else:
                subprocess.Popen(["start", "ms-windows-store:"], shell=True)
                return "Opening the Microsoft Store, sir."
        except Exception:
            return "Unable to trigger the Microsoft Store protocol, sir."
            
    if "open brave" in p_lower or "brave browser" in p_lower:
        try:
            brave_paths = [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
            ]
            launched = False
            for path in brave_paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    launched = True
                    break
            if not launched:
                subprocess.Popen(["start", "brave"], shell=True)
            return "Launching Brave browser, sir."
        except Exception as e:
            return f"I encountered an issue launching Brave: {e}"
            
    if "open spotify" in p_lower:
        try:
            subprocess.Popen(["start", "spotify:"], shell=True)
            return "Launching Spotify, sir."
        except Exception:
            return "Unable to trigger Spotify, sir."
            
    if "open code" in p_lower or "visual studio" in p_lower:
        try:
            subprocess.Popen(["code"], shell=True)
            return "Opening Visual Studio Code, sir."
        except Exception:
            return "Unable to open Visual Studio Code, sir."
            
    if "open browser" in p_lower or "chrome" in p_lower:
        try:
            subprocess.Popen(["start", "chrome"], shell=True)
            return "Launching your web browser, sir."
        except Exception:
            return "Unable to launch the browser, sir."
            
    if "bluestacks" in p_lower or "emulator" in p_lower:
        try:
            bs_path = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe"
            if os.path.exists(bs_path):
                os.startfile(bs_path)
            else:
                subprocess.Popen(["start", "bluestacks"], shell=True)
            return "Launching the BlueStacks emulator, sir."
        except Exception:
            return "Failed to start the emulator executable, sir."

    if "open folder" in p_lower or "files" in p_lower or "explorer" in p_lower:
        os.system(f'explorer "{user_home}"')
        return "Opening your user files directory now, sir."
        
    return None

# ==========================================
# 3. BACKGROUND BRAIN & CONTINUOUS LOOP
# ==========================================
def init_memory():
    conn = sqlite3.connect("jarvis_memory.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, role TEXT, content TEXT)")
    conn.commit()
    conn.close()

def fetch_memory(conn):
    c = conn.cursor()
    c.execute("SELECT role, content FROM history ORDER BY id DESC LIMIT 6")
    rows = c.fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def save_memory(conn, role, content):
    c = conn.cursor()
    c.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()

def jarvis_worker():
    global current_state, last_spoken_text
    
    warnings.filterwarnings("ignore")
    init_memory()
    
    print("Loading Whisper ears...")
    model = whisper.load_model("base.en")
    samplerate = 16000

    def generate_speech(text, filename):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2_5", 
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
        except Exception:
            pass

    def speak(text):
        global last_spoken_text
        last_spoken_text = text
        temp_file = f"response_{uuid.uuid4().hex}.mp3"
        generate_speech(text, temp_file)
        
        if os.path.exists(temp_file):
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            try:
                os.remove(temp_file)
            except Exception:
                pass

    def ask_jarvis(prompt):
        local_action_response = execute_system_command(prompt)
        if local_action_response:
            return local_action_response

        conn = sqlite3.connect("jarvis_memory.db")
        live_context = ""
        
        messages = [
            {
                "role": "system", 
                "content": "You are Jarvis, a sophisticated British AI assistant. Speak directly to the user in character with a refined cadence. Keep responses brief, conversational, and direct. Do NOT use tool calls, JSON blocks, or code functions. Always remember past details provided by the user from your conversation history."
            }
        ]
        
        history = fetch_memory(conn)
        messages.extend(history)
        
        prompt_clean = "".join(c if c.isalnum() else " " for c in prompt.lower())
        prompt_words = set(prompt_clean.split())
        
        trigger_words_web = {"weather", "today", "rate", "price", "news", "time", "current"}
        trigger_words_sys = {"system", "cpu", "ram", "hardware", "performance", "specs"}
        
        if trigger_words_web.intersection(prompt_words):
            print("[UPLINK]: Fetching live web data...")
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    with DDGS() as ddgs:
                        res = list(ddgs.text(prompt, max_results=1))
                        if res:
                            live_context += f"\n\n[WEB DATA: {res[0]['body']}]"
            except Exception:
                pass
                
        if trigger_words_sys.intersection(prompt_words):
            print("[DIAGNOSTIC]: Reading hardware telemetry...")
            cpu = psutil.cpu_percent(interval=0.2)
            ram = psutil.virtual_memory().percent
            live_context += f"\n\n[SYSTEM TELEMETRY: CPU usage at {cpu}%, RAM usage at {ram}%]"
            
        user_msg = {"role": "user", "content": prompt + live_context}
        messages.append(user_msg)
        
        try:
            completion = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                max_tokens=200
            )
            response_text = completion.choices[0].message.content
            
            save_memory(conn, "user", prompt)
            save_memory(conn, "assistant", response_text)
            conn.close()
            
            return response_text
        except Exception as e:
            err_trace = traceback.format_exc()
            print(f"\n[CRASH DETECTED]:\n{err_trace}\n")
            conn.close()
            return "I encountered an unhandled exception in my subroutines, sir."

    print("\n=== JARVIS OS ONLINE (CONTINUOUS CONVERSATION MODE) ===")
    
    while True:
        current_state = "IDLE"
        print("[LISTENING FOR WAKE WORD: 'Wake up, Jarvis']...")
        
        audio_chunk = sd.rec(int(3 * samplerate), samplerate=samplerate, channels=1, dtype='float32')
        sd.wait()
        audio_chunk = audio_chunk.flatten()
        
        wake_transcript = model.transcribe(audio_chunk, fp16=False)["text"].strip().lower()
        
        if "wake up" in wake_transcript or "jarvis" in wake_transcript:
            current_state = "SPEAKING"
            speak("At your service, sir. I'm listening.")
            
            while True:
                current_state = "LISTENING"
                print("\n[LISTENING FOR YOUR INSTRUCTION... Speak freely]")
                
                audio_frames = []
                def active_callback(indata, frames, time, status):
                    audio_frames.append(indata.copy())
                
                with sd.InputStream(samplerate=samplerate, channels=1, callback=active_callback):
                    sd.sleep(8000)
                    
                if not audio_frames:
                    continue
                    
                user_audio = np.concatenate(audio_frames, axis=0).flatten().astype(np.float32)
                current_state = "THINKING"
                
                user_transcript = model.transcribe(user_audio, fp16=False)["text"].strip()
                
                if user_transcript:
                    print(f"[{user_transcript}]")
                    if "go to sleep" in user_transcript.lower() or "standby" in user_transcript.lower():
                        current_state = "SPEAKING"
                        speak("Returning to standby mode, sir.")
                        break
                        
                    response = ask_jarvis(user_transcript)
                    current_state = "SPEAKING"
                    speak(response)

brain_thread = threading.Thread(target=jarvis_worker, daemon=True)
brain_thread.start()

# ==========================================
# 4. GRAPHICAL USER INTERFACE (EXPANDED HUD & EQUALIZER)
# ==========================================
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Jarvis OS")

BG_COLOR = (8, 10, 18)
CYAN = (0, 255, 255)
DEEP_BLUE = (0, 100, 255)
RED = (255, 50, 80)
WHITE = (220, 240, 255)

clock = pygame.time.Clock()
time_elapsed = 0

def draw_arc_segments(surface, color, center, radius, width, angle_offset, segments, gap_angle):
    arc_length = (360 / segments) - gap_angle
    if arc_length <= 0: return
    rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
    for i in range(segments):
        start = math.radians(i * (360 / segments) + angle_offset)
        end = math.radians(i * (360 / segments) + arc_length + angle_offset)
        pygame.draw.arc(surface, color, rect, start, end, width)

def draw_ticks(surface, color, center, radius, length, count, offset=0, width=1):
    for i in range(count):
        angle = math.radians((i * (360 / count)) + offset)
        x1 = center[0] + math.cos(angle) * radius
        y1 = center[1] + math.sin(angle) * radius
        x2 = center[0] + math.cos(angle) * (radius + length)
        y2 = center[1] + math.sin(angle) * (radius + length)
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)

def draw_wireframe_globe(surface, color, center, radius, angle_offset):
    pygame.draw.circle(surface, color, center, radius, 1)
    temp_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.ellipse(temp_surf, color, (radius - (radius*0.4), 0, radius * 0.8, radius * 2), 1)
    pygame.draw.ellipse(temp_surf, color, (0, radius - (radius*0.4), radius * 2, radius * 0.8), 1)
    rotated_surf = pygame.transform.rotate(temp_surf, angle_offset)
    surface.blit(rotated_surf, rotated_surf.get_rect(center=center))

def draw_audio_sine_wave(surface, color, center, radius, time_val, active):
    points = []
    num_points = 60
    amplitude = 12 if active else 4
    frequency = 6
    
    for i in range(num_points):
        angle = (i / num_points) * (2 * math.pi)
        wave = math.sin(angle * frequency + (time_val * 0.01)) * amplitude
        r = radius + wave
        x = center[0] + math.cos(angle) * r
        y = center[1] + math.sin(angle) * r
        points.append((x, y))
        
    if len(points) > 2:
        pygame.draw.aalines(surface, color, True, points)

def draw_equalizer(surface, color, center_x, bottom_y, time_val, active):
    num_bars = 24
    bar_width = 8
    spacing = 4
    total_width = num_bars * (bar_width + spacing)
    start_x = center_x - (total_width // 2)
    
    for i in range(num_bars):
        if active:
            height = int(10 + math.sin(i + (time_val * 0.015)) * 25 + random.randint(0, 15))
        else:
            height = int(4 + math.sin(i + (time_val * 0.005)) * 4)
            
        bar_rect = pygame.Rect(start_x + (i * (bar_width + spacing)), bottom_y - height, bar_width, height)
        pygame.draw.rect(surface, color, bar_rect, border_radius=2)

running = True
a_fast, a_med, a_slow = 0.0, 0.0, 0.0
speed_mult = 1.0 

while running:
    dt = clock.tick(60)
    time_elapsed += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    screen.fill(BG_COLOR)
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    parallax_x = (mouse_x - (WIDTH // 2)) * 0.02
    parallax_y = (mouse_y - (HEIGHT // 2)) * 0.02
    center = (int((WIDTH // 2) + parallax_x), int((HEIGHT // 2) + parallax_y))

    if current_state == "LISTENING":
        target_speed = 4.0
        core_color = RED
        pulse = (math.sin(time_elapsed * 0.015) * 0.3) + 1.2
    elif current_state == "THINKING":
        target_speed = 0.5
        core_color = DEEP_BLUE
        pulse = (math.sin(time_elapsed * 0.002) * 0.1) + 0.9
    elif current_state == "SPEAKING":
        target_speed = 2.0
        core_color = CYAN
        pulse = (math.sin(time_elapsed * 0.01) * 0.2) + 1.1
    else:
        target_speed = 1.0
        core_color = CYAN
        pulse = (math.sin(time_elapsed * 0.005) * 0.15) + 1.0

    speed_mult += (target_speed - speed_mult) * 0.05

    a_fast -= 3.0 * speed_mult
    a_med += 1.2 * speed_mult
    a_slow -= 0.4 * speed_mult

    alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(alpha_surf, (*DEEP_BLUE, int(40 * pulse)), center, int(120 * pulse))
    pygame.draw.circle(alpha_surf, (*core_color, int(20 * pulse)), center, int(160 * pulse))
    screen.blit(alpha_surf, (0, 0))

    draw_wireframe_globe(screen, core_color, center, int(45 * pulse), a_slow * 2)
    pygame.draw.circle(screen, WHITE, center, 10, 0)

    is_active = current_state in ["LISTENING", "SPEAKING"]
    draw_audio_sine_wave(screen, core_color, center, int(90 * pulse), time_elapsed, is_active)
    if is_active:
        draw_audio_sine_wave(screen, WHITE, center, int(130 * pulse), -time_elapsed, True)

    draw_arc_segments(screen, core_color, center, 60, 3, a_fast, 3, 40)
    draw_arc_segments(screen, WHITE, center, 75, 1, -a_fast * 1.5, 6, 20)

    draw_arc_segments(screen, DEEP_BLUE, center, 100, 8, a_med, 4, 15)
    draw_ticks(screen, core_color, center, 115, 8, 36, a_slow)
    
    draw_arc_segments(screen, core_color, center, 140, 2, a_slow, 2, 90)
    draw_arc_segments(screen, RED, center, 150, 4, a_fast * 0.8, 12, 25)
    pygame.draw.circle(screen, DEEP_BLUE, center, 180, 1)
    
    pygame.draw.polygon(screen, core_color, [(center[0], center[1] - 190), (center[0] - 12, center[1] - 175), (center[0] + 12, center[1] - 175)], 2)
    pygame.draw.polygon(screen, core_color, [(center[0], center[1] + 190), (center[0] - 12, center[1] + 175), (center[0] + 12, center[1] + 175)], 2)

    # ==========================
    # BOTTOM HUD & EQUALIZER WIDGETS
    # ==========================
    font = pygame.font.SysFont("courier", 12, bold=True)
    
    draw_equalizer(screen, core_color, WIDTH // 2, HEIGHT - 70, time_elapsed, is_active)
    
    radar_center = (80, HEIGHT - 80)
    pygame.draw.circle(screen, DEEP_BLUE, radar_center, 45, 1)
    pygame.draw.circle(screen, core_color, radar_center, 25, 1)
    pygame.draw.circle(screen, core_color, radar_center, 3, 0)
    radar_angle = time_elapsed * 0.003
    rx = radar_center[0] + math.cos(radar_angle) * 45
    ry = radar_center[1] + math.sin(radar_angle) * 45
    pygame.draw.line(screen, core_color, radar_center, (rx, ry), 1)

    sub_bg = pygame.Rect(140, HEIGHT - 45, WIDTH - 280, 30)
    pygame.draw.rect(screen, (12, 18, 32), sub_bg, border_radius=4)
    pygame.draw.rect(screen, core_color, sub_bg, 1, border_radius=4)
    
    sub_text = font.render(f"FEED: {last_spoken_text[:55]}...", True, WHITE)
    screen.blit(sub_text, (sub_bg.x + 10, sub_bg.y + 8))

    cpu_val = psutil.cpu_percent(interval=None)
    ram_val = psutil.virtual_memory().percent
    current_time = datetime.now().strftime("%H:%M:%S")
    
    hud_left = [
        f"SYS.STATE // {current_state}",
        f"CPU LOAD  // {cpu_val}%",
        f"RAM USAGE // {ram_val}%",
        f"UPLINK    // SECURE"
    ]
    
    hud_right = [
        f"TIME      // {current_time}",
        f"AI ENGINE // GROQ-LLM",
        f"VOICE API // ACTIVE",
        f"CORE      // STABLE"
    ]
    
    for idx, text in enumerate(hud_left):
        t_surf = font.render(text, True, core_color)
        screen.blit(t_surf, (20, 20 + (idx * 18)))
        
    for idx, text in enumerate(hud_right):
        t_surf = font.render(text, True, core_color)
        screen.blit(t_surf, (WIDTH - t_surf.get_width() - 20, 20 + (idx * 18)))

    state_surf = font.render(f"STATUS // {current_state}", True, core_color)
    screen.blit(state_surf, (center[0] - state_surf.get_width() // 2, center[1] + 205))

    pygame.display.flip()

pygame.quit()
sys.exit()
