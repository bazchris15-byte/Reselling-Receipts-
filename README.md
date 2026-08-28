
# Receipt Snap

A phone-first receipt tracker.

## What it does

1. Tap **Take Receipt Picture**
2. Use your phone camera
3. The image is sent to the OpenAI API for receipt reading
4. Vendor, date, total, tax, category, payment method, and description are extracted
5. The receipt image and data are saved automatically in SQLite
6. Export everything to CSV any time

## Categories

- Inventory
- Shipping Supplies
- Gas
- Equipment
- Repairs
- Meals/Travel
- Office
- Fees
- Other

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

pip install -r requirements.txt

export OPENAI_API_KEY="your-key-here"
# Windows PowerShell:
# $env:OPENAI_API_KEY="your-key-here"

python app.py
```

Then open `http://localhost:5000`.

## Use it on your iPhone

For the camera button and install-to-home-screen experience, deploy the app to a secure HTTPS host.
Once deployed:

1. Open the site in Safari
2. Tap Share
3. Tap **Add to Home Screen**

It will behave much like a lightweight app.

## Important

- Keep your OpenAI API key on the server. Never put it in the webpage.
- Receipt images are stored in the local `receipts/` folder.
- Receipt data is stored in `receipts.db`.
- Back up both if you use this for tax records.
- AI can occasionally misread a receipt. Keep the original image as the source record.
