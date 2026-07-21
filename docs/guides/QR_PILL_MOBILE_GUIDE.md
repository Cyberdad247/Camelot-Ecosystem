# QR Pill Mobile Activation Guide

**How to Activate QR Pill from Your Mobile Device**

---

## Overview

The QR Pill can be activated from any mobile device using:
1. **Native camera** (recommended) — point phone camera at printed QR code
2. **Image upload** — upload QR code screenshot/image from photo library
3. **QR data entry** — paste pill activation URL directly

---

## How to Get the QR Code

### Option A: Print & Ship
```
1. Vizion (Sovereign Commander) approves pill activation
2. CAMELOT-OS generates QR code
3. QR code printed on physical label/card
4. Sent via postal mail to user
5. User scans with mobile phone
```

### Option B: Email/SMS
```
1. Vizion generates QR activation link
2. Link sent via encrypted email or SMS
3. User clicks link on mobile phone
4. Browser opens activation page
5. User scans QR from computer screen/printed copy
```

### Option C: WhatsApp/Telegram
```
1. Vizion shares QR code image via WhatsApp/Telegram
2. User saves image to phone
3. Opens activation page
4. Uploads saved QR image
5. Pill activates
```

---

## Step-by-Step Activation (Mobile)

### **Scenario 1: Camera Scan**

**Prerequisites**:
- Mobile device with camera
- QR code visible (printed or on screen)
- Internet connection (WiFi or mobile data)

**Steps**:

1. **Receive Link**
   ```
   User receives: https://camelot-os.local/qr-pill/activate/a1b2c3d4e5f6g7h8
   (via email, SMS, WhatsApp, etc.)
   ```

2. **Open Link on Mobile**
   ```
   - Click link on mobile phone
   - Browser opens activation page
   - See: "QR Pill Activation" header
   ```

3. **Request Camera Permission**
   ```
   - Tap "Start Camera" button
   - Browser asks: "Allow access to camera?"
   - Tap "Allow" or "Yes"
   ```

4. **Position Camera at QR Code**
   ```
   - Point camera at printed QR code or screen QR
   - Keep steady for 1-2 seconds
   - Focus on QR code (green frame appears)
   ```

5. **QR Detected**
   ```
   - Browser automatically detects QR
   - Displays: "QR Code Detected"
   - Shows extracted pill_id
   - Camera stops automatically
   ```

6. **Confirm Activation**
   ```
   - Tap "Confirm Activation" button
   - System sends activation to CAMELOT-OS
   - Shows: "Activating..." spinner
   ```

7. **Approval & Activation**
   ```
   - Vizion (Sovereign Commander) approves
   - Pill begins self-bootstrap
   - Page shows: "✓ Activation successful!"
   - Real-time status updates appear
   ```

8. **Completion**
   ```
   - Pill transitions to LIVE state
   - Health checks begin
   - Bifrost ledger updated
   - Session expires (1 hour TTL)
   ```

---

### **Scenario 2: Image Upload**

**Prerequisites**:
- Mobile device with photo library
- QR code image saved to phone
- Internet connection

**Steps**:

1. **Open Activation Page**
   ```
   Same as above, but skip camera permission
   ```

2. **Upload QR Image**
   ```
   - Scroll to "Option 2: Upload QR Image"
   - Tap upload area (or drag if desktop)
   - Select QR code from photo library
   ```

3. **Processing**
   ```
   - Browser decodes QR from image
   - Displays: "QR Code Detected"
   - Shows extracted pill_id
   ```

4. **Confirm & Activate**
   ```
   Same as Scenario 1, steps 6-8
   ```

---

## QR Code Generation & Format

### QR Code Data Format
```
qr_pill://{pill_id}?token={activation_token}&expires={timestamp}

Example:
qr_pill://test_pill_abc123?token=eyJhbGci...&expires=2026-06-15T15:00:00Z
```

### Generate QR Code (Python)
```python
from control_plane.qr_pill_mobile import get_mobile_activation
import qrcode

mobile = get_mobile_activation()
activation_link = mobile.generate_activation_link("pill_abc123")

# Create QR code image
qr = qrcode.QRCode()
qr.add_data(activation_link)
qr.make()
img = qr.make_image()
img.save("qr_pill_abc123.png")
```

### Generate QR Code (Online Tools)
```
1. Go to https://qrcode.com or https://www.qr-code-generator.com/
2. Paste activation link
3. Download QR code image
4. Print or share
```

---

## Mobile Browser Requirements

| Feature | Chrome | Safari | Firefox | Edge |
|---------|--------|--------|---------|------|
| Camera Access | ✓ | ✓ (iOS 14+) | ✓ | ✓ |
| File Upload | ✓ | ✓ | ✓ | ✓ |
| WebSocket | ✓ | ✓ | ✓ | ✓ |
| HTTPS Required | ✓ | ✓ | ✓ | ✓ |

**Note**: Camera access requires HTTPS (except localhost). HTTP will not show camera option.

---

## Security Features

### 1. Session-Based Activation
```
- Each activation link has unique session_id
- Session expires after 1 hour
- Cannot be reused
- One-time activation only
```

### 2. HTTPS/TLS Encryption
```
- All traffic encrypted
- Prevents man-in-the-middle attacks
- QR data never sent in plain text
```

### 3. IP Address Tracking
```
- Activation logged with IP address
- User agent recorded
- Timestamp captured
- Audit trail in SOVEREIGNTY_LEDGER.md
```

### 4. Sovereign Commander Approval
```
- All activations require Vizion approval
- Critical operations block until approved
- Auto-escalation if activation fails
```

### 5. Activation Token
```
- QR includes expiring activation token
- Token validates on server
- Prevents old QR codes from working
- Token refresh capability
```

---

## Troubleshooting

### Camera Not Working

**Problem**: "Allow access to camera?" prompt doesn't appear

**Solution**:
1. Check HTTPS connection (not HTTP)
2. Check browser permissions settings
3. Try different browser
4. Use image upload instead

**Code**:
```javascript
// Browser console diagnostic
navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    console.log("Available cameras:", devices);
  });
```

### QR Code Not Detected

**Problem**: Camera shows video but QR not detected

**Solution**:
1. Ensure QR code is clearly visible
2. Adjust lighting (not too bright/dark)
3. Hold phone steady for 2+ seconds
4. Try different angle
5. Use image upload instead

### Connection Error

**Problem**: "Network error" when confirming activation

**Solution**:
1. Check internet connection (WiFi or data)
2. Check that CAMELOT-OS backend is running
3. Try again in a few seconds
4. Check firewall settings

### Session Expired

**Problem**: "Session expired" message after 1+ hour

**Solution**:
1. Request new activation link from Vizion
2. New link generates new session
3. Try activation again

---

## Real-Time Status Updates (WebSocket)

After activation is confirmed, the page connects to WebSocket for real-time updates:

```javascript
// WebSocket connection
const ws = new WebSocket(`wss://camelot-os.local/api/qr-pill/status/{session_id}`);

ws.onmessage = (event) => {
    const status = JSON.parse(event.data);
    // Display real-time status
    console.log(status.message);
};
```

### Status Update Sequence
```
1. "Activation request received"
2. "Waiting for Sovereign Commander approval"
3. "Approval granted by Vizion"
4. "Initializing pill..."
5. "Connecting to Bifrost bridge..."
6. "Connecting to Knight brain..."
7. "Starting self-bootstrap..."
8. "Bootstrap step 1/11: Creating pill directory..."
9. "Bootstrap step 2/11: Creating sovereignty ledger..."
... (more steps)
10. "Bootstrap complete"
11. "Running verification checks..."
12. "✓ All checks passed"
13. "Pill is now LIVE"
14. "Health check scheduled for 24h"
```

---

## Advanced: Custom QR Data

If you need to include custom data in QR code:

```
qr_pill://{pill_id}?token={token}&expires={ts}&custom_field=value
```

### Parse Custom Fields (Browser)
```javascript
function parseQRData(qrData) {
    const [scheme, rest] = qrData.split("://");
    const [pillId, queryStr] = rest.split("?");
    const params = new URLSearchParams(queryStr);
    
    return {
        pill_id: pillId,
        token: params.get("token"),
        expires: params.get("expires"),
        custom: params.get("custom_field")
    };
}
```

---

## Enterprise Deployment

### Bulk Activation
```python
from control_plane.qr_pill_mobile import get_mobile_activation
import csv

mobile = get_mobile_activation()

# Generate 100 pills with QR codes
with open("pills.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["pill_id", "activation_link", "qr_image_path"])
    
    for i in range(100):
        pill_id = f"pill_{i:04d}"
        link = mobile.generate_activation_link(pill_id)
        qr_path = f"qr_codes/pill_{i:04d}.png"
        writer.writerow([pill_id, link, qr_path])
```

### Distribute via Email
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Email template with QR code image attachment
def send_activation_email(email, pill_id, qr_image_path):
    msg = MIMEText(f"""
    Your QR Pill is ready for activation!
    
    Pill ID: {pill_id}
    
    Scan the attached QR code with your mobile device
    or click the link below:
    
    https://camelot-os.local/qr-pill/activate/{session_id}
    """)
    
    # Attach QR image
    with open(qr_image_path, 'rb') as f:
        img = MIMEImage(f.read())
        msg.attach(img)
    
    # Send email
    smtplib.SMTP(...).sendmail(...)
```

---

## Mobile App Alternative

For production deployment, consider native mobile app:

```swift
// iOS (Swift)
import Vision
import AVFoundation

class QRPillScanner: NSObject, AVCaptureMetadataOutputObjectsDelegate {
    func metadataOutput(_ output: AVCaptureMetadataOutput,
                       didOutput metadataObjects: [AVMetadataObject],
                       from connection: AVCaptureConnection) {
        // Process QR code
        if let qr = metadataObjects.first as? AVMetadataMachineReadableCodeObject {
            let qrData = qr.stringValue
            // POST to activation endpoint
        }
    }
}
```

```kotlin
// Android (Kotlin)
import androidx.camera.core.Camera
import com.google.mlkit.vision.barcode.BarcodeScanning

class QRPillScanner {
    fun scanQRCode(imageProxy: ImageProxy) {
        val image = imageProxy.image ?: return
        val inputImage = InputImage.fromMediaImage(image, imageProxy.imageInfo.rotationDegrees)
        
        BarcodeScanning.getClient()
            .process(inputImage)
            .addOnSuccessListener { barcodes ->
                for (barcode in barcodes) {
                    val qrData = barcode.rawValue
                    // POST to activation endpoint
                }
            }
    }
}
```

---

## Summary

**Mobile QR Pill Activation Flow**:

```
1. User receives activation link (SMS/email/WhatsApp)
2. User clicks link on mobile phone
3. Browser opens activation page (responsive design)
4. User chooses: Camera Scan OR Image Upload
5. QR code detected and decoded
6. Activation confirmed by user
7. Backend sends activation to Sovereign Commander
8. Vizion approves (manual or auto-gate)
9. QR Pill begins self-bootstrap
10. Real-time status updates via WebSocket
11. Pill reaches LIVE state
12. Session expires (audit trail complete)
```

**Security**: HTTPS + TLS, IP tracking, Sovereign Commander approval, session expiration, activation tokens.

**User Experience**: Works on any mobile browser (Chrome, Safari), no app installation required, intuitive UI, real-time feedback.
