
import pyttsx3
import datetime
import time
import random
import csv
import os
import sys

USE_MIC       = "--mic"     in sys.argv
FORCE_HINDI   = "--hindi"   in sys.argv
FORCE_ENGLISH = "--english" in sys.argv
TEST_VOICE    = "--test"    in sys.argv


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


AGENCY_CONFIG = {
    "name":         "Škoda Noida Sector 18 Showroom",
    "address":      "Plot 17, Sector 18, Noida, Uttar Pradesh 201301",
    "google_maps":  "https://maps.google.com/?q=Skoda+Showroom+Sector+18+Noida",
    "open_time":    "9:00 AM",
    "close_time":   "6:00 PM",
    "off_days":     ["Sunday"],
    "phone":        "+91-120-4567890",
    "website":      "https://www.skoda-auto.in",
}


PUBLIC_HOLIDAYS = {
    "2026-01-01": "New Year's Day",
    "2026-01-14": "Makar Sankranti",
    "2026-01-26": "Republic Day",
    "2026-03-20": "Holi",
    "2026-04-02": "Good Friday",
    "2026-04-14": "Dr. Ambedkar Jayanti",
    "2026-04-29": "Ram Navami",
    "2026-05-12": "Buddha Purnima",
    "2026-07-06": "Eid ul-Adha",
    "2026-08-15": "Independence Day",
    "2026-08-19": "Janmashtami",
    "2026-09-17": "Ganesh Chaturthi",
    "2026-10-02": "Gandhi Jayanti",
    "2026-10-20": "Dussehra",
    "2026-11-09": "Diwali",
    "2026-11-11": "Bhai Dooj",
    "2026-12-25": "Christmas",
}



def now():
    """Always returns the actual current datetime — never hardcoded."""
    return datetime.datetime.now()


def get_time_greeting():
    h = now().hour
    if   h < 12: return "Good morning"
    elif h < 17: return "Good afternoon"
    else:        return "Good evening"


def get_current_time_str():
    """e.g. 10:30 AM"""
    return now().strftime("%I:%M %p")


def get_current_date_str():
    """e.g. Saturday, 23 May 2026"""
    return now().strftime("%A, %d %B %Y")


def get_day_name():
    return now().strftime("%A")


def is_agency_open_now():
    """
    Returns (is_open: bool, reason: str)
    Checks real current time against agency hours.
    """
    today     = now()
    day_name  = today.strftime("%A")
    date_key  = today.strftime("%Y-%m-%d")
    cur_hour  = today.hour
    cur_min   = today.minute

    # Sunday check
    if day_name in AGENCY_CONFIG["off_days"]:
        return False, f"Sunday — showroom is closed on Sundays"

    # Holiday check
    if date_key in PUBLIC_HOLIDAYS:
        return False, f"public holiday ({PUBLIC_HOLIDAYS[date_key]})"

    # Time check (10 AM to 7 PM)
    open_h, close_h = 10, 19
    if cur_hour < open_h:
        return False, f"not yet open — opens at {AGENCY_CONFIG['open_time']} today"
    if cur_hour >= close_h:
        return False, f"closed for today — opens tomorrow at {AGENCY_CONFIG['open_time']}"

    return True, "open"


def get_visit_timing_answer():
    """
    Answers 'when can I visit' with REAL current time awareness.
    This is the fix for the timing question bug.
    """
    is_open, reason = is_agency_open_now()
    today     = now()
    day_name  = today.strftime("%A")
    date_str  = get_current_date_str()
    cur_time  = get_current_time_str()

    if is_open:
        return (
            f"Great news! The showroom is open right now. "
            f"Today is {date_str} and the current time is {cur_time}. "
            f"The showroom is open until {AGENCY_CONFIG['close_time']} today. "
            f"You can head over right now and our team will be happy to assist you. "
            f"The address is {AGENCY_CONFIG['address']}."
        )
    else:
        
        next_day = today + datetime.timedelta(days=1)
        for _ in range(7):
            next_key  = next_day.strftime("%Y-%m-%d")
            next_dname = next_day.strftime("%A")
            if next_dname not in AGENCY_CONFIG["off_days"] and next_key not in PUBLIC_HOLIDAYS:
                break
            next_day += datetime.timedelta(days=1)

        next_label = "tomorrow" if (next_day - today).days == 1 else next_day.strftime("%A, %d %B")

        return (
            f"Today is {date_str} and currently the showroom is {reason}. "
            f"Our showroom is open Monday to Saturday, "
            f"from {AGENCY_CONFIG['open_time']} to {AGENCY_CONFIG['close_time']}. "
            f"Your next available visit would be {next_label} from {AGENCY_CONFIG['open_time']}. "
            f"The address is {AGENCY_CONFIG['address']}."
        )


VOICE_INDEX  = 0     
SPEECH_RATE  = 150    
SPEECH_VOL   = 1.0


def _make_engine():
    """Fresh engine every call — Python 3.11 threading fix."""
    eng = pyttsx3.init('sapi5')
    vs  = eng.getProperty('voices')
    idx = VOICE_INDEX if len(vs) > VOICE_INDEX else 0
    eng.setProperty('voice',  vs[idx].id)
    eng.setProperty('rate',   SPEECH_RATE)
    eng.setProperty('volume', SPEECH_VOL)
    return eng


def _say(text):
    """Speak one sentence. Print to terminal. Fresh engine each time."""
    print(f"\n  🤖 SKODA : {text}")
    try:
        eng = _make_engine()
        eng.say(text)
        eng.runAndWait()
        eng.stop()
        del eng
    except Exception as e:
        print(f"  [VOICE ERROR] {e} — text shown above")


def speak(text, post_pause=0.4):
    """
    Split on sentences. Speak each with a breath gap.
    Makes the bot sound human — not a wall of text.
    Apostrophes removed from contractions for cleaner TTS.
    """
    clean     = text.replace("'", "").replace("'", "")
    raw       = clean.replace('!', '.').replace('?', '.')
    sentences = [s.strip() for s in raw.split('.') if s.strip()]
    q_words   = ["could","would","shall","can","do you","are you",
                 "is there","what","which","how","when","where","shall"]

    for i, sent in enumerate(sentences):
        punct = "?" if any(sent.lower().startswith(w) for w in q_words) else "."
        _say(sent + punct)
        if i < len(sentences) - 1:
            time.sleep(0.38)
    time.sleep(post_pause)


def pause(dur=0.38):
    time.sleep(dur)


#  Voice test 
if TEST_VOICE:
    print("\n  Running voice test...\n")
    _say("This is your Skoda Voice Assistant calling from the Skoda India team.")
    time.sleep(0.3)
    _say("Voice test two. If you heard both lines, voice is working perfectly.")
    print("\n  Done. If both lines were spoken, run the bot normally.\n")
    sys.exit(0)



ACK_POSITIVE = ["Wonderful!", "That is great!", "Absolutely!", "Perfect!",
                "Excellent!", "Fantastic!", "Of course!", "Brilliant!"]
ACK_NEUTRAL  = ["Sure, let me help you with that.",
                "Happy to share that with you.",
                "Great question, let me explain.",
                "I would be happy to help.",
                "Absolutely, here is what you need to know."]
ACK_EMPATHY  = ["I completely understand.",
                "That makes total sense.",
                "I hear you.",
                "That is a really good point."]
FOLLOW_UP_QS = [
    "Is there anything else on your mind?",
    "Any other questions I can help with?",
    "What else can I tell you about our Skoda range?",
    "Anything else before we wrap up?",
]
DONE_WORDS   = ["no","nothing","done","nahi","nahin","theek hai",
                "not now","im good","no more","bas","bye","quit","exit","that is all"]
YES_WORDS    = ["yes","sure","ok","okay","please","go ahead","haan","ha",
                "bilkul","zaroor","why not","sounds good","confirm","book"]


def ack(style="positive"):
    if style == "positive": phrase = random.choice(ACK_POSITIVE)
    elif style == "empathy": phrase = random.choice(ACK_EMPATHY)
    else: phrase = random.choice(ACK_NEUTRAL)
    _say(phrase)
    pause(0.35)



NORTH_EAST_STATES = [
    "uttar pradesh","up","delhi","new delhi","haryana","punjab",
    "rajasthan","himachal pradesh","uttarakhand","bihar","jharkhand",
    "west bengal","assam","odisha","madhya pradesh","chhattisgarh",
    "arunachal pradesh","manipur","meghalaya","mizoram","nagaland",
    "sikkim","tripura","chandigarh","jammu","kashmir","ladakh",
]


def get_language(state):
    if FORCE_HINDI:   return "hindi"
    if FORCE_ENGLISH: return "english"
    return "hindi" if any(ns in state.lower() for ns in NORTH_EAST_STATES) else "english"



FAQ = {
    "affordable": (
        "Great news on that front. "
        "The Kylaq is Skoda most affordable car in India, starting at just 7 lakh 59 thousand rupees. "
        "It is a compact SUV with premium features at a really accessible price point. "
        "Incredible value for what you get."
    ),
    "safe": (
        "Safety is honestly one of Skoda biggest strengths in India. "
        "The Kushaq, Slavia, and the brand-new Kylaq have all received perfect 5-star ratings "
        "under both Global NCAP and Bharat NCAP crash tests. "
        "You and your family are in very safe hands."
    ),
    "warranty": (
        "Skoda gives you a very generous 4-year or 1 lakh kilometre warranty on every new car, "
        "whichever comes first. "
        "And the good news is you can extend it even further if you would like extra peace of mind. "
        "It is one of the best warranty packages in the segment."
    ),
    "diesel": (
        "That is a common question. "
        "Skoda discontinued diesel engines in India after the BS6 emission norms came in. "
        "All current models now run on turbo-petrol TSI engines, "
        "which are quite punchy and surprisingly fuel efficient."
    ),
    "city_mileage": (
        "In heavy city traffic you can expect around 6 to 9 kilometres per litre "
        "from Skoda TSI engines. "
        "That is pretty standard for a modern turbo-petrol in dense city conditions."
    ),
    "highway_mileage": (
        "On the open highway the mileage improves quite noticeably. "
        "You are looking at 16 to 19 kilometres per litre. "
        "The 1.5 litre models even have Active Cylinder Technology "
        "which shuts off two cylinders at cruise speed to save fuel."
    ),
    "service_cost": (
        "Servicing a Skoda is quite affordable, which surprises a lot of people. "
        "For popular models like the Kushaq or Slavia, "
        "the routine annual service typically comes to around 7 thousand to 9 thousand rupees. "
        "Very reasonable for a European brand."
    ),
    "supercare": (
        "Skoda SuperCare is their pre-paid maintenance plan. "
        "You pay upfront today and lock in the current cost of parts and labour "
        "for your future services. "
        "So even if prices go up in two or three years, you are fully protected."
    ),
    "dsg": (
        "The 7-speed DSG is fantastic for highway driving. "
        "But if you are mostly driving in heavy city traffic every day, "
        "the 6-speed torque converter automatic is actually a better choice. "
        "It handles stop and go traffic more smoothly."
    ),
    "epc": (
        "That EPC warning light issue was a known concern with some older models, "
        "but Skoda has fully resolved it now. "
        "They replaced the fuel pumps with more robust components "
        "that handle varying Indian fuel quality much better."
    ),
    "visit_timing": "",   # handled dynamically by get_visit_timing_answer()
}

FAQ_KEYWORDS = {
    "visit_timing":    ["visit","when can i come","open","timing","hours","time to visit",
                        "what time","showroom time","can i come","when to visit","today open",
                        "opening time","closing time","come today","visit today"],
    "affordable":      ["cheap","affordable","price","cost","budget","kylaq","starting","lowest","kitna"],
    "safe":            ["safe","safety","ncap","crash","rating","stars","secure","suraksha"],
    "warranty":        ["warranty","guarantee","coverage","waranti"],
    "diesel":          ["diesel","bs6","fuel type"],
    "city_mileage":    ["city mileage","city fuel","traffic","urban","kmpl","mileage in city"],
    "highway_mileage": ["highway","long drive","road trip","highway mileage","highway fuel"],
    "service_cost":    ["service","maintenance","annual service","servicing","service cost"],
    "supercare":       ["supercare","super care","maintenance plan","prepaid"],
    "dsg":             ["dsg","automatic","gearbox","transmission","gear"],
    "epc":             ["epc","engine light","dashboard","warning light"],
}

CAR_RECS = {
    "suv":       ("the Skoda Kushaq or the brand-new Kylaq",
                  "Both are brilliant compact SUVs with excellent safety ratings and strong resale value."),
    "compact":   ("the Skoda Kylaq",
                  "Our newest and most affordable model, starting at just 7.59 lakh."),
    "sedan":     ("the Skoda Slavia",
                  "A beautifully designed turbo-petrol sedan with a very premium interior feel."),
    "family":    ("the Skoda Kodiaq or the Superb",
                  "Both offer generous cabin space and are perfect for long family road trips."),
    "budget":    ("the Skoda Kylaq",
                  "Starting at 7.59 lakh, it is the most value-packed car in our range right now."),
    "luxury":    ("the Skoda Superb",
                  "Our flagship sedan. It has a truly first-class interior."),
    "automatic": ("the Skoda Slavia or Kushaq with the DSG automatic",
                  "Smooth, fast gear changes. You will love it in the city and on highways."),
    "petrol":    ("the Skoda Kushaq 1.0 TSI",
                  "Very fuel efficient, peppy in traffic, and a joy on the highway."),
}


def match_faq(query):
    q = query.lower()
    for key, kws in FAQ_KEYWORDS.items():
        if any(kw in q for kw in kws):
            if key == "visit_timing":
                return get_visit_timing_answer()   # real-time answer
            return FAQ[key]
    return None


def recommend_car(interest):
    i = interest.lower()
    for key, (car, reason) in CAR_RECS.items():
        if key in i:
            return f"Based on what you are looking for, I would highly recommend {car}. {reason}"
    return (
        "We have a really exciting range right now. "
        "The Kylaq compact SUV starts at just 7.59 lakh and is incredibly popular. "
        "The Kushaq and Slavia are our bestsellers in the mid range. "
        "And the Superb is our flagship for those who want something truly premium. "
        "Which of these sounds most interesting to you?"
    )



SILENT_FALLBACK = (
    "I am sorry, I could not hear anything. "
    "You can type your message below and I will help you right away."
)


def get_input(timeout_msg=True):
    """
    Demo mode: waits for keyboard input.
    Mic mode:  listens via microphone with graceful fallback.
    """
    if USE_MIC:
        result = _listen_mic()
        if result in ("timeout", "unclear", "error"):
            if timeout_msg:
                _say(SILENT_FALLBACK)
                pause(0.5)
                print(f"  👤 TYPE  : ", end="", flush=True)
                try:
                    typed = input("").strip().lower()
                    return typed if typed else "timeout"
                except EOFError:
                    return "timeout"
        return result
    else:
        print(f"  👤 YOU   : ", end="", flush=True)
        try:
            text = input("").strip().lower()
        except EOFError:
            text = ""
        return text if text else "timeout"


def _listen_mic(timeout=8, phrase_limit=10):
    try:
        import speech_recognition as sr
    except ImportError:
        print("  [ERROR] pip install SpeechRecognition pyaudio")
        return "error"
    r = sr.Recognizer()
    r.energy_threshold         = 300
    r.dynamic_energy_threshold = True
    r.pause_threshold          = 0.85
    with sr.Microphone() as source:
        print("\n  🎤 [Listening...]")
        r.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        except Exception:
            return "timeout"
    try:
        query = r.recognize_google(audio, language='en-IN')
        print(f"  👤 YOU   : {query}")
        return query.lower().strip()
    except Exception:
        return "unclear"



def send_whatsapp(lead, score):
    try:
        import pywhatkit as pwt
        mobile     = lead.get("mobile","")
        first_name = lead.get("name","").split()[0]
        city       = lead.get("city","")
        maps_link  = AGENCY_CONFIG["google_maps"]
        address    = AGENCY_CONFIG["address"]
        open_time  = AGENCY_CONFIG["open_time"]
        close_time = AGENCY_CONFIG["close_time"]
        phone      = AGENCY_CONFIG["phone"]

        msg = (
            f"Hello {first_name}! Thank you for speaking with Skoda, the Skoda India voice assistant.\n\n"
            f"Here are your showroom details:\n"
            f"Address: {address}\n"
            f"Timings: Monday to Saturday, {open_time} to {close_time}\n"
            f"Location: {maps_link}\n\n"
            f"Call us: {phone}\n"
            f"Or book online: {AGENCY_CONFIG['website']}\n\n"
            f"We would love to see you for a test drive!\n"
            f"- Team Skoda India"
        )
        pwt.sendwhatmsg_instantly(mobile, msg, wait_time=15, tab_close=True)
        print(f"\n  📱 [WHATSAPP] Sent to {mobile} with location link")
    except ImportError:
        print("  [WHATSAPP] pywhatkit not installed — skipping")
    except Exception as e:
        print(f"  [WHATSAPP ERROR] {e}")



LOG_FILE = "skoda_leads.csv"

LOG_FIELDS = [
    "lead_id","timestamp","name","mobile","email",
    "city","area","state","interest","score","visit_confirmed","notes"
]


def score_lead(confirmed_visit, questions_asked, unclear_count):
    if confirmed_visit:              return "HOT"
    if questions_asked >= 2:         return "WARM"
    return "COLD"


def log_lead(lead, score, confirmed_visit, notes):
    exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "lead_id":         lead.get("id", ""),
            "timestamp":       now().strftime("%Y-%m-%d %H:%M:%S"),
            "name":            lead.get("name",""),
            "mobile":          lead.get("mobile",""),
            "email":           lead.get("email",""),
            "city":            lead.get("city",""),
            "area":            lead.get("area",""),
            "state":           lead.get("state",""),
            "interest":        lead.get("interest",""),
            "score":           score,
            "visit_confirmed": "YES" if confirmed_visit else "NO",
            "notes":           " | ".join(notes),
        })
    print(f"\n  📋 [LOG] {lead.get('name','')} → {score} — saved to {LOG_FILE}")



def greet_customer(lead):
    lang          = get_language(lead.get("state",""))
    time_greet    = get_time_greeting()
    name          = lead.get("name","Friend").split()[0]
    city          = lead.get("city","your city")
    area          = lead.get("area","your area")
    is_open, reason = is_agency_open_now()

    if lang == "hindi":
        _say(f"Namaste {name} ji!")
        pause(0.55)
        _say(f"{time_greet}.")
        pause(0.38)
        _say("Main Skoda bol raha hoon, Skoda India ki taraf se.")
        pause(0.38)
        _say(f"Aapne hamare website par {city}, {area} mein Skoda car ke baare mein jaankari maangi thi.")
        pause(0.38)
        _say("Bahut bahut shukriya aapka. Hum aapki poori madad karne ke liye yahan hain.")
    else:
        _say(f"{time_greet}, {name}!")
        pause(0.55)
        _say("This is Skoda calling from the Skoda India team.")
        pause(0.38)
        _say(f"I can see you recently registered your interest in a Skoda near {area}, {city}.")
        pause(0.38)
        _say("Thank you so much for that. It is wonderful to connect with you today.")

    pause(0.8)

    # Real-time agency status
    if is_open:
        _say(f"Our showroom is open right now, today being {get_current_date_str()}.")
        pause(0.38)
        _say(f"We are open until {AGENCY_CONFIG['close_time']} today, so feel free to visit anytime.")
    else:
        _say(f"Just so you know, today is {get_current_date_str()} and our showroom is currently {reason}.")
        pause(0.38)
        _say(f"We are open Monday to Saturday from {AGENCY_CONFIG['open_time']} to {AGENCY_CONFIG['close_time']}.")

    pause(0.9)



def run_single_lead(lead):
    confirmed_visit = False
    questions_asked = 0
    unclear_count   = 0
    call_notes      = []

    # Step 1: Greet 
    greet_customer(lead)

    #  Step 2: Ask car interest 
    _say("Now I would love to understand a little about what you are looking for.")
    pause(0.38)
    _say("Could you tell me which type of Skoda you are most interested in?")
    pause(0.65)

    car_query   = get_input()
    retry_count = 0

    while car_query == "timeout" and retry_count < 2:
        retry_count   += 1
        unclear_count += 1
        if retry_count == 1:
            _say("I am sorry, I did not quite catch that.")
            pause(0.38)
            _say("Are you looking at an SUV, a sedan, or something budget-friendly?")
        else:
            _say("No worries at all. Let me quickly tell you about our most popular models.")
            pause(0.38)
            _say("The Kylaq is our most affordable compact SUV, starting at 7.59 lakh.")
            pause(0.38)
            _say("The Kushaq and Slavia are our bestsellers in the mid range.")
            pause(0.38)
            _say("And the Superb is our flagship for those who want something truly premium.")
        pause(0.65)
        car_query = get_input()

    if car_query == "timeout":
        car_query = lead.get("interest","suv")

    call_notes.append(f"Interest: {car_query}")

    #  Step 3: Recommend 
    pause(0.38)
    ack("positive")
    speak(recommend_car(car_query), post_pause=0.65)

    #  Step 4: FAQ loop — up to 4 questions 
    _say("I am here for any questions you might have.")
    pause(0.38)
    _say("You can ask about mileage, price, safety, warranty, visit timing, or anything else.")
    pause(0.65)

    for round_num in range(4):
        q = get_input()

        # Done
        if q != "timeout" and any(w in q for w in DONE_WORDS):
            ack("positive")
            break

        # Timeout / unclear
        if q == "timeout":
            unclear_count += 1
            if round_num < 2:
                _say("I am sorry, I could not hear that. Please go ahead, I am listening.")
                pause(0.65)
                continue
            else:
                _say("No worries. I think we have covered the main points nicely.")
                break

        questions_asked += 1
        call_notes.append(f"Q{questions_asked}: {q}")

        answer = match_faq(q)
        if answer:
            ack("neutral")
            speak(answer, post_pause=0.65)
        else:
            rec = recommend_car(q)
            if "We have a really exciting range" not in rec:
                ack("neutral")
                speak(rec, post_pause=0.65)
            else:
                ack("empathy")
                _say("That is a really specific question and I want to make sure you get the right answer.")
                pause(0.38)
                _say("I will arrange for one of our product specialists to personally call you back with full details on that.")
                pause(0.65)

        if round_num < 3:
            _say(random.choice(FOLLOW_UP_QS))
            pause(0.65)

    #  Step 5: Invite for test drive 
    pause(0.9)
    _say(f"I would love to invite you for a test drive at our Skoda showroom in {lead.get('city','your city')}.")
    pause(0.38)
    _say("There is nothing quite like experiencing the car in person.")
    pause(0.38)
    _say("Shall I go ahead and schedule a visit for you?")
    pause(0.65)

    confirm = get_input()

    if confirm != "timeout" and any(w in confirm for w in YES_WORDS):
        confirmed_visit = True
        ack("positive")
        _say("I have noted your request right away.")
        pause(0.38)
        _say(f"Our showroom executive will call you shortly on {lead.get('mobile','')} to confirm the slot.")
        pause(0.38)
        _say("We are really looking forward to seeing you.")
    else:
        _say("Absolutely no pressure at all.")
        pause(0.38)
        _say(f"Whenever you feel ready, our showroom in {lead.get('city','')} is always open Monday through Saturday.")
        pause(0.38)
        _say(f"You can also book a test drive anytime on {AGENCY_CONFIG['website']}.")

    #  Step 6: Warm close 
    pause(0.9)
    first_name = lead.get("name","").split()[0]
    closings = [
        f"Thank you so much for your time today, {first_name}. It was a real pleasure speaking with you. Have a wonderful day.",
        f"It was lovely speaking with you, {first_name}. Thank you for considering Skoda. Wishing you a fantastic day.",
        f"Thank you, {first_name}. We truly appreciate your interest in Skoda India. Take care and have a great day.",
    ]
    speak(random.choice(closings))

    #  Step 7: Score, log, WhatsApp 
    score = score_lead(confirmed_visit, questions_asked, unclear_count)
    log_lead(lead, score, confirmed_visit, call_notes)
    send_whatsapp(lead, score)

    print(f"\n  ✅ Call complete — Score: {score}")
    return score




#  Lead Queue — add real leads here or fetch from DB 
LEAD_QUEUE = [
    {
        "id":            "LEAD-001",
        "name":          "Rahul Sharma",
        "mobile":        "+919876543210",
        "email":         "rahul@example.com",
        "state":         "Uttar Pradesh",
        "district":      "Gautam Buddha Nagar",
        "city":          "Noida",
        "area":          "Sector 18",
        "interest":      "SUV",
        "registered_at": now().isoformat(),
    },
    {
        "id":            "LEAD-002",
        "name":          "Priya Nair",
        "mobile":        "+919123456789",
        "email":         "priya@example.com",
        "state":         "Karnataka",
        "district":      "Bengaluru Urban",
        "city":          "Bengaluru",
        "area":          "Koramangala",
        "interest":      "Sedan",
        "registered_at": now().isoformat(),
    },
    {
        "id":            "LEAD-003",
        "name":          "Amit Singh",
        "mobile":        "+919988776655",
        "email":         "amit@example.com",
        "state":         "Delhi",
        "district":      "South Delhi",
        "city":          "New Delhi",
        "area":          "Saket",
        "interest":      "Budget",
        "registered_at": now().isoformat(),
    },
]


def fetch_lead_from_db(lead_id):
    """
    Wire to real DB in production:
        import mysql.connector
        conn = mysql.connector.connect(
            host="localhost", user="root",
            password=os.getenv("DB_PASS"), database="skoda_leads"
        )
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM leads WHERE id = %s AND called = 0", (lead_id,))
        row = cur.fetchone()
        cur.execute("UPDATE leads SET called = 1 WHERE id = %s", (lead_id,))
        conn.commit()
        return row
    """
    return None   


def run_all_leads():
    """
    Process every lead in LEAD_QUEUE one by one.
    After each call, pauses and asks before dialling next lead.
    """
    total  = len(LEAD_QUEUE)
    scores = []

    for i, lead in enumerate(LEAD_QUEUE):
        print("\n" + "=" * 62)
        print(f"   PROJECT SKODA  |  Lead {i+1} of {total}")
        print(f"   Name   : {lead['name']}")
        print(f"   City   : {lead['city']} — {lead['area']}")
        print(f"   State  : {lead['state']}")
        print(f"   Mobile : {lead['mobile']}")
        print(f"   Date   : {get_current_date_str()}")
        print(f"   Time   : {get_current_time_str()}")
        print("=" * 62)

        if not USE_MIC:
            print(f"\n  Press ENTER to start the call with {lead['name']}, or type 'skip' to skip.")
            cmd = input("  > ").strip().lower()
            if cmd == "skip":
                print(f"  Skipped {lead['name']}")
                continue

        score = run_single_lead(lead)
        scores.append({"lead": lead["name"], "score": score})

        # After each lead (except last), ask to continue
        if i < total - 1:
            remaining = total - i - 1
            print(f"\n  {remaining} lead(s) remaining.")
            if not USE_MIC:
                print(f"  Press ENTER to call next lead ({LEAD_QUEUE[i+1]['name']}), or type 'stop' to exit.")
                cmd = input("  > ").strip().lower()
                if cmd == "stop":
                    print("\n  Stopping. Thank you.")
                    break
            time.sleep(1.5)

    # Summary
    print("\n" + "=" * 62)
    print("   SESSION SUMMARY")
    print("=" * 62)
    hot  = sum(1 for s in scores if s["score"] == "HOT")
    warm = sum(1 for s in scores if s["score"] == "WARM")
    cold = sum(1 for s in scores if s["score"] == "COLD")
    for s in scores:
        print(f"   {s['lead']:<25} → {s['score']}")
    print(f"\n   HOT: {hot}  |  WARM: {warm}  |  COLD: {cold}")
    print(f"   All results saved to: {LOG_FILE}")
    print("=" * 62 + "\n")



if __name__ == "__main__":
    mode = "MIC MODE" if USE_MIC else "DEMO MODE — type your replies"
    print("\n" + "=" * 62)
    print("   PROJECT SKODA — SKODA INDIA VOICE BOT  v5.0")
    print(f"   {mode}")
    print(f"   Today : {get_current_date_str()}")
    print(f"   Time  : {get_current_time_str()}")
    is_open, reason = is_agency_open_now()
    status = "OPEN" if is_open else f"CLOSED ({reason})"
    print(f"   Showroom : {status}")
    print("=" * 62)
    if not USE_MIC:
        print("\n   Tips:")
        print("   - Type your reply and press Enter after each SKODA question")
        print("   - Try: 'suv', 'budget', 'mileage', 'when can I visit', 'yes'")
        print("   - Type 'done' to skip remaining questions")
        print("   - Type 'skip' between leads to skip to the next one\n")

    run_all_leads()
