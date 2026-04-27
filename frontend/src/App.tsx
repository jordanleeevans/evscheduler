import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ApolloProvider } from '@apollo/client';
import apolloClient from './apolloClient';
import Dashboard from './components/Dashboard';
import ChargingForm from './components/ChargingForm';
import TariffChart from './components/TariffChart';

export default function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <BrowserRouter>
        <div style={{ fontFamily: 'system-ui, sans-serif', maxWidth: '900px', margin: '0 auto' }}>
          <Routes>
            <Route
              path="/"
              element={
                <>
                  <Dashboard />
                  <TariffChart />
                </>
              }
            />
            <Route path="/schedule" element={<ChargingForm />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ApolloProvider>
  );
}
