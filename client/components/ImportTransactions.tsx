import * as React from 'react';
import { Formik, Field, Form } from 'formik';
import { useDispatch, useSelector } from 'react-redux';
import { Popover } from '@headlessui/react';

import type { SyncOptions, Transaction } from '../types';
import type { RootState } from '../store/store';
import { addTransaction, setIsImporting } from '../store/transactions';
import { useGetStripeInfoQuery } from '../services/api';
import SubmitButton from './SubmitButton';
import LoadingSpinner from './LoadingSpinner';

const ImportTransactions = () => {
    const dispatch = useDispatch();
    const isImporting = useSelector(
        (state: RootState) => state.transactions.isImporting
    );
    const { data: stripeInfo } = useGetStripeInfoQuery();

    const importTransactions = async (options: SyncOptions) => {
        if (!stripeInfo) {
            alert('No Stripe account connected.');
            return;
        }

        dispatch(setIsImporting(true));

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

        dispatch(setIsImporting(false));
    };

    return (
        <div className="text-left">
            <Popover className="inline relative">
                <Popover.Button
                    className="bg-green-300 hover:bg-green-500 text-slate-800 text-sm py-2 px-4 rounded"
                    disabled={!!isImporting}
                >
                    {isImporting ? (
                        <span>
                            <LoadingSpinner /> Importing
                        </span>
                    ) : (
                        'Import Stripe Transactions'
                    )}
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
                                    isSubmitting={isImporting}
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
