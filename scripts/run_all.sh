#!/usr/bin/env bash
# Crawl 200 different search terms, each saving ~100 products to its own JSON file.
# Output: data/products/<term>.json
# Usage: bash scripts/run_all.sh

set -uo pipefail

# Activate virtualenv — path is relative to the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
source "$PROJECT_DIR/.venv/bin/activate"

SEARCH_TERMS=(
# Smartphones & tablets
"iPhone 16 Pro"
"Samsung Galaxy S25"
"Google Pixel 9"
"Foldable smartphone"
"Gaming smartphone"
"Android tablet 12 inch"
"iPad Air M3"
"iPad Pro OLED"
"budget tablet android"
"e-ink tablet"

# Laptops & computing
"MacBook Pro M4"
"AI laptop"
"gaming laptop RTX 50"
"ultrabook laptop"
"mini PC gaming"
"Chromebook Plus"
"portable monitor 4K"
"USB-C docking station"
"external SSD 2TB"
"Thunderbolt SSD"

# PC hardware
"RTX 5090 graphics card"
"RTX 5080 graphics card"
"AMD Ryzen 9 9950X"
"Intel Core Ultra processor"
"gaming motherboard"
"DDR5 RAM 32GB"
"PC liquid cooler"
"gaming PC case"
"WiFi 7 router"
"mesh WiFi system"

# Gaming
"PlayStation 5 Slim"
"PlayStation 5 Pro"
"Xbox Series X"
"Nintendo Switch OLED"
"Nintendo Switch 2"
"gaming controller pro"
"VR gaming headset"
"gaming steering wheel"
"retro handheld console"
"cloud gaming device"

# Audio
"AirPods Pro 3"
"AirPods 4"
"Sony WH-1000XM6"
"Bose QuietComfort Ultra"
"gaming headset wireless"
"Bluetooth speaker portable"
"party Bluetooth speaker"
"soundbar Dolby Atmos"
"home theater system"
"vinyl record player"

# Wearables & health tech
"Apple Watch Series 11"
"Samsung Galaxy Watch 7"
"smart ring health tracker"
"fitness tracker band"
"sleep tracker ring"
"smart scale body composition"
"blood pressure monitor smart"
"red light therapy mask"
"eye massager device"
"massage gun deep tissue"

# Smart home
"robot vacuum with mop"
"robot lawn mower"
"smart bird feeder camera"
"video doorbell camera"
"smart security camera"
"smart thermostat"
"smart light bulbs"
"smart home hub"
"smart plugs WiFi"
"smart air purifier"

# Home appliances
"air fryer oven"
"espresso machine home"
"coffee grinder burr"
"stand mixer kitchen"
"electric kettle gooseneck"
"countertop ice maker"
"portable blender"
"sous vide cooker"
"food dehydrator"
"rice cooker smart"

# Kitchen trends
"cast iron skillet"
"Dutch oven cookware"
"knife set japanese"
"bamboo cutting board"
"meal prep containers"
"sourdough starter kit"
"bread maker machine"
"electric grill indoor"
"food scale digital"
"glass straw reusable"

# Photography & creator gear
"mirrorless camera full frame"
"vlogging camera"
"action camera 4K"
"drone with camera 4K"
"camera tripod carbon fiber"
"ND filters set"
"camera backpack"
"ring light for streaming"
"green screen backdrop"
"USB microphone podcast"

# Streaming & creator tools
"stream deck controller"
"4K webcam"
"LED panel video light"
"portable teleprompter"
"podcast audio interface"
"studio monitor speakers"
"capture card streaming"
"desk boom arm microphone"
"camera monitor field"
"portable SSD for creators"

# Office & productivity
"standing desk electric"
"ergonomic office chair"
"desk walking treadmill"
"monitor arm dual"
"desk cable management"
"mechanical keyboard custom"
"wireless ergonomic mouse"
"notebook smart reusable"
"digital calendar display"
"AI note taking device"

# Fitness
"adjustable dumbbells"
"home gym system"
"yoga mat eco"
"smart jump rope"
"treadmill folding"
"stationary bike"
"fitness resistance bands"
"foam roller muscle"
"pilates reformer"
"smart water bottle"

# Outdoor & mobility
"electric scooter adult"
"electric bike commuter"
"mountain bike carbon"
"road bike endurance"
"camping tent ultralight"
"hiking backpack 40L"
"hiking boots waterproof"
"portable power station"
"solar generator camping"
"camping stove portable"

# Automotive
"dash cam 4K"
"wireless carplay adapter"
"EV charger home"
"car jump starter"
"tire inflator portable"
"OBD2 scanner bluetooth"
"car vacuum cleaner"
"car phone mount magsafe"
"LED car headlights"
"car interior ambient lights"

# Fashion & accessories
"Nike Air Jordan sneakers"
"Adidas Samba shoes"
"New Balance sneakers"
"streetwear hoodie"
"vintage Levi jeans"
"cargo pants streetwear"
"luxury designer handbag"
"Ray-Ban sunglasses"
"North Face jacket"
"New Era fitted cap"

# Jewelry & watches
"Rolex luxury watch"
"mechanical watch automatic"
"smartwatch android"
"fitness smartwatch"
"diamond engagement ring"
"gold necklace 14k"
"silver bracelet women"
"pearl earrings"
"titanium ring"
"gemstone pendant"

# Collectibles
"Pokemon trading cards"
"Magic the Gathering cards"
"Yu-Gi-Oh cards"
"Funko Pop collectibles"
"LEGO Technic sets"
"Hot Wheels collector cars"
"Star Wars collectibles"
"Marvel action figures"
"anime figurines"
"limited edition sneakers"

# Books & media
"manga box set"
"graphic novel collection"
"vinyl records classic rock"
"K-pop vinyl album"
"retro video game cartridges"
"Nintendo 64 games"
"PlayStation 1 games"
"Game Boy cartridges"
"comic book graded"
"rare vinyl records"

# Musical instruments
"electric guitar starter"
"acoustic guitar bundle"
"digital piano keyboard"
"MIDI controller keyboard"
"DJ controller mixer"
"audio interface USB"
"studio condenser microphone"
"drum machine sampler"
"bass guitar beginner"
"saxophone student"

# Kids & family
"baby stroller travel"
"baby car seat convertible"
"baby monitor WiFi"
"educational STEM toys"
"kids coding robot"
"kids drone"
"kids electric scooter"
"dollhouse wooden"
"building blocks STEM"
"family board games"

# Pets
"automatic cat litter box"
"smart pet feeder"
"pet camera treat dispenser"
"cat tree tower"
"dog harness no pull"
"premium dog food"
"pet grooming vacuum"
"dog crate furniture"
"aquarium fish tank"
"reptile terrarium"

# Travel
"carry on backpack"
"luggage set lightweight"
"travel adapter universal"
"packing cubes compression"
"passport holder RFID"
"travel pillow memory foam"
"portable charger travel"
"travel toiletry organizer"
"neck pillow airplane"
"anti theft backpack"
)

cd "$PROJECT_DIR"
mkdir -p data/products

TOTAL=${#SEARCH_TERMS[@]}
echo "Starting crawl of $TOTAL search terms, ~100 products each."
echo "Output directory: data/products/"
echo ""

for i in "${!SEARCH_TERMS[@]}"; do
  term="${SEARCH_TERMS[$i]}"
  # Sanitize term for filename: lowercase, spaces to underscores, remove special chars
  filename=$(echo "$term" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd '[:alnum:]_-')
  output="data/products/${filename}.json"

  echo "[$(( i + 1 ))/$TOTAL] Crawling: \"$term\" → $output"

  scrapy crawl ebay \
    -a search="$term" \
    -s CLOSESPIDER_ITEMCOUNT=100 \
    -O "$output" \
    2>&1 | grep -E "(item_scraped_count|ERROR|Spider closed)" | tail -3 || true

  echo ""
done

echo "Done. All results saved in data/products/"
