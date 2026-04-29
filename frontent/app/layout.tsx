import type { Metadata } from "next";
import { Sulphur_Point } from "next/font/google";
import "./globals.css";
import { ApolloWrapper } from "./ApolloWrapper";

const sulphurPoint = Sulphur_Point({
  variable: "--font-sulphur-point",
  subsets: ["latin"],
  weight: "300",
});

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
    <html lang="en" className={`${sulphurPoint.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <ApolloWrapper>{children}</ApolloWrapper>
      </body>
    </html>
  );
}
