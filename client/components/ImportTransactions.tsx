import * as React from 'react';
import { Formik, Field, Form } from 'formik';
import { useDispatch, useSelector } from 'react-redux';
import { setIsSyncing, setSyncStatus } from '../store/sync';
import { addTransaction } from '../store/transactions';

import type { RootState } from '../store/store';
import type { SyncOptions, Transaction } from '../types';
import SubmitButton from './SubmitButton';
import { useGetStripeInfoQuery } from '../services/api';

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
        const response = await fetch('/stripe/transactions?' + queryString);

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
        <div>
            <div className="shadow-lg p-4">
                <h3 className="font-semibold mb-4">Stripe transactions</h3>
                <Formik
                    initialValues={{ from_date: '2023-08-28', to_date: '' }}
                    onSubmit={async (values: SyncOptions) => {
                        await importTransactions(values);
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
                                <SubmitButton isSubmitting={isSyncing}>
                                    {isSyncing ? `${status}...` : 'Import'}
                                </SubmitButton>
                            </div>
                        </div>
                    </Form>
                </Formik>
            </div>
        </div>
    );
};

export default ImportTransactions;
