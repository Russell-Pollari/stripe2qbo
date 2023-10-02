import * as React from 'react';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router';

import { useSetStripeTokenMutation } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const StripeCallback = () => {
    const { search } = useLocation();
    const params = new URLSearchParams(search);
    const code = params.get('code');

    const [setStripeToken] = useSetStripeTokenMutation();
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (code) {
            setStripeToken(code)
                .unwrap()
                .then(() => {
                    location.href = '/settings';
                })
                .catch((e) => {
                    // eslint-disable-next-line
                    setError(e?.data?.detail);
                    console.error(e);
                });
        }
    }, [code]);

    return (
        <div className="grid h-1/2 place-items-center">
            <div className="font-semibold">
                <LoadingSpinner />
                Connecting to Stripe...
                {error && <div className="text-red-500 my-4">{error}</div>}
            </div>
        </div>
    );
};

export default StripeCallback;
