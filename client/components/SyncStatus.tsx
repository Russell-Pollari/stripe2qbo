import * as React from 'react';

import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid';
import { useSyncTransactionsMutation } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import PrimaryButton from './PrimaryButton';

const SyncStatus = ({ status, id }: { status: string; id: string }) => {
    const [syncTransactions] = useSyncTransactionsMutation();

    if (status === 'syncing') {
        return (
            <span className="text-green-400">
                <LoadingSpinner /> Syncing
            </span>
        );
    }
    if (status === 'success') {
        return (
            <span className="text-green-500">
                <CheckIcon className="w-4 h-4 inline -mt-px mr-2" />
                Synced
            </span>
        );
    }
    if (status === 'pending') {
        return (
            <PrimaryButton
                onClick={() => {
                    syncTransactions([id])
                        .unwrap()
                        .catch((error) => {
                            console.error(error);
                        });
                }}
            >
                Sync
            </PrimaryButton>
        );
    }
    if (status === 'failed') {
        return (
            <span className="text-red-500">
                <XMarkIcon className="w-4 h-4 inline -mt-px mr-2" />
                Failed
            </span>
        );
    }
    return status;
};

export default SyncStatus;
