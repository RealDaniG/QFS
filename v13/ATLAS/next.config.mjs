/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    images: {
        unoptimized: true, // Required for static export
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    // Electron requires relative paths for file:// protocol loading
    assetPrefix: './',
    trailingSlash: true,
    webpack: (config, { isServer, webpack }) => {
        if (!isServer) {
            config.resolve.fallback = {
                ...config.resolve.fallback,
                fs: false,
                net: false,
                tls: false,
                crypto: false,
                os: false,
                path: false,
                stream: false,
                dns: false,
                child_process: false,
            };

            config.plugins.push(
                new webpack.IgnorePlugin({
                    resourceRegExp: /libp2p|@libp2p|@chainsafe\/libp2p-noise|@peculiar\/asn1-cms|@peculiar\/webcrypto/
                })
            );
        }
        return config;
    },
}

export default nextConfig
