# Pokemon GO Data Repository
# 포켓몬고 데이터 저장소

This directory contains comprehensive Pokemon GO game data including Pokemon information, events, official addresses, items, moves, and game mechanics.

이 디렉토리에는 포켓몬 정보, 이벤트, 공식 주소, 아이템, 기술 및 게임 메커니즘을 포함한 포괄적인 포켓몬고 게임 데이터가 포함되어 있습니다.

## Directory Structure / 디렉토리 구조

```
pokemon-go-data/
├── pokemon/          # Pokemon species data / 포켓몬 종 데이터
│   └── pokemon_list.json
├── events/           # Event information / 이벤트 정보
│   └── events_2025.json
├── locations/        # Official addresses and locations / 공식 주소 및 위치
│   └── official_addresses.json
├── items/            # In-game items / 게임 내 아이템
│   └── items_list.json
├── moves/            # Pokemon moves / 포켓몬 기술
│   └── moves_list.json
├── mechanics/        # Game mechanics / 게임 메커니즘
│   └── game_mechanics.json
└── README.md         # This file / 이 파일
```

## Data Contents / 데이터 내용

### 1. Pokemon Data (pokemon/pokemon_list.json)
포켓몬 데이터 (pokemon/pokemon_list.json)

Contains detailed information about Pokemon including:
- Pokemon ID, names (English and Korean)
- Types, stats (Attack, Defense, Stamina)
- Evolution chains and candy requirements
- Max CP values
- Shiny availability
- Mega Evolution and Primal Reversion data
- Special forms and costumes

포켓몬에 대한 상세 정보 포함:
- 포켓몬 ID, 이름 (영어 및 한국어)
- 타입, 스탯 (공격, 방어, 체력)
- 진화 체인 및 사탕 요구사항
- 최대 CP 값
- 색이 다른 포켓몬 가능 여부
- 메가 진화 및 원시 회귀 데이터
- 특별 폼과 코스튬

**Coverage:**
- Generation 1 (Kanto): 13 Pokemon including starters and legendaries
- Generation 2 (Johto): 4 Pokemon including legendaries
- Generation 3 (Hoenn): 4 Pokemon including legendaries

### 2. Events Data (events/events_2025.json)
이벤트 데이터 (events/events_2025.json)

Complete 2025 event calendar including:
- Seasonal events (New Year, Valentine's Day, Halloween)
- Community Days with exclusive moves
- Cultural events (Lunar New Year)
- Pokemon GO Fest
- Raid events and boss rotations
- Season information

2025년 전체 이벤트 캘린더 포함:
- 계절 이벤트 (새해, 발렌타인데이, 할로윈)
- 전용 기술이 있는 커뮤니티 데이
- 문화 이벤트 (설날)
- 포켓몬고 페스트
- 레이드 이벤트 및 보스 로테이션
- 시즌 정보

**Event Types:**
- Community Days
- Seasonal Events
- Raid Events
- GO Fest
- Community Day Classic

### 3. Official Addresses (locations/official_addresses.json)
공식 주소 (locations/official_addresses.json)

Niantic and Pokemon GO official information:
- Niantic office locations worldwide (San Francisco HQ, Tokyo, London, Seattle, LA)
- Official websites and support pages
- Social media accounts (Twitter, Facebook, Instagram, YouTube, Discord)
- Regional support information
- Community resources

나이앤틱과 포켓몬고 공식 정보:
- 전세계 나이앤틱 사무실 위치 (샌프란시스코 본사, 도쿄, 런던, 시애틀, LA)
- 공식 웹사이트 및 지원 페이지
- 소셜 미디어 계정 (트위터, 페이스북, 인스타그램, 유튜브, 디스코드)
- 지역 지원 정보
- 커뮤니티 리소스

### 4. Items Data (items/items_list.json)
아이템 데이터 (items/items_list.json)

Comprehensive item database:
- **Poke Balls**: Standard, Great, Ultra, Premier
- **Potions & Revives**: All healing items
- **Berries**: Razz, Nanab, Pinap, Golden Razz, Silver Pinap
- **Evolution Items**: Sun Stone, King's Rock, Metal Coat, Dragon Scale, Up-Grade, Sinnoh Stone, Unova Stone
- **Battle Items**: Fast TM, Charged TM, Elite TMs
- **Power-up Items**: Stardust, Candy, Rare Candy, Candy XL, Rare Candy XL
- **Incense & Lures**: Standard and special lures (Glacial, Mossy, Magnetic, Rainy)
- **Raid Passes**: Raid Pass, Remote Raid Pass, Premium Battle Pass
- **Storage Upgrades**: Pokemon and Item Bag upgrades

포괄적인 아이템 데이터베이스:
- **몬스터볼**: 일반, 수퍼볼, 하이퍼볼, 프리미어볼
- **상처약 & 기력**: 모든 회복 아이템
- **열매**: 라즈, 나나, 파일, 금색 라즈, 은색 파일
- **진화 아이템**: 태양의돌, 왕의징표석, 금속코트, 용의비늘, 업그레이드, 신오의돌, 하나의돌
- **배틀 아이템**: 빠른 기술머신, 차지 기술머신, 엘리트 기술머신
- **파워업 아이템**: 별의모래, 사탕, 이상한사탕, XL사탕, 이상한사탕XL
- **향로 & 루어**: 일반 및 특수 루어 (글레이셜, 이끼, 마그네틱, 레이니)
- **레이드패스**: 레이드패스, 리모트 레이드패스, 프리미엄 배틀패스
- **보관함 업그레이드**: 포켓몬 및 도구 가방 업그레이드

### 5. Moves Data (moves/moves_list.json)
기술 데이터 (moves/moves_list.json)

Pokemon move information:
- **Fast Moves**: Quick Attack, Vine Whip, Water Gun, Dragon Breath, Confusion, Counter, Charm, Shadow Claw, and more
- **Charged Moves**: Including Community Day exclusive moves (Hydro Cannon, Blast Burn, Frenzy Plant, Meteor Mash)
- **Signature Moves**: Sacred Sword, V-create, Aeroblast, Sacred Fire
- **Legacy Moves**: Requiring Elite TMs
- Move statistics: Power, Energy, DPT, EPT
- PvP-specific stats and effects

포켓몬 기술 정보:
- **빠른 기술**: 전광석화, 덩굴채찍, 물대포, 용의숨결, 염동력, 카운터, 스위트키스, 섀도크로 등
- **차지 기술**: 커뮤니티 데이 전용 기술 포함 (하이드로캐논, 블래스트번, 하드플랜트, 코멧펀치)
- **전용 기술**: 성스러운칼, V제너레이트, 에어로블래스트, 성스러운불꽃
- **레거시 기술**: 엘리트 기술머신 필요
- 기술 통계: 위력, 에너지, DPT, EPT
- PvP 전용 스탯 및 효과

### 6. Game Mechanics (mechanics/game_mechanics.json)
게임 메커니즘 (mechanics/game_mechanics.json)

Detailed game system information:
- **Gyms**: Defending, battling, coin earning, motivation system
- **Raids**: All tiers (1-star to 5-star, Mega, Elite), mechanics, rewards
- **GO Battle League**: Great League, Ultra League, Master League, ranking system
- **Buddy System**: Heart activities, buddy levels, benefits
- **Trading**: Friendship levels, Lucky Pokemon, special trades
- **Team GO Rocket**: Grunts, Leaders, Giovanni, Shadow Pokemon
- **Research Tasks**: Field, Special, Timed, and Season Research

상세한 게임 시스템 정보:
- **체육관**: 방어, 배틀, 코인 획득, 동기 시스템
- **레이드**: 모든 티어 (1성급~5성급, 메가, 엘리트), 메커니즘, 보상
- **GO 배틀 리그**: 그레이트리그, 울트라리그, 마스터리그, 랭킹 시스템
- **친구 시스템**: 하트 활동, 친구 레벨, 혜택
- **교환**: 친밀도 레벨, 행운의 포켓몬, 특별 교환
- **로켓단**: 일반 조직원, 간부, 비주기, 섀도우 포켓몬
- **리서치 과제**: 필드, 스페셜, 시간 제한, 시즌 리서치

## Data Format / 데이터 형식

All data files are in JSON format with the following features:
- UTF-8 encoding for international character support
- Bilingual support (English and Korean) where applicable
- Consistent naming conventions
- Structured hierarchical data

모든 데이터 파일은 다음 기능을 가진 JSON 형식입니다:
- 국제 문자 지원을 위한 UTF-8 인코딩
- 해당되는 경우 이중 언어 지원 (영어 및 한국어)
- 일관된 명명 규칙
- 구조화된 계층 데이터

## Usage Examples / 사용 예시

### Loading Pokemon Data
```python
import json

# Load Pokemon data
with open('pokemon/pokemon_list.json', 'r', encoding='utf-8') as f:
    pokemon_data = json.load(f)

# Access Generation 1 Pokemon
gen1_pokemon = pokemon_data['generation_1']

# Find Pikachu
pikachu = next(p for p in gen1_pokemon if p['name'] == 'Pikachu')
print(f"Pikachu Max CP: {pikachu['max_cp']}")
print(f"Pikachu Korean Name: {pikachu['korean_name']}")
```

### Loading Event Data
```python
import json

# Load event data
with open('events/events_2025.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

# Get all Community Days
community_days = [e for e in events['events_2025'] if e['event_type'] == 'Community Day']
```

### Loading Official Addresses
```javascript
const fs = require('fs');

// Load official addresses
const addresses = JSON.parse(
    fs.readFileSync('locations/official_addresses.json', 'utf-8')
);

// Get Niantic headquarters
const hq = addresses.niantic_offices.find(office => office.headquarters);
console.log(`HQ Address: ${hq.address}`);
```

## Data Sources / 데이터 출처

This data is compiled from:
- Official Pokemon GO website (pokemongolive.com)
- Niantic official announcements
- Game datamining and community research
- The Silph Road research
- Pokemon GO Hub and other community resources

이 데이터는 다음에서 컴파일되었습니다:
- 공식 포켓몬고 웹사이트 (pokemongolive.com)
- 나이앤틱 공식 발표
- 게임 데이터마이닝 및 커뮤니티 연구
- 실프 로드 연구
- 포켓몬고 허브 및 기타 커뮤니티 리소스

## Updates / 업데이트

This data is current as of January 2025. Pokemon GO is regularly updated with new content, so some information may change over time.

이 데이터는 2025년 1월 기준입니다. 포켓몬고는 정기적으로 새로운 콘텐츠로 업데이트되므로 일부 정보는 시간이 지남에 따라 변경될 수 있습니다.

## Contributing / 기여

To update or add data:
1. Ensure data follows the existing JSON structure
2. Include both English and Korean names/descriptions where applicable
3. Verify accuracy against official sources
4. Submit updates with clear documentation

데이터를 업데이트하거나 추가하려면:
1. 데이터가 기존 JSON 구조를 따르는지 확인
2. 해당되는 경우 영어 및 한국어 이름/설명 모두 포함
3. 공식 출처와 대조하여 정확성 확인
4. 명확한 문서와 함께 업데이트 제출

## License / 라이선스

This data compilation is for informational purposes. Pokemon GO and all related content are trademarks of Niantic, Inc. and The Pokemon Company.

이 데이터 컴파일은 정보 제공 목적입니다. 포켓몬고 및 모든 관련 콘텐츠는 나이앤틱 및 포켓몬 컴퍼니의 상표입니다.

## Contact / 연락처

For questions or corrections regarding this data, please refer to:
- Official Pokemon GO Support: https://niantic.helpshift.com/hc/en/6-pokemon-go/
- Pokemon GO Live: https://pokemongolive.com/

이 데이터에 대한 질문이나 수정 사항은 다음을 참조하십시오:
- 공식 포켓몬고 지원: https://niantic.helpshift.com/hc/en/6-pokemon-go/
- 포켓몬고 라이브: https://pokemongolive.com/
