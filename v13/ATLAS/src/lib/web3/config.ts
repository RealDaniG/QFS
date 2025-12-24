import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { mainnet, sepolia } from 'wagmi/chains';

// WalletConnect Project ID
// Get your own at https://cloud.walletconnect.com
// Production Project ID for QFS x ATLAS
const projectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || '80c09c1575d107410279232c10587db9';

export const config = getDefaultConfig({
    appName: 'QFS × ATLAS V20',
    projectId,
    chains: [mainnet, sepolia],
    // IMPORTANT: Set to false for Electron desktop app
    // This ensures WalletConnect modals work correctly
    ssr: false,
});

