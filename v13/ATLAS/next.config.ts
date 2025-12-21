
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  rewrites: async () => {
    return [
      {
        source: '/api/v18/:path*',
        destination: 'http://127.0.0.1:8001/api/v18/:path*',
      },
    ];
  },
};

export default nextConfig;
