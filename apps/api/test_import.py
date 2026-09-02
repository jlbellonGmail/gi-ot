#!/usr/bin/env python
import sys

sys.path.insert(0, ".")
from app.models import (
    Asset,
    Customer,
    Location,
    Priority,
    Technician,
    User,
    WorkOrderStatus,
    WorkOrderType,
)

print("OK: all imports from app.models worked")
print("Customer:", Customer)
print("Asset:", Asset)