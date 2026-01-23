# iOS Web Push Notifications Test App

A Next.js Progressive Web App (PWA) demonstrating web push notifications on iOS devices using MagicBell. This template supports iOS 16.5+, desktop browsers, and Android devices.

Apple officially released web push notification support for iOS with iOS 16.5 in May 2023. This project provides a working implementation with proper HMAC authentication for secure communication with MagicBell's API.

## Features

- ✅ Web Push notifications on iOS 16.5+ (PWA required)
- ✅ Desktop and Android browser support
- ✅ Server-side HMAC authentication for security
- ✅ Automatic test notification on subscription
- ✅ Device-specific instructional UI
- ✅ Service Worker with push notification handling

## Prerequisites

- Node.js 18+ installed
- A MagicBell account (free tier available)
- For iOS testing: ngrok or similar tunneling tool (HTTPS required)
- iOS device with iOS 16.5 or later

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd webpush-ios-test
npm install
```

### Step 2: Create a MagicBell Account

1. Go to [https://www.magicbell.com](https://www.magicbell.com)
2. Sign up for a free account
3. Create a new project (or use an existing one)

### Step 3: Generate VAPID Keys

VAPID keys are required for web push notifications.

1. Go to [https://www.magicbell.com/tools/vapid-keys](https://www.magicbell.com/tools/vapid-keys)
2. Click **"Generate New Keys"**
3. **Save both keys** - you'll need them in the next step:
   - VAPID Public Key (starts with `B...`)
   - VAPID Private Key (long base64 string)

### Step 4: Configure Web Push Channel in MagicBell

This is a **critical step** - without this, the app will fail with 401 errors.

1. Log in to your MagicBell Dashboard at [https://app.magicbell.com](https://app.magicbell.com)
2. Navigate to **Channels** in the left sidebar
3. Find and click on **Web Push**
4. **Enable** the Web Push channel (toggle it ON)
5. Paste your **VAPID Public Key** in the Public Key field
6. Paste your **VAPID Private Key** in the Private Key field
7. Click **Save** or **Update**
8. Verify the channel shows as "Enabled"

### Step 5: Get Your API Credentials

1. In the MagicBell Dashboard, go to **Settings** → **API**
2. Copy your credentials:
   - **API Key** (starts with `pk_...`)
   - **API Secret** (starts with `sk_...`)

### Step 6: Configure Environment Variables

1. Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

2. Edit the `.env` file and add your credentials:

```bash
NEXT_PUBLIC_MAGICBELL_API_KEY=pk_your_api_key_here
MAGICBELL_API_SECRET=sk_your_api_secret_here
```

**Important Security Notes:**
- Never commit the `.env` file to version control
- The API Secret should remain server-side only
- The `.gitignore` file already excludes `.env` files

### Step 7: Start the Development Server

```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000) (or the next available port if 3000 is in use).

### Step 8: Test on Desktop Browser First

1. Open [http://localhost:3000](http://localhost:3000) in your browser
2. Click the **Subscribe** button
3. Grant notification permission when prompted
4. You should receive a test notification immediately
5. Check the browser console for any errors

If the Subscribe button is grayed out showing "Loading", check:
- Your Web Push channel is enabled in MagicBell Dashboard
- Your VAPID keys are correctly configured
- Your `.env` file has the correct credentials
- The dev server logs for any errors

## Testing on iOS Devices

iOS requires HTTPS for PWA installation and push notifications. Use ngrok to expose your local server.

### Step 1: Install ngrok

```bash
brew install ngrok
```

Or download from [https://ngrok.com](https://ngrok.com)

### Step 2: Start ngrok Tunnel

In a separate terminal window:

```bash
ngrok http 3000
```

Or if your dev server is on a different port:

```bash
ngrok http 3002
```

ngrok will provide an HTTPS URL like: `https://abc123.ngrok-free.app`

### Step 3: Install PWA on iOS Device

**Requirements:**
- iOS 16.5 or later
- Safari browser (required)
- HTTPS URL (provided by ngrok)

**Installation Steps:**

1. Open Safari on your iPhone
2. Navigate to the ngrok HTTPS URL (e.g., `https://abc123.ngrok-free.app`)
3. Wait for the page to fully load
4. Tap the **Share** icon (box with arrow pointing up)
5. Scroll down and tap **"Add to Home Screen"**
6. Name the app (e.g., "Push Test")
7. Tap **"Add"**
8. **Important:** Launch the app from the home screen icon (not from Safari)

### Step 4: Subscribe to Notifications

1. Launch the PWA from your home screen
2. Tap the **Subscribe** button
3. Grant notification permission when iOS prompts you
4. You should receive an automatic test notification
5. The subscription will appear in your MagicBell Dashboard under Subscribers/Devices

### Step 5: Send Test Notifications

**From MagicBell Dashboard:**
1. Go to Notifications → Send
2. Create a new notification with a title and message
3. Select your device subscription as the recipient
4. Send - the notification should appear on your iOS device

**Via API:**
```bash
curl -X POST https://api.magicbell.com/notifications \
  -H "X-MAGICBELL-API-KEY: your_api_key" \
  -H "X-MAGICBELL-API-SECRET: your_api_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "notification": {
      "title": "Test Notification",
      "message": "Testing iOS web push!"
    },
    "recipients": {
      "matches": [{"subscriber_id": "your_subscriber_id"}]
    }
  }'
```

## How It Works

### HMAC Authentication

This app implements server-side HMAC authentication for secure communication with MagicBell. Here's how it works:

1. **Client generates a user ID** - A unique ID is created and stored in localStorage
2. **Client requests HMAC** - The app calls `/api/hmac?userId=...` to get a cryptographic signature
3. **Server generates HMAC** - The API route creates an HMAC using the API Secret (server-side only)
4. **Client authenticates** - The HMAC is passed to `MagicBellProvider` as the `userKey` prop
5. **MagicBell validates** - All API requests include the HMAC for authentication

**Key Files:**
- `/src/pages/api/hmac.ts` - Server-side HMAC generation endpoint
- `/src/pages/_app.tsx` - HMAC fetching and MagicBellProvider configuration
- `/src/components/subscriber.tsx` - Subscription UI and logic
- `/src/services/subscriptionManager.ts` - Subscription management
- `/public/manifest.json` - PWA configuration
- `/public/sw.js` - Service Worker for push notification handling

## Troubleshooting

### Subscribe Button Stuck on "Loading"

**Cause:** Web Push channel not configured in MagicBell Dashboard

**Solution:**
1. Go to MagicBell Dashboard → Channels → Web Push
2. Ensure the channel is **enabled**
3. Verify VAPID keys are entered correctly
4. Save the configuration
5. Refresh the app

### 401 Unauthorized Error

**Cause:** HMAC authentication failure or invalid API credentials

**Solution:**
1. Verify your `.env` file has the correct API Key and Secret
2. Restart the dev server after changing `.env`
3. Check that your MagicBell project has HMAC enabled
4. Clear browser cache and reload

### Cannot Add to Home Screen on iOS

**Cause:** Not using HTTPS connection

**Solution:**
- Use ngrok to provide an HTTPS URL
- Local HTTP URLs don't work for PWA installation on iOS

### Notifications Not Received on iOS

**Possible causes and solutions:**

1. **App launched from Safari instead of home screen icon**
   - Delete the PWA and reinstall it
   - Always launch from the home screen

2. **Notification permissions denied**
   - Go to iPhone Settings → Notifications → [Your App]
   - Enable notifications

3. **VAPID keys not configured**
   - Check MagicBell Dashboard → Channels → Web Push
   - Ensure VAPID keys are saved

4. **iOS notification settings**
   - Check Do Not Disturb is off
   - Check Focus modes aren't blocking notifications

### ngrok Tunnel Disconnected

**Cause:** ngrok free tier disconnects after some time

**Solution:**
- Restart ngrok: `ngrok http 3000`
- Note the new URL
- Reinstall the PWA with the new URL

## Important Notes for iOS

- **PWA Installation Required:** Web push only works when the app is added to the home screen. Safari alone won't receive notifications.
- **HTTPS Required:** iOS requires HTTPS for PWA installation (use ngrok for local development)
- **Launch from Home Screen:** Always open the app from the home screen icon, not Safari
- **iOS 16.5+ Required:** Older iOS versions don't support web push
- **Safari Only:** Other browsers (Chrome, Firefox) on iOS don't support web push yet
- **Notification Limits:** iOS has stricter notification limits than desktop browsers

## Project Structure

```
├── public/
│   ├── manifest.json          # PWA configuration
│   ├── sw.js                  # Service Worker for push notifications
│   └── icons/                 # App icons for PWA
├── src/
│   ├── components/
│   │   ├── subscriber.tsx     # Main subscription UI component
│   │   └── ...
│   ├── pages/
│   │   ├── _app.tsx           # App wrapper with MagicBellProvider
│   │   ├── index.tsx          # Home page
│   │   └── api/
│   │       ├── hmac.ts        # Server-side HMAC generation
│   │       └── welcome.ts     # Send welcome notification
│   ├── services/
│   │   └── subscriptionManager.ts  # Subscription logic
│   └── hooks/
│       └── useDeviceInfo.tsx  # Device detection
├── .env                       # Your credentials (DO NOT COMMIT)
├── .env.example               # Template for environment variables
└── package.json
```

## Deployment

For production deployment:

1. Deploy to a platform like Vercel, Netlify, or your own server
2. Set environment variables in your hosting platform
3. Update the manifest.json with your production domain
4. Users can install the PWA directly from your production URL
5. No ngrok needed - your domain provides HTTPS

## Resources

- [MagicBell Documentation](https://www.magicbell.com/docs)
- [MagicBell Web Push Guide](https://www.magicbell.com/docs/channels/web_push)
- [VAPID Key Generator](https://www.magicbell.com/tools/vapid-keys)
- [Apple's Web Push Documentation](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/)
- [Web Push Notifications on iOS](https://www.magicbell.com/blog/ios-now-supports-web-push-notifications-and-why-you-should-care)

## Support

- For MagicBell support: [GitHub Discussions](https://github.com/orgs/magicbell/discussions)
- For app-specific issues: Open an issue on this repository

## License

This project is based on MagicBell's official webpush-ios-template.
