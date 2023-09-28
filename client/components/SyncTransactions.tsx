import * as React from 'react';
import { useSelector } from 'react-redux';
import { ArrowPathIcon } from '@heroicons/react/24/outline';

import type { RootState } from '../store/store';
import PrimaryButton from './PrimaryButton';
import LoadingSpinner from './LoadingSpinner';
import {
    useSyncTransactionsMutation,
    useGetTransactionsQuery,
} from '../services/api';

const SyncTransactions = () => {
    const [syncTransactions] = useSyncTransactionsMutation();
    const selectedTransactionIds = useSelector(
        (state: RootState) => state.transactions.selectedTransactionIds
    );
    const { data: transactions = [] } = useGetTransactionsQuery();

    return (
        <PrimaryButton onClick={() => syncTransactions(selectedTransactionIds)}>
            {transactions.some((t) => t.status === 'syncing') ? (
                <span>
                    <LoadingSpinner />
                    Syncing{' '}
                    {
                        transactions.filter((t) => t.status === 'syncing')
                            .length
                    }{' '}
                    transactions..
                </span>
            ) : (
                <span>
                    <ArrowPathIcon className="inline-block mr-2 h-4 w-4 -mt-px" />{' '}
                    Sync {selectedTransactionIds.length} transactions
                </span>
            )}
        </PrimaryButton>
    );
};

export default SyncTransactions;
