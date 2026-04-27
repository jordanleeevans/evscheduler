export interface Vehicle {
  id: string;
  name: string;
  batteryCapacityKwh: number;
  currentBatteryPct: number;
  createdAt: string;
}

export type SessionStatus = 'PENDING' | 'SCHEDULED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';

export interface ChargingSlot {
  id: string;
  slotStart: string;
  slotEnd: string;
  pricePerKwh: number;
  isSelected: boolean;
}

export interface ChargingSession {
  id: string;
  vehicle: Vehicle;
  departureTime: string;
  targetChargePct: number;
  status: SessionStatus;
  slots: ChargingSlot[];
  createdAt: string;
}

export interface Tariff {
  id: string;
  name: string;
  region: string;
  validFrom: string;
  validTo: string;
}

export interface TariffPrice {
  slotStart: string;
  slotEnd: string;
  pricePerKwh: number;
}
