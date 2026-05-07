"use client";

import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

export default function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, borderBottom: "2px solid #2b2b2b" }}
        >
          EV Scheduler
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
