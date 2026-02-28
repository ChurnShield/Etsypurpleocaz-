#!/usr/bin/env node
/**
 * PURPLEOCAZ — ETSY LISTING PUBLISHER
 * =====================================
 *
 * Creates the Tattoo Studio Business Kit listing on Etsy:
 * 1. Authenticates with Etsy via OAuth2 (opens browser for consent)
 * 2. Creates the listing with title, description, tags, price
 * 3. Uploads all 6 listing images
 * 4. Uploads the delivery ZIP as the digital file
 */

import http from 'http';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

// ============================================
// CONFIGURATION
// ============================================

// Load API key from .env file
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const envPath = path.join(__dirname, '.env');
let ETSY_API_KEYSTRING = '';
let ETSY_SHARED_SECRET = '';
try {
  const envContent = fs.readFileSync(envPath, 'utf8');
  const keyMatch = envContent.match(/ETSY_API_KEYSTRING=(.+)/);
  const secretMatch = envContent.match(/ETSY_SHARED_SECRET=(.+)/);
  if (keyMatch) ETSY_API_KEYSTRING = keyMatch[1].trim();
  if (secretMatch) ETSY_SHARED_SECRET = secretMatch[1].trim();
} catch (e) {
  // fallback
}
if (!ETSY_API_KEYSTRING || !ETSY_SHARED_SECRET) {
  console.error('Could not load ETSY_API_KEYSTRING or ETSY_SHARED_SECRET from .env');
  process.exit(1);
}

// x-api-key header needs keystring:shared_secret
// client_id in OAuth calls uses just the keystring
const ETSY_X_API_KEY = `${ETSY_API_KEYSTRING}:${ETSY_SHARED_SECRET}`;

const CONFIG = {
  ETSY_API_KEYSTRING,
  ETSY_X_API_KEY,
  REDIRECT_URI: 'http://localhost:3847/callback',
  SCOPES: 'shops_r shops_w listings_r listings_w listings_d',

  // File paths
  LISTING_IMAGES_DIR: path.join(process.env.HOME || process.env.USERPROFILE, 'OneDrive', 'Desktop'),
  DELIVERY_ZIP: path.join(process.env.HOME || process.env.USERPROFILE, 'OneDrive', 'Desktop', 'Tattoo-Studio-Business-Kit-DELIVERY.zip'),

  // Listing details
  LISTING: {
    title: 'Tattoo Studio Business Kit | 36 Print-Ready Templates | Consultation Form, Aftercare, Release, Price List, Social Media',
    description: `\u2605 THE COMPLETE TATTOO STUDIO BUSINESS KIT \u2605

Everything your tattoo studio needs -- beautifully designed, print-ready, and delivered instantly.

This professional bundle includes 36 pages across 9 essential templates, available in 4 style variants so you can match your studio's brand perfectly.

------------------------------

WHAT'S INCLUDED (9 Templates x 4 Variants = 36 Pages)

* Consultation Form -- Client info, tattoo details, front & back body placement diagrams, health & medical screening
* Aftercare Card (3.5x2") -- Do's & Don'ts, 4-stage healing timeline, print-ready card stock size
* Release & Liability Waiver -- 7 initialled consent clauses, dual signatures, photo consent
* Client Intake Form -- Registration, tattoo history, style preferences, communication preferences
* Price List / Service Menu (5.5x8.5") -- Hourly rates, flash pricing, cover-ups, add-ons, policies
* Gift Certificate (6x4") -- Fillable amount, personal message, gift code, beautiful presentation
* Social Media Templates -- Instagram post (1080x1080), story (1080x1920), and testimonial post
* Booking Confirmation -- Appointment details, payment summary, pre-appointment checklist
* Thank You & Review Card (5x3.5") -- Referral code, QR code placeholder, step-by-step review guide

------------------------------

4 STYLE VARIANTS INCLUDED

Classic -- Warm cream with gold accents (print-friendly, ~8% ink coverage)
Clean -- Crisp white with slate blue accents (modern, minimal)
Warm -- Parchment with deep burgundy accents (vintage, traditional)
Bold -- Dark background with gold accents (digital use -- perfect for iPad or screen display)

------------------------------

WHAT YOU RECEIVE

- Print-Ready PDF files -- professionally formatted, ready to print straight away
- Organised in folders by variant (Classic, Clean, Warm, Bold)
- Correct print dimensions for every template
- Instant digital download

FREE BONUS UPDATE: Editable Canva template links will be added as a free update. When ready, you'll receive a notification from Etsy to download the updated files -- giving you full customisation with your studio name, logo, and branding. No extra charge, no need to repurchase.

------------------------------

WHY TATTOO ARTISTS LOVE THIS KIT

- Body placement diagrams -- clients mark front & back
- Tattoo style checkboxes (Traditional, Fine Line, Blackwork, Realism, Japanese, Geometric + more)
- 4-stage healing timeline on the aftercare card (Days 1-3, Days 4-14, Weeks 3-4, Months 2-3)
- 7 individually initialled consent clauses -- proper legal structuring
- Flash day pricing highlighted on the service menu
- Pre-appointment checklist (eat well, hydrate, no blood thinners, bring snacks)
- Referral programme built into the thank you card (friend code + client credit)
- QR code placeholder for Google / Yelp / Facebook reviews
- Print-friendly designs -- low ink coverage means cheap to print in bulk

------------------------------

HOW TO USE

1. Purchase and download instantly
2. Open the PDF files -- they're ready to print right away
3. Print at home, at a local print shop, or use digitally on an iPad/tablet
4. When the free Canva update arrives, customise with your studio details

No design skills needed. No software to install.

------------------------------

VALUE BREAKDOWN

If purchased individually at $4.99 each, these 9 templates would cost $44.91.
This bundle saves you over 33% -- just $29.99 for the complete set.

------------------------------

PLEASE NOTE

- This is a DIGITAL DOWNLOAD -- no physical items will be shipped
- You receive print-ready PDF files, organised by colour variant
- Editable Canva templates will be added as a FREE update (no extra cost)
- Colours may vary slightly between screens and print
- The legal forms are templates -- we recommend having them reviewed by a legal professional for your jurisdiction

Questions? We're happy to help -- just send us a message!

PurpleOcaz -- Designed with love for tattoo artists everywhere`,
    tags: [
      'tattoo templates', 'tattoo business kit', 'tattoo forms',
      'consultation form', 'aftercare card', 'tattoo artist',
      'tattoo price list', 'tattoo waiver', 'studio templates',
      'editable templates', 'digital download', 'tattoo shop forms',
      'business bundle'
    ],
    price: 29.99,
    quantity: 999,
    who_made: 'i_did',
    when_made: 'made_to_order',
    taxonomy_id: 2078,
    type: 'download',
    is_digital: true,
  },

  IMAGE_FILES: [
    '01-Hero-Bundle-Overview.png',
    '02-Whats-Included-Grid.png',
    '03-Four-Style-Variants.png',
    '04-Value-Breakdown.png',
    '05-How-It-Works.png',
    '06-Designed-For-Tattoo-Artists.png',
  ],
};

// ============================================
// OAUTH2 PKCE HELPERS
// ============================================

function generateCodeVerifier() {
  return crypto.randomBytes(32).toString('base64url');
}

function generateCodeChallenge(verifier) {
  return crypto.createHash('sha256').update(verifier).digest('base64url');
}

function generateState() {
  return crypto.randomBytes(16).toString('hex');
}

// ============================================
// OAUTH2 FLOW
// ============================================

async function authenticate() {
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);
  const state = generateState();

  const authUrl = `https://www.etsy.com/oauth/connect?` +
    `response_type=code&` +
    `redirect_uri=${encodeURIComponent(CONFIG.REDIRECT_URI)}&` +
    `scope=${encodeURIComponent(CONFIG.SCOPES)}&` +
    `client_id=${CONFIG.ETSY_API_KEYSTRING}&` +
    `state=${state}&` +
    `code_challenge=${codeChallenge}&` +
    `code_challenge_method=S256`;

  console.log('\n========================================');
  console.log('  ETSY AUTHENTICATION');
  console.log('========================================');
  console.log('\nOpening your browser to authorise with Etsy...');
  console.log('\nIf it doesn\'t open automatically, visit this URL:\n');
  console.log(authUrl);
  console.log('\nWaiting for authorisation callback...\n');

  try {
    const platform = process.platform;
    if (platform === 'darwin') execSync(`open "${authUrl}"`);
    else if (platform === 'win32') execSync(`start "" "${authUrl}"`);
    else execSync(`xdg-open "${authUrl}"`);
  } catch (e) {
    console.log('(Could not open browser automatically -- please visit the URL above)');
  }

  return new Promise((resolve, reject) => {
    const server = http.createServer(async (req, res) => {
      const url = new URL(req.url, `http://localhost:3847`);

      if (url.pathname === '/callback') {
        const code = url.searchParams.get('code');
        const returnedState = url.searchParams.get('state');

        if (returnedState !== state) {
          res.writeHead(400);
          res.end('State mismatch -- authentication failed');
          reject(new Error('State mismatch'));
          server.close();
          return;
        }

        try {
          const tokenResponse = await fetch('https://api.etsy.com/v3/public/oauth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
              grant_type: 'authorization_code',
              client_id: CONFIG.ETSY_API_KEYSTRING,
              redirect_uri: CONFIG.REDIRECT_URI,
              code: code,
              code_verifier: codeVerifier,
            }),
          });

          const tokens = await tokenResponse.json();

          if (tokens.access_token) {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(`
              <html><body style="font-family:system-ui;display:flex;align-items:center;justify-content:center;height:100vh;background:#0D0D0D;color:#C4A265;">
                <div style="text-align:center">
                  <h1>Authenticated!</h1>
                  <p style="color:#888">You can close this window and return to the terminal.</p>
                </div>
              </body></html>
            `);

            const tokenFile = path.join(__dirname, 'etsy-publish-tokens.json');
            fs.writeFileSync(tokenFile, JSON.stringify(tokens, null, 2));
            console.log('Authentication successful! Token saved.');
            console.log(`   Access token expires in: ${tokens.expires_in} seconds`);
            console.log(`   Refresh token valid for: 90 days\n`);

            resolve(tokens);
          } else {
            res.writeHead(400);
            res.end('Token exchange failed: ' + JSON.stringify(tokens));
            reject(new Error('Token exchange failed: ' + JSON.stringify(tokens)));
          }
        } catch (err) {
          res.writeHead(500);
          res.end('Error: ' + err.message);
          reject(err);
        }

        server.close();
      }
    });

    server.listen(3847, () => {
      console.log('Callback server listening on port 3847...');
    });

    setTimeout(() => {
      server.close();
      reject(new Error('Authentication timed out after 5 minutes'));
    }, 300000);
  });
}

// ============================================
// ETSY API HELPERS
// ============================================

async function etsyGet(endpoint, accessToken) {
  const response = await fetch(`https://openapi.etsy.com/v3${endpoint}`, {
    headers: {
      'x-api-key': CONFIG.ETSY_X_API_KEY,
      'Authorization': `Bearer ${accessToken}`,
    },
  });
  return response.json();
}

async function etsyPost(endpoint, accessToken, body) {
  const response = await fetch(`https://openapi.etsy.com/v3${endpoint}`, {
    method: 'POST',
    headers: {
      'x-api-key': CONFIG.ETSY_X_API_KEY,
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams(body),
  });
  return response.json();
}

async function etsyPatch(endpoint, accessToken, body) {
  const response = await fetch(`https://openapi.etsy.com/v3${endpoint}`, {
    method: 'PATCH',
    headers: {
      'x-api-key': CONFIG.ETSY_X_API_KEY,
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams(body),
  });
  return response.json();
}

async function uploadImage(shopId, listingId, accessToken, imagePath, rank) {
  const imageData = fs.readFileSync(imagePath);
  const fileName = path.basename(imagePath);

  const boundary = '----FormBoundary' + crypto.randomBytes(16).toString('hex');

  const bodyBuffer = Buffer.concat([
    Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="image"; filename="${fileName}"\r\nContent-Type: image/png\r\n\r\n`),
    imageData,
    Buffer.from(`\r\n--${boundary}\r\nContent-Disposition: form-data; name="rank"\r\n\r\n${rank}\r\n--${boundary}--\r\n`),
  ]);

  const response = await fetch(`https://openapi.etsy.com/v3/application/shops/${shopId}/listings/${listingId}/images`, {
    method: 'POST',
    headers: {
      'x-api-key': CONFIG.ETSY_X_API_KEY,
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
    },
    body: bodyBuffer,
  });

  return response.json();
}

async function uploadDigitalFile(shopId, listingId, accessToken, filePath) {
  const fileData = fs.readFileSync(filePath);
  const fileName = path.basename(filePath);

  const boundary = '----FormBoundary' + crypto.randomBytes(16).toString('hex');

  const bodyBuffer = Buffer.concat([
    Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="file"; filename="${fileName}"\r\nContent-Type: application/zip\r\n\r\n`),
    fileData,
    Buffer.from(`\r\n--${boundary}\r\nContent-Disposition: form-data; name="name"\r\n\r\n${fileName}\r\n--${boundary}--\r\n`),
  ]);

  const response = await fetch(`https://openapi.etsy.com/v3/application/shops/${shopId}/listings/${listingId}/files`, {
    method: 'POST',
    headers: {
      'x-api-key': CONFIG.ETSY_X_API_KEY,
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
    },
    body: bodyBuffer,
  });

  return response.json();
}

// ============================================
// MAIN FLOW
// ============================================

async function main() {
  console.log('');
  console.log('========================================');
  console.log('  PURPLEOCAZ -- ETSY LISTING PUBLISHER');
  console.log('  Tattoo Studio Business Kit');
  console.log('========================================');

  // ---- STEP 0: Check for files ----
  console.log('\nSTEP 0: Checking files...');

  const imagesDir = CONFIG.LISTING_IMAGES_DIR;
  const zipPath = CONFIG.DELIVERY_ZIP;

  if (!fs.existsSync(zipPath)) {
    console.log(`Could not find delivery ZIP at: ${zipPath}`);
    process.exit(1);
  }

  for (const img of CONFIG.IMAGE_FILES) {
    const imgPath = path.join(imagesDir, img);
    if (!fs.existsSync(imgPath)) {
      console.log(`Missing image: ${img}`);
      process.exit(1);
    }
  }
  console.log(`   Images: ${imagesDir}`);
  console.log(`   ZIP: ${zipPath} (${(fs.statSync(zipPath).size / 1024 / 1024).toFixed(1)}MB)`);
  console.log('   All files found\n');

  // ---- STEP 1: Authenticate ----
  let tokens;
  const tokenFile = path.join(__dirname, 'etsy-publish-tokens.json');

  if (fs.existsSync(tokenFile)) {
    try {
      tokens = JSON.parse(fs.readFileSync(tokenFile, 'utf8'));
      console.log('Found saved tokens. Testing if still valid...');

      const testResult = await etsyGet('/application/users/me', tokens.access_token);

      if (testResult.user_id) {
        console.log(`   Logged in as user: ${testResult.user_id}`);
      } else if (tokens.refresh_token) {
        console.log('   Access token expired. Refreshing...');
        const refreshResponse = await fetch('https://api.etsy.com/v3/public/oauth/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            grant_type: 'refresh_token',
            client_id: CONFIG.ETSY_API_KEYSTRING,
            refresh_token: tokens.refresh_token,
          }),
        });
        tokens = await refreshResponse.json();
        if (tokens.access_token) {
          fs.writeFileSync(tokenFile, JSON.stringify(tokens, null, 2));
          console.log('   Token refreshed successfully');
        } else {
          console.log('   Refresh failed -- need to re-authenticate');
          tokens = null;
        }
      } else {
        tokens = null;
      }
    } catch (e) {
      console.log('   Saved tokens invalid -- need to re-authenticate');
      tokens = null;
    }
  }

  if (!tokens || !tokens.access_token) {
    tokens = await authenticate();
  }

  const accessToken = tokens.access_token;

  // ---- STEP 2: Get Shop ID ----
  console.log('\nSTEP 2: Getting your shop details...');
  const meResponse = await etsyGet('/application/users/me', accessToken);
  const userId = meResponse.user_id;

  const shopResponse = await etsyGet(`/application/users/${userId}/shops`, accessToken);
  const shopId = shopResponse.shop_id || shopResponse.results?.[0]?.shop_id;
  const shopName = shopResponse.shop_name || shopResponse.results?.[0]?.shop_name;

  if (!shopId) {
    console.log('Could not find your shop. Make sure your API key is linked to your Etsy account.');
    process.exit(1);
  }

  console.log(`   Shop: ${shopName} (ID: ${shopId})\n`);

  // ---- STEP 3: Create Listing ----
  console.log('STEP 3: Creating listing...');

  const listingData = {
    title: CONFIG.LISTING.title,
    description: CONFIG.LISTING.description,
    price: CONFIG.LISTING.price,
    quantity: CONFIG.LISTING.quantity,
    who_made: CONFIG.LISTING.who_made,
    when_made: CONFIG.LISTING.when_made,
    taxonomy_id: CONFIG.LISTING.taxonomy_id,
    type: CONFIG.LISTING.type,
    is_digital: CONFIG.LISTING.is_digital,
    tags: CONFIG.LISTING.tags.join(','),
  };

  const listingResponse = await etsyPost(
    `/application/shops/${shopId}/listings`,
    accessToken,
    listingData
  );

  if (listingResponse.listing_id) {
    console.log(`   Listing created! ID: ${listingResponse.listing_id}`);
    console.log(`   Status: ${listingResponse.state} (draft until published)\n`);
  } else {
    console.log('   Failed to create listing:', JSON.stringify(listingResponse, null, 2));
    process.exit(1);
  }

  const listingId = listingResponse.listing_id;

  // ---- STEP 4: Upload Images ----
  console.log('STEP 4: Uploading listing images...');

  for (let i = 0; i < CONFIG.IMAGE_FILES.length; i++) {
    const imgPath = path.join(imagesDir, CONFIG.IMAGE_FILES[i]);
    const rank = i + 1;
    console.log(`   Uploading ${CONFIG.IMAGE_FILES[i]} (rank ${rank})...`);

    const imgResult = await uploadImage(shopId, listingId, accessToken, imgPath, rank);

    if (imgResult.listing_image_id) {
      console.log(`   Image ${rank} uploaded`);
    } else {
      console.log(`   Image ${rank} issue:`, JSON.stringify(imgResult));
    }
  }

  console.log('');

  // ---- STEP 5: Upload Digital File ----
  console.log('STEP 5: Uploading digital delivery file...');
  console.log(`   File: ${path.basename(zipPath)} (${(fs.statSync(zipPath).size / 1024 / 1024).toFixed(1)}MB)`);

  const fileResult = await uploadDigitalFile(shopId, listingId, accessToken, zipPath);

  if (fileResult.listing_file_id) {
    console.log(`   Digital file uploaded! File ID: ${fileResult.listing_file_id}`);
  } else {
    console.log('   File upload issue:', JSON.stringify(fileResult));
  }

  // ---- STEP 6: Activate Digital Delivery ----
  // Required PATCH after file upload so Etsy UI recognises the file
  // and buyers can actually download it
  console.log('\nSTEP 6: Activating digital delivery...');

  const patchResult = await etsyPatch(
    `/application/shops/${shopId}/listings/${listingId}`,
    accessToken,
    { type: 'download' }
  );

  if (patchResult.listing_id) {
    console.log(`   Digital delivery activated (state: ${patchResult.state})\n`);
  } else {
    console.log('   Activation issue:', JSON.stringify(patchResult));
  }

  // ---- DONE ----
  console.log('========================================');
  console.log('  LISTING CREATED SUCCESSFULLY!');
  console.log('========================================');
  console.log('');
  console.log(`   Listing ID: ${listingId}`);
  console.log(`   Status: ${listingResponse.state}`);
  console.log(`   URL: https://www.etsy.com/listing/${listingId}`);
  console.log('');
  console.log('   The listing is in DRAFT status.');
  console.log('   Go to Etsy Shop Manager -> Listings -> Drafts');
  console.log('   Review it and click PUBLISH when ready.');
  console.log('');
}

main().catch(err => {
  console.error('\nError:', err.message);
  process.exit(1);
});
