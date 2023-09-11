import * as React from 'react';

import StripeConnection from '../components/StripeConnection';
import SyncSettings from '../components/settings/SyncSettings';

const SettingsPage = () => {
    return (
        <div className="flex justify-center">
            <div className="w-96">
                <StripeConnection />
                <SyncSettings />
            </div>
        </div>
    );
};

export default SettingsPage;
