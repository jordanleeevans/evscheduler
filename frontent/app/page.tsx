import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import VehicleCard from "./ui/VehicleCard";
import { getVehicles, Vehicle } from "./lib/vehicles";

export default async function Home() {
  // const vehicles = await getVehicles();
  // mock 10 vehicles for testing
  const vehicles: Vehicle[] = Array.from({ length: 10 }, (_, i) => ({
    id: `vehicle-${i + 1}`,
    name: `Vehicle ${i + 1}`,
    batteryCapacityKwh: 50 + i * 5,
    currentBatteryPct: Math.floor(Math.random() * 101),
  }));
  return (
    <Box
      component="main"
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        gap: 3,
      }}
    >
      <Typography variant="h3" component="h1" sx={{ fontWeight: "bold" }}>
        Welcome to EV Scheduler
      </Typography>
      {vehicles.length > 0 ? (
        <VehicleCards vehicles={vehicles} />
      ) : (
        <NoVehiclesText />
      )}
    </Box>
  );
}

interface VehicleCardsProps {
  vehicles: Vehicle[];
}

function VehicleCards({ vehicles }: VehicleCardsProps) {
  return (
    <Stack
      direction="row"
      spacing={{ xs: 2, sm: 3, md: 4 }}
      useFlexGap
      sx={{ flexWrap: "wrap" }}
    >
      {vehicles.map((vehicle) => (
        <VehicleCard key={vehicle.id} vehicle={vehicle} />
      ))}
    </Stack>
  );
}

function NoVehiclesText() {
  return <Typography variant="body1">No vehicles available</Typography>;
}
