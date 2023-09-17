import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Transaction } from '../types';

type transactionState = {
    transactions: Transaction[];
    selectedTransaction: number | null;
    syncingTransactions: string[];
    isImporting: boolean;
};

const initialState: transactionState = {
    transactions: [],
    selectedTransaction: null,
    syncingTransactions: [],
    isImporting: false,
};

export const transactionsSlice = createSlice({
    name: 'transactions',
    initialState: initialState,
    reducers: {
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
        setIsImporting: (state, action: PayloadAction<boolean>) => {
            state.isImporting = action.payload;
        },
    },
});

export const { selectTransaction, setIsImporting } = transactionsSlice.actions;
