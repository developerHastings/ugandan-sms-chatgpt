from dotenv import load_dotenv
import os
import requests

load_dotenv()  # Load environment variables from .env file

url = "https://api.sunbird.ai/tasks/nllb_translate"
access_token = os.getenv("AUTH_TOKEN")
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

data = {
    "source_language": "lug",
    "target_language": "eng",
    "text": "Ekibiina ekiddukanya omuzannyo gw’emisinde mu ggwanga ekya Uganda Athletics Federation kivuddeyo nekitegeeza nga lawundi esooka eyemisinde egisunsulamu abaddusi abanakiika mu mpaka ezenjawulo ebweru w’eggwanga egya National Athletics Trials nga bwegisaziddwamu.",
}

response = requests.post(url, headers=headers, json=data)

print(response.json())

language_codes = {
    "English": "eng",
    "Luganda": "lug",
    "Runyankole": "nyn",
    "Acholi": "ach",
    "Ateso": "teo",
    "Lugbara": "lgg"
}

url = "https://api.sunbird.ai/tasks/stt"
access_token = os.getenv("AUTH_TOKEN")
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {access_token}",
}

files = {
    "audio": (
        "FILE_NAME",
        open("/path/to/audio_file", "rb"),
        "audio/mpeg",
    ),
}
data = {
    "language": "lug",
    "adapter": "lug",
}

response = requests.post(url, headers=headers, files=files, data=data)

print(response.json())

url = "https://api.sunbird.ai/tasks/summarise"
token = os.getenv("AUTH_TOKEN")
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

text = (
    "ndowooza yange ku baana bano abato abatalina tufuna funa ya uganda butuufu "
    "eserbamby omwana oyo bingi bye yeegomba okuva mu buto bwe ate by'atasobola "
    "kwetuusaako bw'afuna mu naawumuwaamagezi nti ekya mazima nze kaboyiaadeyaatei "
    "ebintu kati bisusse mu uganda wano ebyegombebw'omwana by'atasobola kwetuusaako "
    "ng'ate abazadde nabo bambi bwe beetunulamubamufuna mpola tebasobola kulabirira "
    "mwana oyo bintu by'ayagala ekivaamu omwana akemererwan'ayagala omulenzi omulenzi "
    "naye n'atoba okuatejukira ba mbi ba tannategeera bigambo bya kufuna famire fulani "
    "bakola kyagenda layivu n'afuna embuto eky'amazima nze mbadde nsaba be kikwata "
    "govenment sembera embeera etuyisa nnyo abaana ne tubafaako embeera gwe nyiga gwa "
    "omuzadde olina olabirira maama we olina olabirira n'abato kati kano akasuumuseemu "
    "bwe ka kubulako ne keegulirayooba kapalaobakakioba tokyabisobola ne keyiiyabatuyambe "
    "buduufuembeera bagikyusa mu tulemye"
)

data = {"text": text}

response = requests.post(url, headers=headers, json=data)

print(response.json())

import os

import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.sunbird.ai/tasks/language_id"
token = os.getenv("AUTH_TOKEN")
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

text = "ndowooza yange ku baana bano abato abatalina tufuna funa ya uganda butuufu"

data = {"text": text}

response = requests.post(url, headers=headers, json=data)

print(response.json())
class Config:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
        self.TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
        self.SERVER_PORT = int(os.getenv("PORT", "5000"))
        self.ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "default-admin-token")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
          # Emergency configuration
        self.EMERGENCY_CONTACTS = os.getenv("EMERGENCY_CONTACTS", "").split(",")
        self.EMERGENCY_SERVICES = {
            "police": "999",
            "ambulance": "911", 
            "fire": "112",
            "red_cross": "+256-414-258-701"
        }
        self.EMERGENCY_MESSAGE_TEMPLATE = os.getenv(
            "EMERGENCY_MESSAGE_TEMPLATE", 
            "🚨 EMERGENCY ALERT from {user_number}: {message}"
        )
config = Config()