export interface PersonIdentification {
  id: string;
  tenant_id: string;
  person_id: string;
  country_code: string;
  identification_type: string;
  identification_value: string;
  is_primary: boolean;
  created_at: string;
}

export interface Customer {
  tenant_id: string;
  person_id: string;
  display_name: string;
  person_type: "INDIVIDUAL" | "LEGAL";
  address: string | null;
  phone: string | null;
  email: string | null;
  notes: string | null;
  status: "ACTIVE" | "INACTIVE";
  identifications: PersonIdentification[];
  created_at: string;
  updated_at: string;
}

export interface CustomerUpdate {
  person_type?: "INDIVIDUAL" | "LEGAL";
  display_name?: string;
  address?: string;
  phone?: string;
  email?: string;
  notes?: string;
  status?: "ACTIVE" | "INACTIVE";
}

export interface Technician {
  tenant_id: string;
  person_id: string;
  display_name: string;
  person_type: "INDIVIDUAL" | "LEGAL";
  address: string | null;
  phone: string | null;
  email: string | null;
  notes: string | null;
  status: "ACTIVE" | "INACTIVE";
  identifications: PersonIdentification[];
  profession: string | null;
  license_number: string | null;
  commission_percentage: number | null;
  technician_status: "ACTIVE" | "INACTIVE";
  user_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserAccount {
  id: string;
  email: string;
  full_name: string;
  role_code: "PLATFORM_OWNER" | "TENANT_ADMIN" | "TENANT_OFFICE" | "TENANT_TECHNICIAN";
  is_active: boolean;
  created_at: string;
}

export interface TechnicianUpdate {
  person_type?: "INDIVIDUAL" | "LEGAL";
  display_name?: string;
  address?: string;
  phone?: string;
  email?: string;
  notes?: string;
  status?: "ACTIVE" | "INACTIVE";
  profession?: string;
  license_number?: string;
  commission_percentage?: number;
  technician_status?: "ACTIVE" | "INACTIVE";
}

export interface Location {
  id: string;
  tenant_id: string;
  customer_id: string;
  name: string;
  address: string | null;
  city: string | null;
  province: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssetType {
  id: string;
  tenant_id: string;
  code: string;
  label: string;
  active: boolean;
}

export interface Asset {
  id: string;
  tenant_id: string;
  location_id: string;
  asset_type_id: string | null;
  name: string;
  description: string | null;
  brand: string | null;
  model: string | null;
  serial_number: string | null;
  internal_code: string | null;
  qr_code: string | null;
  status: "ACTIVE" | "INACTIVE" | "RETIRED";
  notes: string | null;
  created_at: string;
  updated_at: string;
  asset_type?: AssetType;
}

export interface CustomerCreate {
  person_type: "INDIVIDUAL" | "LEGAL";
  display_name: string;
  address?: string;
  phone?: string;
  email?: string;
  notes?: string;
  identifications: {
    country_code: string;
    identification_type: string;
    identification_value: string;
    is_primary?: boolean;
  }[];
}

export interface TechnicianCreate {
  person_type: "INDIVIDUAL" | "LEGAL";
  display_name: string;
  address?: string;
  phone?: string;
  email?: string;
  notes?: string;
  identifications: {
    country_code: string;
    identification_type: string;
    identification_value: string;
    is_primary?: boolean;
  }[];
  profession?: string;
  license_number?: string;
  commission_percentage?: number;
}

export interface LocationCreate {
  customer_id: string;
  name: string;
  address?: string;
  city?: string;
  province?: string;
  notes?: string;
}

export interface AssetCreate {
  location_id: string;
  asset_type_id?: string;
  name: string;
  description?: string;
  brand?: string;
  model?: string;
  serial_number?: string;
  internal_code?: string;
  qr_code?: string;
  notes?: string;
  status?: "ACTIVE" | "INACTIVE" | "RETIRED";
}

// WorkOrderStatus catálogo fijo (modelo-datos.md §4.13)
export interface WorkOrderStatus {
  code: "PENDING" | "IN_PROGRESS" | "COMPLETED" | "UNRESOLVED";
  label: string;
  is_terminal: boolean;
}

// WorkOrderType catálogo parametrizable por tenant
export interface WorkOrderType {
  id: string;
  tenant_id: string;
  code: string;
  label: string;
  active: boolean;
}

// Priority catálogo parametrizable por tenant
export interface Priority {
  id: string;
  tenant_id: string;
  code: "LOW" | "NORMAL" | "HIGH" | "URGENT";
  label: string;
  sort_order: number;
  active: boolean;
}

// WorkOrder — núcleo del producto (modelo-datos.md §4.12)
export interface WorkOrder {
  id: string;
  tenant_id: string;
  number: number;
  customer_id: string;
  location_id: string;
  asset_id: string;
  technician_id: string | null;
  work_order_type_id: string;
  priority_id: string;
  status_id: string;
  requested_description: string;
  performed_description: string | null;
  scheduled_at: string | null;
  started_at: string | null;
  finished_at: string | null;
  created_by: string | null;
  updated_by: string | null;
  created_at: string;
  updated_at: string;
  status_code: "PENDING" | "IN_PROGRESS" | "COMPLETED" | "UNRESOLVED";
  status_label: string | null;
  is_terminal: boolean;
  priority_code: "LOW" | "NORMAL" | "HIGH" | "URGENT" | null;
  priority_label: string | null;
}

export interface WorkOrderCreate {
  customer_id: string;
  location_id: string;
  asset_id: string;
  work_order_type_id: string;
  priority_id: string;
  requested_description: string;
  technician_id?: string;
  scheduled_at?: string;
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role_code: "PLATFORM_OWNER" | "TENANT_ADMIN" | "TENANT_OFFICE" | "TENANT_TECHNICIAN";
  tenant_id: string | null;
  technician_person_id: string | null;
}

export interface WorkOrderPhoto {
  id: string;
  work_order_id: string;
  caption: string | null;
  taken_at: string;
  uploaded_by: string | null;
  created_at: string;
}

export interface WorkOrderHistoryEntry {
  id: string;
  tenant_id: string;
  work_order_id: string;
  event_type: "CREATED" | "ASSIGNED" | "STATUS_CHANGE" | "REOPENED";
  previous_value: string | null;
  new_value: string | null;
  performed_by: string | null;
  performed_at: string;
  notes: string | null;
}