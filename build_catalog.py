import json
import re

with open("hf_full_tree.json") as f:
    raw = json.load(f)

dirs = sorted([x["path"] for x in raw if x.get("is_dir")])

# Word dictionary for clean Korean pamphlet labels
WORD_KO = {
    "vehicle": "특수차량",
    "forklift": "지게차",
    "palletjack": "핸드 팔레트 자키",
    "handtruck": "핸드카/운반카",
    "tilttruck": "틸트 더스트카",
    "cart": "운반 카트",
    "trolley": "트롤리/대차",
    "vehiclesupport": "차량 리프트/작키",
    "robot": "로봇",
    "robotic": "로보틱 시스템",
    "robotics": "자율주행 로봇",
    "conveyor": "컨베이어 벨트",
    "conveyorbelt": "컨베이어 벨트",
    "warehouse": "물류창고 설비",
    "pallet": "물류 팔레트",
    "rack": "보관 랙/선반",
    "crate": "플라스틱/목재 상자",
    "box": "박스/패키지",
    "drum": "산업용 드럼통",
    "container": "보관 용기/컨테이너",
    "storage": "수납/보관함",
    "factory": "공장 설비",
    "equipment": "산업용 장비",
    "airsystem": "공조/에어 컴프레서",
    "coolingsystem": "냉각 시스템",
    "electricalsystem": "전장/배터리 시스템",
    "climate": "냉난방/송풍기",
    "structure": "건축/구조물",
    "ladder": "사다리",
    "barrier": "안전 펜스/바리케이드",
    "sign": "안전 표지판",
    "fireprotection": "소방/소화 설비",
    "ppe": "안전 보호구(PPE)",
    "construction": "건설 현장 장비",
    "handtool": "수공구",
    "powertool": "전동공구",
    "servicetool": "정비 툴/크레인",
    "testingtool": "계측/진단 장비",
    "bodypart": "자동차 외장 부품",
    "enginecomponent": "엔진 부품",
    "brakesystem": "브레이크 부품",
    "suspension": "서스펜션 부품",
    "drivetrain": "구동계 부품",
    "exhaustsystem": "배기 부품",
    "fuelsystem": "연료계 부품",
    "interiorpart": "차량 내장 부품",
    "wheel": "휠/림",
    "tire": "타이어",
    "bed": "침대",
    "hospital": "병원용",
    "chair": "의자",
    "patient": "환자용",
    "surgical": "수술용",
    "xray": "엑스레이 장비",
    "ct": "CT 촬영기",
    "iv": "수액 걸이(IV 폴)",
    "anesthesia": "마취기",
    "blood": "혈액/의료 소모품",
    "instrument": "정밀/의료 기구",
    "computer": "컴퓨터/IT 기기",
    "tv": "디스플레이/TV",
    "cabinet": "캐비닛/수납장",
    "stationery": "사무용품",
    "book": "도서/문서",
    "blinds": "블라인드",
    "lighting": "조명 기구",
    "fixture": "설비 픽스처",
    "decor": "인테리어 소품",
    "device": "전자 기기",
    "appliance": "가전제품",
    "cleaning": "청소 도구/세제",
    "bucket": "버킷/양동이",
    "bin": "폐기물/분리수거함",
    "consumable": "산업 소모품/케미컬",
    "paint": "도장/페인트 용품",
    "tape": "산업용 테이프",
    "food": "식품/식자재",
    "kitchenware": "주방 기구/조리도구",
    "dishware": "식기류",
    "utensil": "조리/커트러리",
    "bottle": "보틀/실험병",
    "orange": "오렌지",
    "blue": "블루",
    "red": "레드",
    "yellow": "옐로우",
    "green": "그린",
    "black": "블랙",
    "white": "화이트",
    "gray": "그레이",
    "brown": "브라운",
    "heavyduty": "중량물용",
    "lowprofile": "저상형",
    "mobile": "이동식",
    "small": "소형",
    "bot": "모바일 봇",
    "arm": "로봇 팔",
    "lifttable": "리프트 테이블",
    "scissormobile": "이동식 시저 리프트",
}

def categorize(asset_id):
    p = asset_id.split("_")[0].lower()
    low = asset_id.lower()
    if p in ("vehicle", "palletjack", "handtruck", "tilttruck", "cart", "trolley", "vehiclesupport") or "forklift" in low or "trolley" in low or "cart" in low:
        return "forklift_vehicle", "🚜 지게차·운반차량", 180.0, 0.25
    if p in ("robot", "robotic", "robotics", "conveyor") or "robot" in low or "conveyor" in low or "arm_articulated" in low:
        return "robotics", "🤖 로봇·자동화 설비", 65.0, 0.30
    if p in ("warehouse", "pallet", "rack", "crate", "box", "drum", "container", "storage"):
        return "warehouse", "🏭 물류·창고·팔레트", 18.5, 0.35
    if p in ("factory", "equipment", "airsystem", "coolingsystem", "electricalsystem", "climate", "structure", "ladder", "barrier", "sign", "fireprotection", "ppe", "construction"):
        return "factory", "⚙️ 공장·산업기계", 45.0, 0.28
    if p in ("handtool", "powertool", "servicetool", "testingtool", "bodypart", "enginecomponent", "brakesystem", "suspension", "drivetrain", "exhaustsystem", "fuelsystem", "interiorpart", "wheel", "tire", "carframe"):
        return "tools_auto", "🔧 공구·정비·자동차부품", 8.5, 0.42
    if p in ("xray", "ct", "iv", "anesthesia", "blood", "instrument", "catheter", "bandage", "cannulae", "clogs") or "hospital" in low or "medical" in low or "surgical" in low or "patient" in low or "laboratory" in low:
        return "medical", "🏥 의료·병원·연구실", 24.0, 0.32
    if p in ("computer", "tv", "cabinet", "stationery", "book", "blinds", "lighting", "fixture", "decor", "device", "chair", "table", "desk"):
        return "office_it", "🖥️ IT·오피스·가구", 12.0, 0.36
    if p in ("food", "kitchenware", "dishware", "utensil", "bottle"):
        return "food_kitchen", "🍎 식음료·주방용품", 1.2, 0.48
    return "appliances_misc", "🏠 가전·청소·생활소모품", 5.0, 0.40

def translate_name(asset_id):
    parts = asset_id.split("_")
    ko_parts = []
    for pt in parts:
        low = pt.lower()
        if low in WORD_KO:
            ko_parts.append(WORD_KO[low])
        elif re.match(r"^[a-z]\d+$", low):
            ko_parts.append(pt.upper())
        else:
            # Split camelCase
            sub = re.sub(r"([a-z])([A-Z])", r"\1 \2", pt)
            ko_parts.append(sub)
    # Deduplicate consecutive identical words
    dedup = []
    for w in ko_parts:
        if not dedup or dedup[-1] != w:
            dedup.append(w)
    return " ".join(dedup)

catalog = []
for d in dirs:
    cat_id, cat_label, default_mass, default_rest = categorize(d)
    # Special overrides for our featured heavy equipment
    if "forklift" in d:
        default_mass, default_rest = 245.1, 0.18
    elif "palletJack" in d:
        default_mass, default_rest = 78.5, 0.22
    elif "robotics_small_bot" in d:
        default_mass, default_rest = 34.0, 0.30

    catalog.append({
        "id": d,
        "name_ko": translate_name(d),
        "cat_id": cat_id,
        "cat_label": cat_label,
        "mass_kg": default_mass,
        "restitution": default_rest,
        "thumb": f"https://huggingface.co/datasets/nvidia/simready-assets/resolve/main/{d}/simready_usd/.thumbs/256x256/sm_{d}_01.usd.png",
        "hf_url": f"https://huggingface.co/datasets/nvidia/simready-assets/tree/main/{d}"
    })

with open("catalog.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False)

print(f"Built catalog.json with {len(catalog)} items.")

