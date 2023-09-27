import * as React from 'react';

import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid';
import { useSyncTransactionsMutation } from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const SyncStatus = ({ status, id }: { status: string; id: string }) => {
    const [syncTransactions] = useSyncTransactionsMutation();

    if (status === 'syncing') {
        return <LoadingSpinner />;
    }
    if (status === 'success') {
        return (
            <span className="text-green-500">
                <CheckIcon className="w-6 h-6 inline -m-px" />
                Synced
            </span>
        );
    }
    if (status === 'pending') {
        return (
            <button
                className="inline-block font-semibold bg-green-500 hover:bg-green-600 text-gray-100 py-2 px-4 rounded-full text-sm shadow-lg"
                onClick={() => syncTransactions([id])}
            >
                Sync
            </button>
        );
    }
    if (status === 'failed') {
        return (
            <span className="text-red-500">
                <XMarkIcon className="w-6 h-6 inline -m-px" />
                Failed
            </span>
        );
    }
    return status;
};

export default SyncStatus;
