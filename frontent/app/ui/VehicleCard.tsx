import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import type { Vehicle } from "../lib/vehicles";

type Props = {
  vehicle: Vehicle;
};

export default function VehicleCard({ vehicle }: Props) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6">{vehicle.name}</Typography>
        <Typography variant="body2" color="text.secondary">
          {vehicle.batteryCapacityKwh} kWh &nbsp;·&nbsp;{" "}
          {vehicle.currentBatteryPct}% charged
        </Typography>
      </CardContent>
    </Card>
  );
}
