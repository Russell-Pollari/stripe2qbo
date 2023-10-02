import * as React from 'react';

import StripeConnection from '../components/StripeConnection';
import QBOConnection from '../components/QBOConnection';
import SyncSettings from '../components/settings/SyncSettings';
import { useGetCompanyInfoQuery } from '../services/api';

const SettingsPage = () => {
    const { data: qboInfo } = useGetCompanyInfoQuery();

    return (
        <div className="flex justify-center p-4">
            <div className="w-96">
                <h2 className="text-xl font-semibold mb-4">Connections</h2>

                <QBOConnection />
                <StripeConnection />
                <h2 className="text-xl font-semibold mt-8 mb-4">Settings</h2>

                {qboInfo && <SyncSettings />}
            </div>
        </div>
    );
};

export default SettingsPage;
