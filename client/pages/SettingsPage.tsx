import * as React from 'react';

import StripeConnection from '../components/StripeConnection';
import QBOConnection from '../components/QBOConnection';
import SyncSettings from '../components/settings/SyncSettings';
import { useGetCompanyInfoQuery } from '../services/api';

const SettingsPage = () => {
    const { data: qboInfo } = useGetCompanyInfoQuery();

    return (
        <div className="flex justify-center">
            <div className="w-96">
                <QBOConnection />
                <StripeConnection />
                {qboInfo && <SyncSettings />}
            </div>
        </div>
    );
};

export default SettingsPage;
