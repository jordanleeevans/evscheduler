import { gql } from '@apollo/client';

export const GET_VEHICLES = gql`
  query GetVehicles {
    vehicles {
      id
      name
      batteryCapacityKwh
      currentBatteryPct
      createdAt
    }
  }
`;

export const GET_CHARGING_SESSIONS = gql`
  query GetChargingSessions {
    chargingSessions {
      id
      vehicle {
        id
        name
        batteryCapacityKwh
        currentBatteryPct
        createdAt
      }
      departureTime
      targetChargePct
      status
      slots {
        id
        slotStart
        slotEnd
        pricePerKwh
        isSelected
      }
      createdAt
    }
  }
`;

export const GET_TARIFF_PRICES = gql`
  query GetTariffPrices($from: String!, $to: String!, $region: String) {
    tariffPrices(from: $from, to: $to, region: $region) {
      slotStart
      slotEnd
      pricePerKwh
    }
  }
`;
