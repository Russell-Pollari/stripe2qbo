import * as React from 'react';

import ConnectionCard from './ConnectionCard';
import {
    useGetStripeInfoQuery,
    useDisconnectStripeMutation,
} from '../services/api';

const connect = () => {
    fetch('/stripe/oauth2')
        .then((response) => response.json())
        .then((data: string) => {
            location.href = data;
        });
};

const StripeConnection = () => {
    const { data: stripeInfo, isLoading, error } = useGetStripeInfoQuery();
    const [disconnect] = useDisconnectStripeMutation();
    console.log(error);
    return (
        <ConnectionCard
            isConnected={!!stripeInfo}
            title="Stripe account"
            isLoading={isLoading}
            disconnect={() => {
                disconnect();
            }}
        >
            {stripeInfo && !error ? (
                <span>
                    {stripeInfo.id} ({stripeInfo.country})
                </span>
            ) : (
                <button
                    className="inline-block hover:bg-slate-100 text-gray-500 font-bold p-2 rounded-full text-sm"
                    onClick={connect}
                >
                    Connect a Stripe account
                </button>
            )}
        </ConnectionCard>
    );
};

export default StripeConnection;
