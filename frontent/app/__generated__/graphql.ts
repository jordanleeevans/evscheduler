/* eslint-disable */
import { TypedDocumentNode as DocumentNode } from "@graphql-typed-document-node/core";
export type Maybe<T> = T | null;
export type InputMaybe<T> = T | null | undefined;
export type Exact<T extends { [key: string]: unknown }> = {
  [K in keyof T]: T[K];
};
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]?: Maybe<T[SubKey]>;
};
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]: Maybe<T[SubKey]>;
};
export type MakeEmpty<
  T extends { [key: string]: unknown },
  K extends keyof T,
> = { [_ in K]?: never };
export type Incremental<T> =
  | T
  | {
      [P in keyof T]?: P extends " $fragmentName" | "__typename" ? T[P] : never;
    };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string };
  String: { input: string; output: string };
  Boolean: { input: boolean; output: boolean };
  Int: { input: number; output: number };
  Float: { input: number; output: number };
  DateTime: { input: any; output: any };
  Percentage: { input: any; output: any };
};

export type ChargingSession = {
  __typename?: "ChargingSession";
  createdAt: Scalars["DateTime"]["output"];
  departureTime: Scalars["DateTime"]["output"];
  id: Scalars["ID"]["output"];
  slots: Array<ChargingSlot>;
  status: SessionStatus;
  targetChargePct: Scalars["Percentage"]["output"];
  vehicle: Vehicle;
};

export type ChargingSlot = {
  __typename?: "ChargingSlot";
  id: Scalars["ID"]["output"];
  isSelected: Scalars["Boolean"]["output"];
  pricePerKwh: Scalars["Float"]["output"];
  slotEnd: Scalars["DateTime"]["output"];
  slotStart: Scalars["DateTime"]["output"];
};

export type Mutation = {
  __typename?: "Mutation";
  cancelChargingSession: ChargingSession;
  createVehicle: Vehicle;
  scheduleChargingSession: ChargingSession;
  updateBatteryLevel: Vehicle;
};

export type MutationCancelChargingSessionArgs = {
  id: Scalars["ID"]["input"];
};

export type MutationCreateVehicleArgs = {
  batteryCapacityKwh: Scalars["Float"]["input"];
  currentBatteryPct: Scalars["Percentage"]["input"];
  name: Scalars["String"]["input"];
};

export type MutationScheduleChargingSessionArgs = {
  departureTime: Scalars["DateTime"]["input"];
  targetChargePct: Scalars["Percentage"]["input"];
  vehicleId: Scalars["ID"]["input"];
};

export type MutationUpdateBatteryLevelArgs = {
  currentBatteryPct: Scalars["Percentage"]["input"];
  vehicleId: Scalars["ID"]["input"];
};

export type Query = {
  __typename?: "Query";
  chargingSession?: Maybe<ChargingSession>;
  chargingSessions: Array<ChargingSession>;
  tariffPrices: Array<TariffPrice>;
  vehicle?: Maybe<Vehicle>;
  vehicles: Array<Vehicle>;
};

export type QueryChargingSessionArgs = {
  id: Scalars["ID"]["input"];
};

export type QueryTariffPricesArgs = {
  from: Scalars["DateTime"]["input"];
  region?: InputMaybe<Scalars["String"]["input"]>;
  to: Scalars["DateTime"]["input"];
};

export type QueryVehicleArgs = {
  id: Scalars["ID"]["input"];
};

export enum SessionStatus {
  Active = "ACTIVE",
  Cancelled = "CANCELLED",
  Completed = "COMPLETED",
  Pending = "PENDING",
  Scheduled = "SCHEDULED",
}

export type Tariff = {
  __typename?: "Tariff";
  id: Scalars["ID"]["output"];
  name: Scalars["String"]["output"];
  region: Scalars["String"]["output"];
  validFrom: Scalars["DateTime"]["output"];
  validTo: Scalars["DateTime"]["output"];
};

export type TariffPrice = {
  __typename?: "TariffPrice";
  pricePerKwh: Scalars["Float"]["output"];
  slotEnd: Scalars["DateTime"]["output"];
  slotStart: Scalars["DateTime"]["output"];
};

export type Vehicle = {
  __typename?: "Vehicle";
  batteryCapacityKwh: Scalars["Float"]["output"];
  createdAt: Scalars["DateTime"]["output"];
  currentBatteryPct: Scalars["Percentage"]["output"];
  id: Scalars["ID"]["output"];
  name: Scalars["String"]["output"];
};

export type GetVehiclesQueryVariables = Exact<{ [key: string]: never }>;

export type GetVehiclesQuery = {
  __typename?: "Query";
  vehicles: Array<{
    __typename?: "Vehicle";
    id: string;
    name: string;
    batteryCapacityKwh: number;
    currentBatteryPct: any;
  }>;
};

export const GetVehiclesDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "query",
      name: { kind: "Name", value: "GetVehicles" },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          {
            kind: "Field",
            name: { kind: "Name", value: "vehicles" },
            selectionSet: {
              kind: "SelectionSet",
              selections: [
                { kind: "Field", name: { kind: "Name", value: "id" } },
                { kind: "Field", name: { kind: "Name", value: "name" } },
                {
                  kind: "Field",
                  name: { kind: "Name", value: "batteryCapacityKwh" },
                },
                {
                  kind: "Field",
                  name: { kind: "Name", value: "currentBatteryPct" },
                },
              ],
            },
          },
        ],
      },
    },
  ],
} as unknown as DocumentNode<GetVehiclesQuery, GetVehiclesQueryVariables>;
