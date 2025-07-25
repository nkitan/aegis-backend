
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Item(BaseModel):
    name: str
    price: float
    category: str

class Transaction(BaseModel):
    id: Optional[str] = None
    user_id: str
    store_name: str
    transaction_date: datetime
    items: List[Item]
    total_amount: float
    category: Optional[str] = None
    location: Optional[str] = None
