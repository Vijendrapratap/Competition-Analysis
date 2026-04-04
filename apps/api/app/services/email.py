import structlog
from jinja2 import Template

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

ALERT_EMAIL_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
  .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; }
  .header { background: #0d9488; color: white; padding: 24px; }
  .header h1 { margin: 0; font-size: 20px; }
  .header p { margin: 4px 0 0; opacity: 0.9; font-size: 14px; }
  .content { padding: 24px; }
  .alert { border-left: 4px solid; border-radius: 4px; padding: 12px 16px; margin-bottom: 12px; }
  .alert-high { border-color: #dc2626; background: #fef2f2; }
  .alert-medium { border-color: #d97706; background: #fffbeb; }
  .alert-low { border-color: #059669; background: #f0fdf4; }
  .alert-title { font-weight: 600; font-size: 14px; margin: 0; }
  .alert-desc { font-size: 13px; color: #4b5563; margin: 4px 0 0; }
  .cta { display: inline-block; background: #0d9488; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: 500; margin-top: 16px; }
  .footer { padding: 16px 24px; background: #f9fafb; text-align: center; font-size: 12px; color: #9ca3af; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>CompeteIQ</h1>
    <p>{{ alert_count }} competitive alert{{ 's' if alert_count != 1 else '' }} for {{ brand_name }}</p>
  </div>
  <div class="content">
    {% for alert in alerts %}
    <div class="alert alert-{{ alert.severity }}">
      <p class="alert-title">{{ alert.title }}</p>
      <p class="alert-desc">{{ alert.description }}</p>
    </div>
    {% endfor %}
    <a href="{{ dashboard_url }}" class="cta">View Dashboard</a>
  </div>
  <div class="footer">
    You're receiving this because you have alert notifications enabled in CompeteIQ.
  </div>
</div>
</body>
</html>
""")


async def send_alert_email(
    to_email: str,
    subject: str,
    brand_name: str,
    alerts: list[dict],
    dashboard_url: str = "https://app.competeiq.com/dashboard",
) -> None:
    """Send alert notification email via Resend."""
    if not settings.RESEND_API_KEY:
        logger.warning("email_skipped", reason="no Resend API key")
        return

    html = ALERT_EMAIL_TEMPLATE.render(
        brand_name=brand_name,
        alerts=alerts,
        alert_count=len(alerts),
        dashboard_url=dashboard_url,
    )

    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY

        resend.Emails.send({
            "from": "CompeteIQ <alerts@competeiq.app>",
            "to": [to_email],
            "subject": subject,
            "html": html,
        })

        logger.info("email_sent", to=to_email, subject=subject, alerts=len(alerts))
    except Exception as e:
        logger.error("email_failed", to=to_email, error=str(e))
        raise
