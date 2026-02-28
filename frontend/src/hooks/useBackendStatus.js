/**
 * Custom hook that polls the backend health endpoint every 10 seconds.
 * Returns the current backend status.
 */

import { useState, useEffect } from 'react';
import { checkHealth } from '../api/client';

export function useBackendStatus() {
  const [status, setStatus] = useState('checking');
  const [lastChecked, setLastChecked] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function checkStatus() {
      try {
        const result = await checkHealth();
        if (isMounted) {
          setStatus(result.status === 'healthy' ? 'online' : 'offline');
          setLastChecked(new Date());
        }
      } catch (error) {
        if (isMounted) {
          setStatus('offline');
          setLastChecked(new Date());
        }
      }
    }

    // Initial check
    checkStatus();

    // Poll every 10 seconds
    const intervalId = setInterval(checkStatus, 10000);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  return { status, lastChecked };
}
