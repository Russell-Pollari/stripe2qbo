import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Transaction } from '../types';

type transactionState = {
    transactions: Transaction[];
    selectedTransaction: number | null;
};

const initialState: transactionState = {
    transactions: [],
    selectedTransaction: null,
};

export const transactionsSlice = createSlice({
    name: 'transactions',
    initialState: initialState,
    reducers: {
        addTransaction: (state, action: PayloadAction<Transaction>) => {
            const txn = state.transactions.find(
                (t: Transaction) => t.id === action.payload.id
            );
            if (txn && action.payload.status) {
                txn.status = action.payload.status;
                txn.invoice_id = action.payload.invoice_id;
                txn.expense_id = action.payload.expense_id;
                txn.payment_id = action.payload.payment_id;
                txn.transfer_id = action.payload.transfer_id;
            } else {
                state.transactions.push(action.payload);
            }
        },
        selectTransaction: (state, action: PayloadAction<null | string>) => {
            if (action.payload === null) {
                state.selectedTransaction = null;
                return;
            }
            const index = state.transactions.findIndex(
                (t) => t.id === action.payload
            );
            state.selectedTransaction = index;
        },
    },
});

export const { addTransaction, selectTransaction } = transactionsSlice.actions;
