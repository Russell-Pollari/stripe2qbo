import * as React from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { addTransaction, selectTransaction } from '../store/transactions';
import { setIsSyncing, setSyncStatus } from '../store/sync';
import type { RootState } from '../store/store';
import type { Transaction } from '../types';
import SyncDetails from './SyncDetails';

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
            {selectedTransaction !== null && (
                <SyncDetails transaction={transactions[selectedTransaction]} />
            )}
            <div className="text-right">
                <button
                    className="inline-block hover:bg-slate-100 text-gray-500 font-bold p-2 rounded-full text-sm"
                    onClick={syncAll}
                >
                    Sync all
                </button>
            </div>
            <table className="text-left table-auto w-full">
                <thead>
                    <tr className="border-b-2 border-green-300">
                        <th>Type</th>
                        <th className="text-right">Amount</th>
                        <th className="text-right">Fee</th>
                        <th />
                        <th>Description</th>
                        <th>Created</th>
                        <th>Sync status</th>
                        <th />
                    </tr>
                </thead>
                <tbody className="text-gray-700">
                    {transactions.map(
                        (transaction: Transaction, index: number) => (
                            <tr key={transaction.id}>
                                <td className="font-semibold text-black">
                                    {transaction.type}
                                </td>

                                <td className="text-right">
                                    {formatAmount(transaction.amount)}
                                </td>
                                <td className="text-right">
                                    ({formatAmount(transaction.fee)})
                                </td>
                                <td className="px-2">
                                    {transaction.currency.toUpperCase()}
                                </td>
                                <td>{transaction.description}</td>
                                <td>
                                    {new Date(transaction.created * 1000)
                                        .toDateString()
                                        .slice(0, 10)}
                                </td>
                                <td>
                                    {transaction.status}
                                    {transaction.status !== 'success' && (
                                        <button
                                            className="inline-block bg-slate-300 hover:bg-slate-500 text-gray-800 font-bold p-2 rounded-full text-sm"
                                            onClick={() =>
                                                syncTransaction(transaction)
                                            }
                                        >
                                            Sync
                                        </button>
                                    )}
                                </td>
                                <td>
                                    <button
                                        className="inline-block bg-slate-300 hover:bg-slate-500 text-gray-800 font-bold p-2 rounded-full text-sm"
                                        onClick={() =>
                                            dispatch(selectTransaction(index))
                                        }
                                    >
                                        View details
                                    </button>
                                </td>
                            </tr>
                        )
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default TransactionTable;
