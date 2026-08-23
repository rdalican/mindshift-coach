"""Modulo Stripe per gestione abbonamenti Micro-SaaS su Railway.
Supporta abbonamento ricorrente da 9.99€/mese con 3 giorni di prova gratuita e modalità simulazione.
"""

import logging
from typing import Optional, Dict, Any
from app.config import settings
from app.core.models import StripeCheckoutResponse

logger = logging.getLogger("mindshift.stripe")

class StripeManager:
    """Gestore dei pagamenti e abbonamenti Stripe."""

    def __init__(self):
        self.secret_key = settings.STRIPE_SECRET_KEY
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        self.price_id = settings.STRIPE_PRICE_ID
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self._init_stripe()

    def _init_stripe(self):
        if self.secret_key and self.secret_key.strip():
            try:
                import stripe
                stripe.api_key = self.secret_key
                logger.info("Stripe SDK inizializzato con successo.")
            except Exception as e:
                logger.warning(f"Impossibile inizializzare Stripe: {e}")
        else:
            logger.info("Nessuna STRIPE_SECRET_KEY configurata. Modalità simulazione/test attiva.")

    def create_subscription_checkout(
        self,
        sync_key: str,
        email: Optional[str] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> StripeCheckoutResponse:
        """Crea una sessione di Stripe Checkout o una sessione mock per test."""
        
        base_url = settings.APP_BASE_URL.rstrip('/')
        success_url = success_url or f"{base_url}/?payment=success&sync_key={sync_key}"
        cancel_url = cancel_url or f"{base_url}/?payment=cancelled"

        # Se Stripe è configurato con chiave reale
        if self.secret_key and self.secret_key.strip().startswith("sk_"):
            try:
                import stripe
                
                line_items = []
                if self.price_id and self.price_id.strip():
                    line_items.append({"price": self.price_id, "quantity": 1})
                else:
                    # Prezzo dinamico ricorrente 9.99€/mese
                    line_items.append({
                        "price_data": {
                            "currency": "eur",
                            "product_data": {
                                "name": "MindShift Coach Pro (Micro-SaaS)",
                                "description": "Accesso illimitato al motore PNL avanzato e sincronizzazione cloud Windows/Android."
                            },
                            "unit_amount": 999, # 9.99 €
                            "recurring": {"interval": "month"}
                        },
                        "quantity": 1
                    })

                session_params = {
                    "payment_method_types": ["card"],
                    "mode": "subscription",
                    "line_items": line_items,
                    "success_url": success_url + "&session_id={CHECKOUT_SESSION_ID}",
                    "cancel_url": cancel_url,
                    "client_reference_id": sync_key,
                    "metadata": {"sync_key": sync_key},
                    "subscription_data": {
                        "trial_period_days": settings.FREE_TRIAL_DAYS,
                        "metadata": {"sync_key": sync_key}
                    }
                }
                if email:
                    session_params["customer_email"] = email

                session = stripe.checkout.Session.create(**session_params)
                return StripeCheckoutResponse(
                    checkout_url=session.url,
                    session_id=session.id,
                    is_mock=False
                )
            except Exception as e:
                logger.error(f"Errore Stripe Checkout: {e}. Attivazione fallback simulato.")

        # Modalità Test / Simulazione per test locali o anteprima senza chiavi
        mock_session_id = f"cs_test_mock_{sync_key[:8]}"
        mock_url = f"{base_url}/?payment=mock_success&sync_key={sync_key}&session_id={mock_session_id}"
        return StripeCheckoutResponse(
            checkout_url=mock_url,
            session_id=mock_session_id,
            is_mock=True
        )

    def handle_webhook_event(self, payload: bytes, sig_header: Optional[str]) -> Dict[str, Any]:
        """Elabora gli eventi webhook di Stripe per aggiornare lo stato dell'abbonamento."""
        if not self.secret_key or not self.webhook_secret:
            return {"status": "ignored", "reason": "No webhook secret"}

        try:
            import stripe
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            event_type = event["type"]
            data_object = event["data"]["object"]

            result = {"status": "processed", "event_type": event_type}

            if event_type == "checkout.session.completed":
                sync_key = data_object.get("client_reference_id") or data_object.get("metadata", {}).get("sync_key")
                customer_id = data_object.get("customer")
                sub_id = data_object.get("subscription")
                result.update({
                    "action": "activate_subscription",
                    "sync_key": sync_key,
                    "customer_id": customer_id,
                    "subscription_id": sub_id
                })
            elif event_type in ["customer.subscription.updated", "customer.subscription.deleted"]:
                sub_status = data_object.get("status")
                sync_key = data_object.get("metadata", {}).get("sync_key")
                result.update({
                    "action": "update_status",
                    "sync_key": sync_key,
                    "new_status": "active" if sub_status in ["active", "trialing"] else "inactive"
                })

            return result
        except Exception as e:
            logger.error(f"Errore verifica webhook Stripe: {e}")
            return {"status": "error", "message": str(e)}

stripe_manager = StripeManager()
