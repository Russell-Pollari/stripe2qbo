import * as React from 'react';
import { useSelector, useDispatch } from 'react-redux';

import {
    addTransaction,
    RootState,
    setIsSyncing,
    setSyncStatus,
} from '../store';
import type { Transaction } from '../types';

const TransactionTable = () => {
    const transactions = useSelector((state: RootState) => state.transactions);
    const dispatch = useDispatch();

    const syncTransaction = async (transaction: Transaction) => {
        dispatch(setSyncStatus('Syncing 1 transaction'));
        dispatch(setIsSyncing(true));
        const response = await fetch(`/sync?transaction_id=${transaction.id}`, {
            method: 'POST',
        });
        const data = await response.json();
        dispatch(addTransaction(data));
        dispatch(setSyncStatus(''));
        dispatch(setIsSyncing(false));
    };

    const syncAll = () => {
        const transaction_ids = transactions.map((t: Transaction) => [
            'transaction_ids',
            t.id,
        ]);
        const queryString = new URLSearchParams(transaction_ids).toString();
        const ws = new WebSocket(`ws://localhost:8000/syncmany?${queryString}`);
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

    return (
        <div className="text-left mt-4 p-4 shadow-lg">
            <button onClick={syncAll}>Sync all</button>
            <table className="text-left table-auto w-full">
                <thead>
                    <tr>
                        <th>Created</th>
                        <th>Type</th>
                        <th>Amount</th>
                        <th>Description</th>
                        <th>Sync status</th>
                    </tr>
                </thead>
                <tbody>
                    {transactions.map((transaction: Transaction) => (
                        <tr key={transaction.id}>
                            <td>
                                {new Date(transaction.created * 1000)
                                    .toDateString()
                                    .slice(0, 10)}
                            </td>
                            <td>{transaction.type}</td>
                            <td>
                                ${(transaction.amount / 100).toLocaleString()}
                            </td>
                            <td>{transaction.description}</td>
                            <td>
                                {transaction.status}
                                {transaction.status !== 'success' && (
                                    <button
                                        className="inline-block hover:bg-slate-100 text-gray-500 font-bold p-2 rounded-full text-sm"
                                        onClick={() =>
                                            syncTransaction(transaction)
                                        }
                                    >
                                        Sync
                                    </button>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default TransactionTable;
