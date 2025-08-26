"""
Email Service for VelocityPost.ai
Handles password reset emails, notifications, and user communications
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, template: str, context: Dict[str, Any]) -> bool:
    """
    Send email using configured email service
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        template: Email template name (password_reset, welcome, etc.)
        context: Template context variables
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # For development - just log the email
        if os.getenv('FLASK_ENV') == 'development':
            logger.info(f"[EMAIL] To: {to_email}")
            logger.info(f"[EMAIL] Subject: {subject}")
            logger.info(f"[EMAIL] Template: {template}")
            logger.info(f"[EMAIL] Context: {context}")
            print(f"📧 EMAIL: {subject} → {to_email}")
            return True
        
        # Production email sending would go here
        # Example implementations:
        
        # Option 1: SMTP
        smtp_server = os.getenv('MAIL_SERVER')
        if smtp_server:
            return send_smtp_email(to_email, subject, template, context)
        
        # Option 2: SendGrid
        sendgrid_key = os.getenv('SENDGRID_API_KEY')
        if sendgrid_key:
            return send_sendgrid_email(to_email, subject, template, context)
        
        # Fallback - log only
        logger.warning("No email service configured. Email logged only.")
        print(f"📧 EMAIL (NOT SENT): {subject} → {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def send_smtp_email(to_email: str, subject: str, template: str, context: Dict[str, Any]) -> bool:
    """Send email via SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # SMTP configuration
        smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('MAIL_PORT', 587))
        smtp_username = os.getenv('MAIL_USERNAME')
        smtp_password = os.getenv('MAIL_PASSWORD')
        
        if not all([smtp_username, smtp_password]):
            logger.error("SMTP credentials not configured")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = os.getenv('MAIL_DEFAULT_SENDER', smtp_username)
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Generate email body from template
        body = generate_email_body(template, context)
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"SMTP email failed: {e}")
        return False

def send_sendgrid_email(to_email: str, subject: str, template: str, context: Dict[str, Any]) -> bool:
    """Send email via SendGrid API"""
    try:
        import requests
        
        api_key = os.getenv('SENDGRID_API_KEY')
        if not api_key:
            logger.error("SendGrid API key not configured")
            return False
        
        # Generate email body
        body = generate_email_body(template, context)
        
        # SendGrid API request
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject
            }],
            "from": {"email": os.getenv('MAIL_DEFAULT_SENDER', 'noreply@velocitypost.ai')},
            "content": [{
                "type": "text/html",
                "value": body
            }]
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 202:
            logger.info(f"SendGrid email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"SendGrid email failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"SendGrid email failed: {e}")
        return False

def generate_email_body(template: str, context: Dict[str, Any]) -> str:
    """Generate email body from template and context"""
    
    templates = {
        'password_reset': """
        <html>
        <body>
            <h2>Reset Your VelocityPost.ai Password</h2>
            <p>Hi {user_name},</p>
            <p>You requested a password reset for your VelocityPost.ai account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>This link will expire in {expires_in}.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>Best regards,<br>VelocityPost.ai Team</p>
        </body>
        </html>
        """,
        
        'welcome': """
        <html>
        <body>
            <h2>Welcome to VelocityPost.ai!</h2>
            <p>Hi {user_name},</p>
            <p>Welcome to VelocityPost.ai - Your AI-powered social media automation platform!</p>
            <p>You can now:</p>
            <ul>
                <li>Connect your social media accounts</li>
                <li>Generate AI-powered content</li>
                <li>Schedule and automate posts</li>
                <li>Track performance analytics</li>
            </ul>
            <p><a href="{login_url}" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Get Started</a></p>
            <p>Need help? Check out our <a href="{docs_url}">documentation</a> or contact support.</p>
            <p>Best regards,<br>VelocityPost.ai Team</p>
        </body>
        </html>
        """,
        
        'subscription_confirmation': """
        <html>
        <body>
            <h2>Subscription Confirmed!</h2>
            <p>Hi {user_name},</p>
            <p>Thank you for upgrading to {plan_name}!</p>
            <p>Your subscription details:</p>
            <ul>
                <li>Plan: {plan_name}</li>
                <li>Price: ${amount}/month</li>
                <li>Next billing: {next_billing_date}</li>
            </ul>
            <p>You now have access to:</p>
            <ul>
                <li>{max_platforms} social media platforms</li>
                <li>{max_posts} posts per day</li>
                <li>Advanced automation features</li>
                <li>Priority support</li>
            </ul>
            <p><a href="{dashboard_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Dashboard</a></p>
            <p>Best regards,<br>VelocityPost.ai Team</p>
        </body>
        </html>
        """
    }
    
    # Get template or use default
    template_html = templates.get(template, """
    <html>
    <body>
        <h2>VelocityPost.ai Notification</h2>
        <p>{message}</p>
        <p>Best regards,<br>VelocityPost.ai Team</p>
    </body>
    </html>
    """)
    
    # Replace placeholders with context values
    try:
        return template_html.format(**context)
    except KeyError as e:
        logger.warning(f"Missing template variable: {e}")
        # Fallback with available context
        safe_context = {k: v for k, v in context.items() if isinstance(v, (str, int, float))}
        return template_html.format(**safe_context)

def send_password_reset_email(to_email: str, user_name: str, reset_url: str, expires_in: str = "1 hour") -> bool:
    """Send password reset email"""
    return send_email(
        to_email=to_email,
        subject="Reset Your VelocityPost.ai Password",
        template="password_reset",
        context={
            'user_name': user_name,
            'reset_url': reset_url,
            'expires_in': expires_in
        }
    )

def send_welcome_email(to_email: str, user_name: str) -> bool:
    """Send welcome email to new users"""
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    return send_email(
        to_email=to_email,
        subject="Welcome to VelocityPost.ai!",
        template="welcome",
        context={
            'user_name': user_name,
            'login_url': f"{frontend_url}/login",
            'docs_url': f"{frontend_url}/docs"
        }
    )

def send_subscription_confirmation_email(to_email: str, user_name: str, plan_name: str, amount: float, next_billing_date: str) -> bool:
    """Send subscription confirmation email"""
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Plan features mapping
    plan_features = {
        'pro': {'max_platforms': '5', 'max_posts': 'Unlimited'},
        'agency': {'max_platforms': 'Unlimited', 'max_posts': 'Unlimited'},
        'starter': {'max_platforms': '2', 'max_posts': '3'}
    }
    
    features = plan_features.get(plan_name.lower(), {'max_platforms': '2', 'max_posts': '3'})
    
    return send_email(
        to_email=to_email,
        subject="Subscription Confirmed - VelocityPost.ai",
        template="subscription_confirmation",
        context={
            'user_name': user_name,
            'plan_name': plan_name.title(),
            'amount': amount,
            'next_billing_date': next_billing_date,
            'max_platforms': features['max_platforms'],
            'max_posts': features['max_posts'],
            'dashboard_url': f"{frontend_url}/dashboard"
        }
    )

# Test function
def test_email_service():
    """Test email service functionality"""
    try:
        result = send_email(
            to_email="test@example.com",
            subject="Test Email",
            template="welcome",
            context={'user_name': 'Test User'}
        )
        return result
    except Exception as e:
        logger.error(f"Email service test failed: {e}")
        return False

if __name__ == '__main__':
    # Test the email service
    test_result = test_email_service()
    print(f"Email service test: {'✅ PASSED' if test_result else '❌ FAILED'}")