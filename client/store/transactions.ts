import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

type transactionState = {
    selectedTransactionId: string | null;
    selectedTransactionIds: string[];
    isImporting: boolean;
};

const initialState: transactionState = {
    selectedTransactionId: null,
    selectedTransactionIds: [],
    isImporting: false,
};

export const transactionsSlice = createSlice({
    name: 'transactions',
    initialState: initialState,
    reducers: {
        selectTransaction: (state, action: PayloadAction<null | string>) => {
            state.selectedTransactionId = action.payload;
        },
        selectTransactions: (state, action: PayloadAction<string[]>) => {
            state.selectedTransactionIds = action.payload;
        },
        setIsImporting: (state, action: PayloadAction<boolean>) => {
            state.isImporting = action.payload;
        },
    },
});

export const { selectTransaction, setIsImporting, selectTransactions } =
    transactionsSlice.actions;
