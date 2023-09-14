import * as React from 'react';
import { Formik, Field, Form } from 'formik';
import { useDispatch, useSelector } from 'react-redux';
import { setIsSyncing, setSyncStatus } from '../store/sync';
import { addTransaction } from '../store/transactions';

import type { RootState } from '../store/store';
import type { SyncOptions, Transaction } from '../types';
import SubmitButton from './SubmitButton';
import { useGetStripeInfoQuery } from '../services/api';
import { Popover } from '@headlessui/react';

const ImportTransactions = () => {
    const dispatch = useDispatch();
    const isSyncing = useSelector((state: RootState) => state.sync.isSyncing);
    const status = useSelector((state: RootState) => state.sync.status);
    const { data: stripeInfo } = useGetStripeInfoQuery();

    const importTransactions = async (options: SyncOptions) => {
        if (!stripeInfo) {
            alert('No Stripe account connected.');
            return;
        }

        dispatch(setIsSyncing(true));
        dispatch(setSyncStatus('Importing transactions...'));

        const queryString = new URLSearchParams(options).toString();
        const response = await fetch('/api/stripe/transactions?' + queryString);

        if (response.status === 200) {
            const data: Transaction[] = await response.json();
            data.forEach((transaction: Transaction) => {
                dispatch(addTransaction(transaction));
            });
        } else {
            alert('Error importing transactions.');
        }

        dispatch(setSyncStatus(''));
        dispatch(setIsSyncing(false));
    };

    return (
        <div className="text-center">
            <Popover className="inline relative">
                <Popover.Button
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    disabled={!!status}
                >
                    {isSyncing ? `${status}...` : 'Import Stripe Transactions'}
                </Popover.Button>
                <Popover.Panel className="absolute z-10 bg-white p-4 left-0 shadow-lg text-left">
                    <Formik
                        initialValues={{ from_date: '2023-08-28', to_date: '' }}
                        onSubmit={async (values: SyncOptions) => {
                            await importTransactions(values);
                        }}
                    >
                        <Form>
                            <div className="flex justify-between mb-2">
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
                            <div className="text-center">
                                <Popover.Button
                                    as={SubmitButton}
                                    isSubmitting={isSyncing}
                                >
                                    Import
                                </Popover.Button>
                            </div>
                        </Form>
                    </Formik>
                </Popover.Panel>
            </Popover>
        </div>
    );
};

export default ImportTransactions;
