/** @type {import('next').NextConfig} */
import { fileURLToPath } from 'url'
import { dirname } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const nextConfig = {
    output: 'export',
    // distDir: 'out',
    images: {
        unoptimized: true, // Required for static export
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    // Force webpack instead of Turbopack (Turbopack has Windows symlink issues)
    webpack: (config) => {
        // Return config as-is to use webpack
        return config
    },
    // No API routes or rewrites in static export mode

    // Electron requires relative paths for file:// protocol loading
    assetPrefix: './',
    trailingSlash: true, // Optional: helps with file routing consistency
}

export default nextConfig
