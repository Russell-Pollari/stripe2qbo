import * as React from 'react';
import { Formik, Field, Form } from 'formik';

import type { SyncOptions, Transaction } from '../types';

const Sync = () => {
    const [isSyncing, setIsSyncing] = React.useState<boolean>(false);
    const [status, setStatus] = React.useState<string>('');
    const [transactions, setTransactions] = React.useState<Transaction[]>([]);

    const startSync = (options: SyncOptions) => {
        const queryString = new URLSearchParams(options).toString();
        const ws = new WebSocket(`ws://localhost:8000/sync?${queryString}`);
        ws.onopen = () => {
            setIsSyncing(true);
        };
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.status) {
                setStatus(data.status);
            }
            if (data.transaction) {
                setTransactions((prevTransactions: Transaction[]) => [
                    ...prevTransactions,
                    data.transaction,
                ]);
            }
        };
        ws.onclose = () => {
            setIsSyncing(false);
        };
    };

    return (
        <div>
            <div className="shadow-lg p-4">
                <h3 className="font-semibold mb-4">Sync Transactions</h3>
                <Formik
                    initialValues={{ from_date: '2023-08-28', to_date: '' }}
                    onSubmit={(values: SyncOptions) => {
                        startSync(values);
                    }}
                >
                    <Form>
                        <div className="flex justify-between">
                            <div>
                                <label
                                    className="font-semibold mx-2"
                                    htmlFor="from_date"
                                >
                                    From:
                                </label>
                                <Field
                                    id="from_date"
                                    name="from_date"
                                    type="date"
                                />
                                <label
                                    className="font-semibold mx-2"
                                    htmlFor="to_date"
                                >
                                    To:
                                </label>
                                <Field
                                    id="to_date"
                                    name="to_date"
                                    type="date"
                                />
                            </div>
                            <div>
                                <button
                                    disabled={isSyncing}
                                    className="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                                >
                                    {isSyncing
                                        ? `${status}...`
                                        : 'Import and sync'}
                                </button>
                            </div>
                        </div>
                    </Form>
                </Formik>
            </div>

            <div className="text-left mt-4 p-4 shadow-lg">
                <table className="text-left table-auto w-full">
                    <thead>
                        <tr>
                            <th>Created</th>
                            <th>Type</th>
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
                                <td>{transaction.description}</td>
                                <td>{transaction.status}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Sync;
