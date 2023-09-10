import * as React from 'react';
import { Dialog } from '@headlessui/react';
import { useDispatch } from 'react-redux';

import { Transaction } from '../types';
import { selectTransaction } from '../store/transactions';

const SyncDetails = ({ transaction }: { transaction: Transaction | null }) => {
    const dispatch = useDispatch();
    const isOpen = transaction !== null;

    return (
        <Dialog
            className="z-50 relative"
            open={isOpen}
            onClose={() => dispatch(selectTransaction(null))}
        >
            <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
            <div className="fixed inset-0 flex w-screen items-center justify-center p-4">
                <Dialog.Panel className="relative w-full max-w-2xl mx-auto rounded shadow-lg bg-white p-4">
                    {transaction && (
                        <>
                            <Dialog.Title>{transaction.id}</Dialog.Title>
                            <h2 className="text-lg font-semibold">
                                Sync Details
                            </h2>
                            {transaction.invoice_id && (
                                <p>
                                    <strong>Invoice:</strong>{' '}
                                    <a
                                        href={`https://app.qbo.intuit.com/app/invoice?txnId=${transaction.invoice_id}`}
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        {transaction.invoice_id}
                                    </a>
                                </p>
                            )}
                            {transaction.expense_id && (
                                <p>
                                    <strong>Expense:</strong>{' '}
                                    <a
                                        href={`https://app.qbo.intuit.com/app/check?txnId=${transaction.expense_id}`}
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        {transaction.expense_id}
                                    </a>
                                </p>
                            )}
                            {transaction.payment_id && (
                                <p>
                                    <strong>Payment:</strong>{' '}
                                    <a
                                        href={`https://app.qbo.intuit.com/app/recvpayment?txnId=${transaction.payment_id}`}
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        {transaction.payment_id}
                                    </a>
                                </p>
                            )}
                            {transaction.transfer_id && (
                                <p>
                                    <strong>Transfer:</strong>{' '}
                                    <a
                                        href={`https://app.qbo.intuit.com/app/transfer?txnId=${transaction.transfer_id}`}
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        {transaction.transfer_id}
                                    </a>
                                </p>
                            )}
                            <button
                                onClick={() =>
                                    dispatch(selectTransaction(null))
                                }
                            >
                                Close
                            </button>
                        </>
                    )}
                </Dialog.Panel>
            </div>
        </Dialog>
    );
};

export default SyncDetails;
