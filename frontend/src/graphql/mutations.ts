import { gql } from '@apollo/client';

export const CREATE_VEHICLE = gql`
  mutation CreateVehicle(
    $name: String!
    $batteryCapacityKwh: Float!
    $currentBatteryPct: Float!
  ) {
    createVehicle(
      name: $name
      batteryCapacityKwh: $batteryCapacityKwh
      currentBatteryPct: $currentBatteryPct
    ) {
      id
      name
      batteryCapacityKwh
      currentBatteryPct
      createdAt
    }
  }
`;

export const SCHEDULE_CHARGING_SESSION = gql`
  mutation ScheduleChargingSession(
    $vehicleId: ID!
    $departureTime: String!
    $targetChargePct: Float!
  ) {
    scheduleChargingSession(
      vehicleId: $vehicleId
      departureTime: $departureTime
      targetChargePct: $targetChargePct
    ) {
      id
      vehicle {
        id
        name
      }
      departureTime
      targetChargePct
      status
      createdAt
    }
  }
`;

export const CANCEL_CHARGING_SESSION = gql`
  mutation CancelChargingSession($id: ID!) {
    cancelChargingSession(id: $id) {
      id
      status
    }
  }
`;

export const UPDATE_BATTERY_LEVEL = gql`
  mutation UpdateBatteryLevel($vehicleId: ID!, $currentBatteryPct: Float!) {
    updateBatteryLevel(vehicleId: $vehicleId, currentBatteryPct: $currentBatteryPct) {
      id
      name
      currentBatteryPct
    }
  }
`;
