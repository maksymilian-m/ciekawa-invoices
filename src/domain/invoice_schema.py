from pydantic import BaseModel, Field
from datetime import date

class InvoiceExtraction(BaseModel):
    """Structured output model for invoice data extraction."""
    
    invoice_date: date = Field(
        description="The date when the invoice was issued (Data wystawienia)"
    )
    category: str = Field(
        description="Invoice category classification. Must be one of: JEDZENIE, NAPOJE, ALKOHOL, ADMINISTRACYJNE, BANK, BAR, CHEMIA, CIASTA, DOSTAWY, GAZ, IMPREZY, INNE RACHUNKI, KAWA, KONCESJA, LODY, LÓD, PODATEK, PRĄD, REKLAMA, REMONT, ŚMIECIE, UBEZPIECZENIE, WODA, WYPOSAŻENIE"
    )
    vendor: str = Field(
        description="The name of the invoice issuer/vendor (Sprzedawca)"
    )
    net_amount: float = Field(
        description="Total net amount (Kwota netto)"
    )
    gross_amount: float = Field(
        description="Total gross amount including tax (Kwota brutto)"
    )
    invoice_number: str = Field(
        description="Invoice identifier/number (Numer faktury/FV)"
    )
    payment_date: date = Field(
        description="Payment due date (Termin płatności/Data płatności)"
    )
