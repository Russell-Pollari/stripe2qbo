import * as React from 'react';
import { Formik, Field, Form } from 'formik';
import { useDispatch, useSelector } from 'react-redux';
import { Popover } from '@headlessui/react';
import { ArrowDownOnSquareIcon } from '@heroicons/react/24/outline';

import type { SyncOptions } from '../types';
import type { RootState } from '../store/store';
import { setIsImporting } from '../store/transactions';
import {
    useGetStripeInfoQuery,
    useImportTransactionsMutation,
} from '../services/api';
import SubmitButton from './SubmitButton';
import LoadingSpinner from './LoadingSpinner';

const ImportTransactions = () => {
    const dispatch = useDispatch();
    const isImporting = useSelector(
        (state: RootState) => state.transactions.isImporting
    );
    const { data: stripeInfo } = useGetStripeInfoQuery();
    const [importTransactions] = useImportTransactionsMutation();

    const handleSubmit = async (options: SyncOptions) => {
        if (!stripeInfo) {
            alert('No Stripe account connected.');
            return;
        }
        dispatch(setIsImporting(true));
        await importTransactions(options);

        dispatch(setIsImporting(false));
    };

    return (
        <Popover className="inline relative">
            <Popover.Button
                className="text-green-800 bg-green-100 hover:bg-green-200 text-semibold text-sm py-2 px-4 rounded-full border border-green-800 mr-4"
                disabled={!!isImporting}
            >
                {isImporting ? (
                    <span>
                        <LoadingSpinner /> Importing transactions...
                    </span>
                ) : (
                    <span>
                        <ArrowDownOnSquareIcon className="inline-block mr-1 h-4 w-4 -mt-px" />{' '}
                        Import Stripe Transactions
                    </span>
                )}
            </Popover.Button>
            <Popover.Panel className="absolute z-10 bg-white p-4 left-0 shadow-lg text-left">
                <Formik
                    initialValues={{ from_date: '2023-08-28', to_date: '' }}
                    onSubmit={async (values: SyncOptions) => {
                        await handleSubmit(values);
                    }}
                >
                    <Form>
                        <div className="flex justify-between items-center my-2">
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
                        </div>
                        <div className="flex justify-between items-center my-2">
                            <label
                                className="font-semibold mx-2"
                                htmlFor="to_date"
                            >
                                To:
                            </label>
                            <Field id="to_date" name="to_date" type="date" />
                        </div>
                        <div className="text-center">
                            <Popover.Button
                                as={SubmitButton}
                                isSubmitting={isImporting}
                            >
                                {isImporting ? 'Importing..' : 'Import'}
                            </Popover.Button>
                        </div>
                    </Form>
                </Formik>
            </Popover.Panel>
        </Popover>
    );
};

export default ImportTransactions;
