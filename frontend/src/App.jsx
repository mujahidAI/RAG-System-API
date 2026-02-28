/**
 * App.jsx - Main application component with routing.
 * Sets up React Router and wraps content in Layout.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Chat } from './pages/Chat';
import { Ingest } from './pages/Ingest';
import { Evaluate } from './pages/Evaluate';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/ingest" element={<Ingest />} />
          <Route path="/evaluate" element={<Evaluate />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
