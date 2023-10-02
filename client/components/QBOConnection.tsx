import * as React from 'react';

import ConnectionCard from './ConnectionCard';
import {
    useGetCompanyInfoQuery,
    useDisconnectQBOMutation,
} from '../services/api';

const connect = () => {
    fetch('/api/qbo/oauth2')
        .then((response) => response.json())
        .then((data: string) => {
            location.href = data;
        })
        .catch((error) => {
            console.error(error);
        });
};

const QBOConnection = () => {
    const { data: qboInfo, isLoading, error } = useGetCompanyInfoQuery();
    const [disconnect] = useDisconnectQBOMutation();

    return (
        <ConnectionCard
            isConnected={!!qboInfo}
            title="QBO account"
            isLoading={isLoading}
            disconnect={() => {
                disconnect()
                    .unwrap()
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    .catch((e: any) => {
                        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
                        alert(e?.data?.detail);
                    });
            }}
        >
            {qboInfo && !error ? (
                <span>
                    {qboInfo.CompanyName} ({qboInfo.Country})
                </span>
            ) : (
                <button
                    className="inline-block hover:bg-slate-100 text-gray-500 font-bold p-2 rounded-full text-sm"
                    onClick={connect}
                >
                    Connect a QBO account
                </button>
            )}
        </ConnectionCard>
    );
};

export default QBOConnection;
