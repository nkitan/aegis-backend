
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Item(BaseModel):
    name: str
    price: float
    quantity: float = 1.0
    unit: Optional[str] = None  # e.g., "kg", "lbs", "pieces"
    category: str
    discount: Optional[float] = None
    original_price: Optional[float] = None  # price before discount

class Transaction(BaseModel):
    id: Optional[str] = None
    user_id: str
    store_name: str
    transaction_date: datetime
    items: List[Item]
    total_amount: float
    currency: str = "INR"  # Default to INR if not specified
    payment_method: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    receipt_image_url: Optional[str] = None
