import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const YouTubeCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code) {
      // Process the OAuth callback here
      // Then redirect to main YouTube page
      navigate('/youtube');
    }
  }, [navigate]);

  return <div>Processing YouTube connection...</div>;
};

export default YouTubeCallback;