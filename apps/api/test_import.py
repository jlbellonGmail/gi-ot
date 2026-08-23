#!/usr/bin/env python
import sys
sys.path.insert(0, ".")
from app.models import Customer, Asset, Location, Priority, User, WorkOrderStatus, WorkOrderType, Technician
print("OK: all imports from app.models worked")
print("Customer:", Customer)
print("Asset:", Asset)