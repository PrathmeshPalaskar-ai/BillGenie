# ==========================================
# 1. ZAROORI TOOLS (LIBRARIES) MANGWANA
# ==========================================
from fastapi import FastAPI                    # Backend server banane ki main library
from fastapi.middleware.cors import CORSMiddleware  # React aur FastAPI ko aapas me jodne ke liye
from fastapi.responses import RedirectResponse      # Payment ke baad user ko wapas React (Green Tick) par bhejne ke liye
import requests                                # PayPal ke server ko internet ke zariye data bhejne/lane ke liye

# FastAPI ka engine start kar rahe hain aur usko 'app' naam de rahe hain
app = FastAPI()

# ==========================================
# 2. CORS SETUP (SECURITY RULES)
# ==========================================
# Yeh isliye lagaya hai taaki tumhara React (Port 5173) bina kisi security block ke FastAPI (Port 8000) se baat kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Kisi bhi frontend link ko allow karo
    allow_credentials=True,  # Cookies/Headers allow karo
    allow_methods=["*"],     # Har tarah ki request (GET, POST) allow karo
    allow_headers=["*"],     # Har tarah ka data allow karo
)

# ==========================================
# 3. PAYPAL CREDENTIALS (TUMHARI CHABIYAAN)
# ==========================================
# Dhyan rahe: Inke aaspas double quotes (" ") lage hone chahiye
CLIENT_ID = "AYDs5FNYHl9sj2zzS3uuoqqy4GvEPfyFH4T9kjakbQHoajuq0mRd8rinJqIMPeA_q4ddcnuiw_7dGesJ"
SECRET = "EH0PY5wyjerv4M63u7Rdm8Ij14VnoZOX48BneFacAtRhctVQ5bUtkt2_DdUGX7jLUL_xHzkKFOlnbiWW"
PAYPAL_URL = "https://api-m.sandbox.paypal.com" # Yeh PayPal ka test (sandbox) server hai


# ==========================================
# 4. PAYPAL SE ACCESS TOKEN MANGNE WALA FUNCTION
# ==========================================
# PayPal se koi bhi payment karwane se pehle ek temporary chabi (token) leni padti hai
def get_access_token():
    # .strip() isliye lagaya hai taaki agar ID/Secret me galti se space copy ho gaya ho, toh wo hat jaye
    clean_client = CLIENT_ID.strip()
    clean_secret = SECRET.strip()
    
    # PayPal ko batana ki hume ek chabi chahiye
    data = {"grant_type": "client_credentials"}
    response = requests.post(f"{PAYPAL_URL}/v1/oauth2/token", auth=(clean_client, clean_secret), data=data)
    
    # SAFETY CHECK: Agar PayPal error deta hai (ID/Secret galat hone par), toh yahan pakad lenge
    if response.status_code != 200:
        print("\n" + "="*60)
        print("🚨 PAYPAL AUTH ERROR (CLIENT ID YA SECRET GALAT HAI) 🚨")
        print("PayPal Message:", response.text) # Terminal me exact error print karega
        print("="*60 + "\n")
        return "ERROR" # Code crash hone se bachaane ke liye 'ERROR' bhej do
        
    # Agar sab sahi hai, toh token nikal kar wapas bhej do
    return response.json()["access_token"]


# ==========================================
# 5. API 1: PAYMENT LINK BANANE WALI API
# ==========================================
# Jab React me "Pay Now" button dabta hai, toh wo is API par request bhejta hai
@app.get("/create-payment")
def create_payment():
    # Pehle PayPal se chabi (token) maango
    token = get_access_token()
    
    # Agar chabi nahi mili, toh error bhej do
    if token == "ERROR":
        return {"error": "PayPal se connect nahi hua. Terminal check karo, shayad Client ID galat hai."}

    # PayPal ko request bhejne ka format set kar rahe hain
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Payment ki details: 10 Dollar ka order banao
    payment_data = {
        "intent": "CAPTURE", # Iska matlab hume payment abhi leni hai
        "purchase_units": [{"amount": {"currency_code": "USD", "value": "10.00"}}],
        "application_context": {
            # PayPal payment ke baad user ko is "/success" wale link par dhakel dega
            "return_url": "http://127.0.0.1:8000/success",
            "cancel_url": "http://127.0.0.1:8000/cancel"
        }
    }
    
    # PayPal ke server par order bana rahe hain
    response = requests.post(f"{PAYPAL_URL}/v2/checkout/orders", headers=headers, json=payment_data)
    order = response.json()
    
    # PayPal bahut saare link deta hai, hume bas "approve" wala link dhundna hai jahan user card details dalega
    for link in order.get("links", []):
        if link["rel"] == "approve":
            return {"payment_url": link["href"]} # React ko payment ka link bhej do
            
    return {"error": "Payment link nahi mila"}


# ==========================================
# 6. API 2: PAYMENT SUCCESS HONE KE BAAD WALI API
# ==========================================
# Jab user PayPal par payment kar deta hai, toh PayPal usko yahan bhejta hai
@app.get("/success")
def payment_success(token: str): # 'token' URL me aayega jo PayPal dega
    # Paise finalise (capture) karne ke liye wapas nayi chabi maango
    access_token = get_access_token()
    if access_token == "ERROR":
        return {"error": "Payment verify nahi ho payi."}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # PayPal ko command de rahe hain: "Bhai payment verify ho gayi hai, account me daal do"
    capture_url = f"{PAYPAL_URL}/v2/checkout/orders/{token}/capture"
    response = requests.post(capture_url, headers=headers)
    
    # Status Code 201 ka matlab hota hai payment 100% successful aur complete ho gayi hai
    if response.status_code == 201:
        # MAGIC STEP: Black screen ki jagah, user ko wapas React app par bhejo aur URL me '?status=success' laga do
        # Isse React ko pata chal jayega ki payment ho gayi hai aur wo hara (Green) tick ✅ dikhayega
        return RedirectResponse(url="http://localhost:5173/?status=success")
        
    else:
        # Agar payment fail hui toh error dikhao
        return {"error": "Payment capture nahi ho payi"}