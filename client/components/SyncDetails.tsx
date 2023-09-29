import * as React from 'react';
import {
    XMarkIcon,
    ArrowTopRightOnSquareIcon,
    ChevronRightIcon,
} from '@heroicons/react/24/solid';
import { useDispatch, useSelector } from 'react-redux';

import type { Transaction } from '../types';
import type { RootState } from '../store/store';
import { setExpandedTransactionId } from '../store/transactions';
import numToAccountingString from '../numToAccountingString';
import { useGetTransactionsQuery } from '../services/api';
import SyncStatus from './SyncStatus';

const SyncItem = ({ label, href }: { label: string; href: string }) => {
    return (
        <p className="text-gray-500 mb-4">
            <ChevronRightIcon className="w-4 h-4 inline m-px" />
            Created{' '}
            <a
                href={href}
                target="_blank"
                rel="noreferrer"
                className="text-blue-600 hover:text-blue-700"
            >
                {label}{' '}
                <ArrowTopRightOnSquareIcon className="w-4 h-4 inline m-px" />
            </a>
        </p>
    );
};

const StripeTransactionDetais = ({
    transaction,
}: {
    transaction: Transaction;
}) => {
    return (
        <div className="mb-4">
            <p>{transaction.description}</p>
            <p className="text-xs text-gray-500 mb-4">{transaction.id}</p>

            <p className="my-2 text-gray-700">
                {transaction.currency.toUpperCase()}{' '}
                {numToAccountingString(transaction.amount)}{' '}
                {!!transaction.fee && (
                    <span className="text-sm font-normal text-gray-600">
                        ({numToAccountingString(transaction.fee)} Stripe fee)
                    </span>
                )}
            </p>
        </div>
    );
};

const SyncDetails = ({ drawerWidth = 320 }: { drawerWidth: number }) => {
    const dispatch = useDispatch();
    const expandedTransactionId = useSelector(
        (state: RootState) => state.transactions.expandedTransactionId
    );

    const { transaction } = useGetTransactionsQuery(undefined, {
        selectFromResult: ({ data }) => ({
            transaction: data?.find(
                (transaction: Transaction) =>
                    transaction.id === expandedTransactionId
            ),
        }),
    });

    if (!expandedTransactionId) return null;

    return (
        <div
            style={{ width: `${drawerWidth}px` }}
            className="fixed z-40 top-16 right-0 h-screen shadow-xl border-l border-solid border-gray-500 bg-gray-50"
        >
            <div className="px-4 py-2 flex justify-between border-b border-solid border-gray-300 bg-gray-100">
                <div className="mb-2">
                    <span className="text-xl">
                        {transaction.type.slice(0, 1).toUpperCase()}
                        {transaction.type.slice(1)}
                    </span>

                    <span className="text-sm text-gray-600 ml-2">
                        {new Date(transaction.created * 1000)
                            .toISOString()
                            .slice(0, 10)}
                    </span>
                </div>
                <button
                    className="rounded-full w-6 h-6 m-2 text-gray-500 hover:text-gray-800"
                    onClick={() => dispatch(setExpandedTransactionId(null))}
                >
                    <XMarkIcon className="w-6" />
                </button>
            </div>
            <div className="p-4 pr-6">
                <StripeTransactionDetais transaction={transaction} />

                <div className="mt-4">
                    <SyncStatus
                        status={transaction.status}
                        id={transaction.id}
                    />
                </div>

                <div className="mt-2">
                    {!!transaction.failure_reason && (
                        <p className="text-red-400">
                            {transaction.failure_reason}
                        </p>
                    )}
                    {transaction.invoice_id && (
                        <SyncItem
                            label="Invoice"
                            href={`https://app.qbo.intuit.com/app/invoice?txnId=${transaction.invoice_id}`}
                        />
                    )}
                    {transaction.payment_id && (
                        <SyncItem
                            label="Payment"
                            href={`https://app.qbo.intuit.com/app/recvpayment?txnId=${transaction.payment_id}`}
                        />
                    )}
                    {transaction.expense_id && (
                        <SyncItem
                            label="Expense"
                            href={`https://app.qbo.intuit.com/app/check?txnId=${transaction.expense_id}`}
                        />
                    )}
                    {transaction.transfer_id && (
                        <SyncItem
                            label="Transfer"
                            href={`https://app.qbo.intuit.com/app/transfer?txnId=${transaction.transfer_id}`}
                        />
                    )}
                </div>
            </div>
        </div>
    );
};

export default SyncDetails;
