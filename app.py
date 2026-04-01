from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════
# CONFIGURACIÓN EMAIL
# ═══════════════════════════════════════

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "your-email@gmail.com")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "your-app-password")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "recipient@example.com")

# ═══════════════════════════════════════
# ENDPOINT DE FORMULARIO
# ═══════════════════════════════════════

@app.route("/api/quote-request", methods=["POST"])
def quote_request():
    try:
        data = request.json
        
        # Validar datos requeridos
        name = data.get("name", "").strip()
        address = data.get("address", "").strip()
        phone = data.get("phone", "").strip()
        service = data.get("service", "Not specified")
        details = data.get("details", "").strip()
        
        if not name or not address or not phone:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Enviar email a empresa
        email_sent = send_quote_email(name, address, phone, service, details)
        
        if email_sent:
            return jsonify({
                "success": True, 
                "message": "Quote request received! We'll contact you within 2 hours."
            }), 200
        else:
            return jsonify({
                "success": False, 
                "error": "Failed to process request. Please try again."
            }), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# ═══════════════════════════════════════
# FUNCIÓN ENVIAR EMAIL
# ═══════════════════════════════════════

def send_quote_email(name, address, phone, service, details):
    """Envía email a la empresa con datos del formulario"""
    
    try:
        # Crear mensaje
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🟨 NEW QUOTE REQUEST: {name} - {service}"
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # HTML body (profesional)
        html_body = f"""
        <html style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
          <body>
            <div style="max-width: 600px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
              
              <!-- Header -->
              <div style="border-bottom: 3px solid #f5a623; padding-bottom: 20px; margin-bottom: 20px;">
                <h1 style="color: #0a0a0a; margin: 0; font-size: 24px;">New Quote Request 📋</h1>
                <p style="color: #666; margin: 5px 0 0 0; font-size: 12px;">Received: {timestamp}</p>
              </div>
              
              <!-- Content -->
              <table style="width: 100%; margin-bottom: 25px;">
                <tr>
                  <td style="padding: 12px 0; border-bottom: 1px solid #eee;">
                    <strong style="color: #0a0a0a; display: block; margin-bottom: 4px;">Full Name</strong>
                    <span style="color: #333; font-size: 14px;">{name}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 12px 0; border-bottom: 1px solid #eee;">
                    <strong style="color: #0a0a0a; display: block; margin-bottom: 4px;">Address</strong>
                    <span style="color: #333; font-size: 14px;">{address}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 12px 0; border-bottom: 1px solid #eee;">
                    <strong style="color: #0a0a0a; display: block; margin-bottom: 4px;">Phone</strong>
                    <span style="color: #333; font-size: 14px; font-weight: bold;">
                      <a href="tel:{phone}" style="color: #f5a623; text-decoration: none;">{phone}</a>
                    </span>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 12px 0; border-bottom: 1px solid #eee;">
                    <strong style="color: #0a0a0a; display: block; margin-bottom: 4px;">Service Requested</strong>
                    <span style="color: #333; font-size: 14px; background: rgba(245,166,35,0.1); padding: 6px 12px; border-radius: 4px; display: inline-block;">{service}</span>
                  </td>
                </tr>
                {f'<tr><td style="padding: 12px 0;"><strong style="color: #0a0a0a; display: block; margin-bottom: 4px;">Additional Details</strong><span style="color: #333; font-size: 14px; white-space: pre-wrap;">{details}</span></td></tr>' if details else ''}
              </table>
              
              <!-- Action Button -->
              <div style="text-align: center; margin: 30px 0;">
                <a href="tel:{phone}" style="background: #f5a623; color: #0a0a0a; padding: 14px 40px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; text-transform: uppercase; letter-spacing: 1px;">
                  📞 Call Client Immediately
                </a>
              </div>
              
              <!-- Footer -->
              <div style="background: #f9f9f9; padding: 15px; border-radius: 4px; border-left: 3px solid #f5a623; margin-top: 25px; font-size: 12px; color: #666;">
                <p style="margin: 0;"><strong>⏱️ Follow-up Required:</strong> Within 2 hours as promised to client</p>
                <p style="margin: 5px 0 0 0;">This request came from {timestamp}</p>
              </div>
              
            </div>
          </body>
        </html>
        """
        
        # Plain text fallback
        text_body = f"""
NEW QUOTE REQUEST
================

Name: {name}
Address: {address}
Phone: {phone}
Service: {service}
Details: {details if details else "N/A"}

Timestamp: {timestamp}

ACTION: Contact client immediately (promised 2-hour response)
        """
        
        # Adjuntar ambas versiones
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        # Enviar con Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent to {RECIPIENT_EMAIL}")
        return True
        
    except Exception as e:
        print(f"❌ Email send failed: {str(e)}")
        return False

# ═══════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
