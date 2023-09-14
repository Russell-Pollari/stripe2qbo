import * as React from 'react';
import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import {
    addTransaction,
    selectTransaction,
    setSyncingTransaction,
    removeSyncingTransaction,
} from '../store/transactions';
import { setIsSyncing, setSyncStatus } from '../store/sync';
import type { RootState } from '../store/store';
import type { Transaction } from '../types';
import SyncDetails from './SyncDetails';
import { DataGrid, GridRowsProp, GridColDef } from '@mui/x-data-grid';
import { CheckIcon } from '@heroicons/react/24/solid';

const LoadingSpinner = () => (
    <div role="status">
        <svg
            aria-hidden="true"
            className="w-8 h-8 mr-2 text-green-200 animate-spin fill-green-600"
            viewBox="0 0 100 101"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path
                d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                fill="currentColor"
            />
            <path
                d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                fill="currentFill"
            />
        </svg>
        <span className="sr-only">Loading...</span>
    </div>
);

const formatAmount = (amount: number) => {
    let amount_string = (amount / 100).toLocaleString();
    if (!amount_string.split('.')[1]) {
        amount_string = `${amount_string}.00`;
    }
    if (amount_string.split('.')[1].length === 1) {
        amount_string = `${amount_string}0`;
    }
    if (amount < 0) {
        return `($${amount_string.slice(1)})`;
    }
    return `$${amount_string}`;
};

const TransactionTable = () => {
    const transactions = useSelector(
        (state: RootState) => state.transactions.transactions
    );
    const selectedTransaction = useSelector(
        (state: RootState) => state.transactions.selectedTransaction
    );
    const syncingTransactionIds = useSelector(
        (state: RootState) => state.transactions.syncingTransactions
    );
    const [selectedTransactionIds, setSelectedTransactionIds] = useState<
        string[]
    >([]);
    const dispatch = useDispatch();

    const syncTransaction = async (transactionId: string) => {
        dispatch(setSyncStatus('Syncing 1 transaction'));
        dispatch(setSyncingTransaction(transactionId));
        dispatch(setIsSyncing(true));
        const response = await fetch(
            `/api/sync?transaction_id=${transactionId}`,
            {
                method: 'POST',
            }
        );
        const data = await response.json();
        dispatch(addTransaction(data));
        dispatch(setSyncStatus(''));
        dispatch(setIsSyncing(false));
        dispatch(removeSyncingTransaction(transactionId));
        return data;
    };

    const syncAll = () => {
        const transaction_ids = selectedTransactionIds.map((id) => [
            'transaction_ids',
            id,
        ]);
        const queryString = new URLSearchParams(transaction_ids).toString();
        const ws = new WebSocket(
            `ws://localhost:8000/api/syncmany?${queryString}`
        );
        ws.onopen = () => {
            dispatch(setIsSyncing(true));
            dispatch(setSyncingTransaction(selectedTransactionIds));
        };
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.status) {
                dispatch(setSyncStatus(data.status));
            }
            if (data.transaction) {
                dispatch(addTransaction(data.transaction));
                dispatch(removeSyncingTransaction(data.transaction.id));
            }
        };
        ws.onclose = () => {
            dispatch(setSyncStatus(''));
            dispatch(setIsSyncing(false));
        };
    };

    const rows: GridRowsProp = transactions.map((transaction: Transaction) => {
        return {
            id: transaction.id,
            type: transaction.type,
            amount: formatAmount(transaction.amount),
            fee: formatAmount(-transaction.fee),
            currency: transaction.currency.toUpperCase(),
            description: transaction.description,
            created: new Date(transaction.created * 1000),
            status: transaction.status,
        };
    });

    const columns: GridColDef[] = [
        { field: 'type', headerName: 'Type', width: 100 },
        { field: 'amount', headerName: 'Amount', width: 150 },
        { field: 'fee', headerName: 'Fee', width: 150 },
        { field: 'currency', headerName: 'Currency', width: 100 },
        { field: 'description', headerName: 'Description', width: 300 },
        { field: 'created', headerName: 'Created', type: 'date', width: 150 },
        {
            field: 'status',
            headerName: 'Status',
            width: 150,
            renderCell: (params) => {
                if (syncingTransactionIds.includes(params.row.id)) {
                    return <LoadingSpinner />;
                }
                if (params.value === 'success') {
                    return (
                        <span>
                            Synced
                            <CheckIcon className="w-6 h-6 text-green-500" />
                        </span>
                    );
                }
                return params.value;
            },
        },
        {
            field: 'actions',
            headerName: 'Actions',
            type: 'actions',
            width: 300,
            getActions: (params) => [
                <button
                    disabled={syncingTransactionIds.includes(params.row.id)}
                    className="inline-block bg-slate-300 hover:bg-slate-600 text-gray-500 font-bold p-2 rounded-full text-sm"
                    onClick={() => syncTransaction(params.row.id)}
                >
                    {syncingTransactionIds.includes(params.row.id)
                        ? 'Syncing..'
                        : 'Sync'}
                </button>,
                <button
                    onClick={() => {
                        dispatch(selectTransaction(params.row.id));
                    }}
                >
                    View details
                </button>,
            ],
            renderHeader: () => (
                <div className="text-right">
                    <button
                        className="inline-block bg-slate-300 hover:bg-slate-600 text-gray-500 font-bold p-2 rounded-full text-sm"
                        onClick={syncAll}
                    >
                        Sync {selectedTransactionIds.length} transactions
                    </button>
                </div>
            ),
        },
    ];

    return (
        <div className="text-left mt-4 p-4 shadow-lg">
            {selectedTransaction !== null && (
                <SyncDetails transaction={transactions[selectedTransaction]} />
            )}

            <div className="w-full h-full">
                <DataGrid
                    onRowSelectionModelChange={(selection) => {
                        setSelectedTransactionIds(selection as string[]);
                    }}
                    rows={rows}
                    columns={columns}
                    checkboxSelection
                    pageSizeOptions={[10, 25]}
                />
            </div>
        </div>
    );
};

export default TransactionTable;
