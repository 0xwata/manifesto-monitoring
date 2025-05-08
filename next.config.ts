import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'www.shugiin.go.jp',
        port: '',
        pathname: '/**',
      },
      { // Add Sangiin hostname
        protocol: 'https',
        hostname: 'www.sangiin.go.jp',
        port: '',
        pathname: '/**',
      },
    ],
  },
  /* config options here */
};

export default nextConfig;
