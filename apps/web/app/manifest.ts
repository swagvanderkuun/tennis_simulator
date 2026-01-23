import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'RacketRoute',
    short_name: 'RacketRoute',
    description: 'Tennis analytics dashboard',
    start_url: '/',
    display: 'standalone',
    background_color: '#0B0F16',
    theme_color: '#0B0F16',
    icons: [
      {
        src: '/racketroute-logo.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  };
}

