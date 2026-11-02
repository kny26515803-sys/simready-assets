# 🚜 NVIDIA SimReady — Sim-to-Real 워크셀 시뮬레이터 & 2,677 에셋 디지털 팜플렛

NVIDIA의 오픈소스 피지컬 AI 에셋 라이브러리([`nvidia/simready-assets`](https://huggingface.co/datasets/nvidia/simready-assets))를 활용하여, **로컬 디스크 용량을 최소한으로 사용하면서도 실제 산업용 작업장(Workcell) 물리 실험과 2,677개 전체 품목 탐색·변환을 수행**할 수 있는 Sim-to-Real 웹 시뮬레이터 및 디지털 팜플렛입니다.

---

## ✨ 주요 기능

### 1. 🏭 Sim-to-Real 물류창고 피지컬 AI 워크셀 시뮬레이터 (`index.html`)
- **실제 기구학(Articulation)이 분리된 오렌지 전동 지게차 (`vehicle_forklift_orange_a01`)**:
  - `W` / `S` (또는 `↑` / `↓`): 가감속, 구름 마찰, 중량 관성이 적용된 전후진 주행 + 4륜 바퀴 실시간 회전
  - `A` / `D` (또는 `←` / `→`): 조향 핸들(`sm_rudder`) 회전 및 차체 선회
  - `R` / `F` (또는 HUD 슬라이더): 유압 포크(`sm_fork`) 및 마스트 롤러 상하 리프팅 (`0.00m ~ 1.15m`)
- **포크-팔레트 실제 적재(Lifting) 및 강체 충돌 물리**:
  - 포크를 낮추고(`0.02m`) 팔레트(`pallet_a01`) 하단으로 진입한 뒤 포크를 상승(`R`)시키면 팔레트와 적재 박스(`box_cardboard_a01`)가 포크에 결속되어 함께 리프팅됩니다.
  - 적재 시 총 중량(`245.1kg + 화물 42.5kg = 287.6kg`)이 실시간 합산됩니다.
- **🤖 Sim-to-Real AI 자율 피킹·하역 실험 모드**:
  - `[🤖 AI 자율 피킹·하역 실험 시작]` 버튼 클릭 시 상태머신(`1_INSERT_FORKS` → `2_LIFT_CARGO` → `3_DRIVE_TO_DROPZONE` → `4_LOWER_PALLET` → `5_RETRACT_SAFE`)이 작동하여 지게차가 스스로 팔레트를 피킹해 목표 하역 구역(Zone B)까지 자율 운반·하역합니다.
- **자율주행 모바일 로봇 AMR (`robotics_small_bot_a01`)**:
  - 작업장 외곽을 자율 순찰하며 회전 브러시를 구동하고, 지게차 접근 시 LiDAR 안전 거리 감지로 자동 일시 정지합니다.

### 2. 📘 2,677종 SimReady 에셋 디지털 팜플렛 (`catalog.json` & `server.py`)
- `nvidia/simready-assets` 내 전체 **2,677개 에셋**을 9대 직관적 한글 카테고리(지게차·운반차량, 로봇·자동화, 물류·창고·팔레트, 공장·산업기계, 공구·정비, 의료·병원, IT·오피스, 가전·청소, 식음료·주방)로 분류했습니다.
- Hugging Face 공식 `256x256` 프리뷰 썸네일 실시간 스트리밍으로 로컬 디스크 부담 없이 전 품목을 시각적으로 검색·열람할 수 있습니다.
- **`[➕ 작업장에 즉시 배치]`**: 사전 변환된 에셋 5종은 즉시 작업장에 스폰되며, 클라우드 에셋은 로컬 Blender 헤드리스 파이프라인(`blender_worker.py`)을 통해 OpenUSD(`.usda`/`.usd`)를 경량 `.glb`로 자동 변환 후 임시 원본을 즉시 삭제하여 디스크 여유 공간을 보호합니다.

---

## 🚀 실행 방법

```bash
python3 server.py
```

브라우저에서 **http://localhost:8000** 으로 접속합니다.
