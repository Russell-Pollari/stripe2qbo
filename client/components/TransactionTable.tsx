import * as React from 'react';
import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { addTransaction, selectTransaction } from '../store/transactions';
import { setIsSyncing, setSyncStatus } from '../store/sync';
import type { RootState } from '../store/store';
import type { Transaction } from '../types';
import SyncDetails from './SyncDetails';
import { DataGrid, GridRowsProp, GridColDef } from '@mui/x-data-grid';

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
    const [selectedTransactionIds, setSelectedTransactionIds] = useState<
        string[]
    >([]);
    const dispatch = useDispatch();

    const syncTransaction = async (transactionId: string) => {
        dispatch(setSyncStatus('Syncing 1 transaction'));
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
        return data;
    };

    const syncAll = () => {
        const transaction_ids = selectedTransactionIds.map((id) => [
            'transaction_ids',
            id,
        ]);
        console.log(transaction_ids);
        const queryString = new URLSearchParams(transaction_ids).toString();
        const ws = new WebSocket(
            `ws://localhost:8000/api/syncmany?${queryString}`
        );
        ws.onopen = () => {
            dispatch(setIsSyncing(true));
        };
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.status) {
                dispatch(setSyncStatus(data.status));
            }
            if (data.transaction) {
                dispatch(addTransaction(data.transaction));
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
        { field: 'status', headerName: 'Status', width: 150 },
        {
            field: 'actions',
            headerName: 'Actions',
            type: 'actions',
            width: 300,
            getActions: (params) => [
                <button
                    className="inline-block bg-slate-300 hover:bg-slate-600 text-gray-500 font-bold p-2 rounded-full text-sm"
                    onClick={() => syncTransaction(params.row.id)}
                >
                    Sync
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
