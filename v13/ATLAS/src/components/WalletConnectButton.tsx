'use client';

import { ConnectButton } from '@rainbow-me/rainbowkit';

export function WalletConnectButton() {
    return (
        <div className="flex flex-col items-end gap-2">
            <ConnectButton
                label="Connect Wallet"
                accountStatus="address"
                chainStatus="icon"
                showBalance={false}
            />
        </div>
    );
}
