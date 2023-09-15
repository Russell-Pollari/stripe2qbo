import * as React from 'react';
import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { DataGrid, GridRowsProp, GridColDef } from '@mui/x-data-grid';
import { CheckIcon } from '@heroicons/react/24/solid';

import {
    addTransaction,
    selectTransaction,
    setSyncingTransaction,
    removeSyncingTransaction,
} from '../store/transactions';
import { setIsSyncing, setSyncStatus } from '../store/sync';
import type { RootState } from '../store/store';
import type { Transaction } from '../types';
import LoadingSpinner from './LoadingSpinner';
import numToAccountingFormat from '../numToAccountingString';

const TransactionTable = () => {
    const dispatch = useDispatch();

    const transactions = useSelector(
        (state: RootState) => state.transactions.transactions
    );
    const syncingTransactionIds = useSelector(
        (state: RootState) => state.transactions.syncingTransactions
    );
    const [selectedTransactionIds, setSelectedTransactionIds] = useState<
        string[]
    >([]);

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
        ws.onerror = (error) => {
            alert(error);
            dispatch(setSyncStatus(''));
            dispatch(setIsSyncing(false));
        };
    };

    const rows: GridRowsProp = transactions.map((transaction: Transaction) => {
        return {
            id: transaction.id,
            type: transaction.type,
            amount: transaction.amount,
            fee: -transaction.fee,
            currency: transaction.currency.toUpperCase(),
            description: transaction.description,
            created: new Date(transaction.created * 1000),
            status: transaction.status,
        };
    });

    const columns: GridColDef[] = [
        { field: 'type', headerName: 'Type', width: 100 },
        {
            field: 'amount',
            headerName: 'Amount',
            width: 150,
            valueFormatter: (params) => {
                return numToAccountingFormat(params.value as number);
            },
        },
        {
            field: 'fee',
            headerName: 'Fee',
            width: 150,
            valueFormatter: (params) => {
                return numToAccountingFormat(params.value as number);
            },
        },
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
    );
};

export default TransactionTable;
