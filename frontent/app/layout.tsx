import type { Metadata } from "next";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import { ApolloWrapper } from "./ApolloWrapper";
import ThemeRegistry from "./ui/ThemeRegistry";
import Navbar from "./ui/Navbar";
import "./globals.css";
import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";

export const metadata: Metadata = {
  title: "EV Scheduler",
  description:
    "A simple app to schedule electric vehicle charging sessions based on time-of-use tariffs.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>
          <ThemeRegistry>
            <Navbar />
            <ApolloWrapper>{children}</ApolloWrapper>
          </ThemeRegistry>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
