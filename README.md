# Receipt Snap Free

A zero-subscription, phone-first receipt tracker.

## How it works
- Tap **Take Receipt Picture**
- OCR runs in the browser with Tesseract.js
- The app guesses store, date, total, and category
- You get a quick confirmation screen
- The receipt image + record are saved locally on your phone/browser using IndexedDB
- Export CSV or a JSON backup whenever you want

## Cost
The app itself has no API key, backend, or subscription requirement.
GitHub Pages can host these static files for free.

## Important limitations
- OCR runs on-device/in-browser and can misread faded, crumpled, handwritten, or unusually formatted receipts.
- The first OCR use needs internet access to load the Tesseract.js library/language data from the CDN.
- Data is stored in the browser on that device. Clearing Safari website data can erase it.
- Use **Backup JSON** regularly if these are important tax records.

## Publish free with GitHub Pages
1. Create a GitHub repository.
2. Upload `index.html`, `manifest.json`, `sw.js`, `icon-192.png`, and `icon-512.png`.
3. In the repository, open **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Select the `main` branch and `/ (root)`, then Save.
6. GitHub will give you a `github.io` web address.
7. Open that address in Safari on iPhone.
8. Tap **Share → Add to Home Screen**.

No Render and no OpenAI API key needed.
