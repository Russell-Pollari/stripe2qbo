import * as React from 'react';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router';

import { useSetQBOTokenMutation } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const QBOCallback = () => {
    const { search } = useLocation();
    const params = new URLSearchParams(search);
    const code = params.get('code');
    const realmId = params.get('realmId');

    const [setQBOCode] = useSetQBOTokenMutation();
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (code && realmId) {
            setQBOCode({ code, realmId })
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
    }, [code, realmId]);

    return (
        <div className="grid h-1/2 place-items-center">
            <div className="font-semibold">
                <LoadingSpinner />
                Connecting to QuickBooks...
                {error && <div className="text-red-500 my-4">{error}</div>}
            </div>
        </div>
    );
};

export default QBOCallback;
