/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    // distDir: 'out',
    images: {
        unoptimized: true, // Required for static export
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    experimental: {
        turbopack: {
            root: __dirname,
        },
    },
    // No API routes or rewrites in static export mode

    // Electron requires relative paths for file:// protocol loading
    assetPrefix: process.env.NEXT_PUBLIC_IS_ELECTRON_BUILD ? './' : undefined,
    trailingSlash: true, // Optional: helps with file routing consistency
}

export default nextConfig
