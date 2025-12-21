const fs = require('fs')
const path = require('path')

console.log('🚀 Running pre-build optimizations...')

// Clear Next.js cache
const cacheDirs = ['.next', '.turbo', 'node_modules/.cache']
cacheDirs.forEach(dir => {
    const dirPath = path.join(process.cwd(), dir)
    if (fs.existsSync(dirPath)) {
        console.log(`🗑️  Clearing ${dir}...`)
        try {
            fs.rmSync(dirPath, { recursive: true, force: true })
        } catch (e) {
            console.warn(`⚠️  Failed to clear ${dir}: ${e.message}`)
        }
    }
})

// Verify environment variables
const envFile = path.join(process.cwd(), '.env.local')
if (fs.existsSync(envFile)) {
    const envContent = fs.readFileSync(envFile, 'utf-8')
    if (envContent.includes('v18-atlas-project-id')) {
        console.warn('⚠️  WARNING: Using placeholder WalletConnect Project ID!')
        console.warn('   Get a real one at: https://cloud.walletconnect.com/')
    }
}

console.log('✅ Pre-build complete!\n')
