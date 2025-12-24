import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { mainnet, sepolia } from 'wagmi/chains';

// WalletConnect Project ID
// Get your own at https://cloud.walletconnect.com
// For development, a placeholder is used. Replace in production!
const projectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || 'qfs-atlas-v20-dev';

export const config = getDefaultConfig({
    appName: 'QFS × ATLAS V20',
    projectId,
    chains: [mainnet, sepolia],
    // IMPORTANT: Set to false for Electron desktop app
    // This ensures WalletConnect modals work correctly
    ssr: false,
});

