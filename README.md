# SEAFOOD BOIL RAMPAGE🦀

An arcade-style shooter built with Pygame where your goal is to gather the ultimate seafood boil while surviving the chaos of a last-minute grocery run.

## 🛒 The Premise
An arcade shooter inspired by Space Invaders, featuring classic fixed-shooter movement and wave-based survival, but set in the high-stakes world of Jersey grocery shopping. The store is closing, and you need the perfect ingredients for your seafood boil. Instead of aliens, you’re dodging aggressive shoppers in a race against time to clear the aisles of eggs, corn, shrimp, and crab. The music is pumping, the doors are locking, and the only way to get your ingredients is to blast through them.

## 🎮 Gameplay Features
* **Classic Arcade Mechanics:** Inspired by the golden era of fixed shooters.
* **Dynamic Difficulty:** Choose between **WEEKDAY** (Casual), **WEEKEND** (Busy), or **HOLIDAY** (Absolute Mayhem) to change movement speed and patterns.
* **The Lobster Reward:** Rare lobsters spawn randomly. Catching them is the only way to trigger the "Gold Standard" ending.
* **Realistic Economy:** Points are scaled to real-world currency (10 pts = $1.00).
* **The "Blind Checkout":** To keep the pressure on, the score is hidden during the final victory screen. You only find out your official total by checking your "Gold Receipt."
* **Visuals:** All character sprites, ingredient icons, and backgrounds were designed using Canva.
* **Audio:** The grocery-store music/sounds and other sound effects were self-produced/curated using GarageBand, YouTube Studio, and Freesound.

## 🧾 The Gold Receipt
If you successfully clear the board and catch at least one lobster, the game generates a `receipt.txt` file on your desktop. This is your official tally of the rampage, featuring:
* Real-time timestamps.
* Itemized billing for eggs, corn, shrimp, crab, and lobster.
* A scaled final total with realistic currency formatting.

## 🛠️ Installation & Controls
1. Ensure you have `pygame` installed: `pip install pygame`
2. Download the zip file
3. Run the game: `python seafood_boil_rampage.py`

**Controls:**
* **Arrow Keys:** Move your shopping cart.
* **Spacebar:** Launch Old Bay seasoning (bullets).
* **Enter:** Navigate menus and return your cart.
