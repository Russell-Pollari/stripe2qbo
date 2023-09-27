import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

type transactionState = {
    selectedTransactionId: number | string;
    isImporting: boolean;
};

const initialState: transactionState = {
    selectedTransactionId: null,
    isImporting: false,
};

export const transactionsSlice = createSlice({
    name: 'transactions',
    initialState: initialState,
    reducers: {
        selectTransaction: (state, action: PayloadAction<null | string>) => {
            state.selectedTransactionId = action.payload;
        },
        setIsImporting: (state, action: PayloadAction<boolean>) => {
            state.isImporting = action.payload;
        },
    },
});

export const { selectTransaction, setIsImporting } = transactionsSlice.actions;
