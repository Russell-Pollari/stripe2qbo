import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

type transactionState = {
    expandedTransactionId: string | null;
    selectedTransactionIds: string[];
    isImporting: boolean;
};

const initialState: transactionState = {
    expandedTransactionId: null,
    selectedTransactionIds: [],
    isImporting: false,
};

export const transactionsSlice = createSlice({
    name: 'transactions',
    initialState: initialState,
    reducers: {
        setExpandedTransactionId: (
            state,
            action: PayloadAction<null | string>
        ) => {
            state.expandedTransactionId = action.payload;
        },
        selectTransactionIds: (state, action: PayloadAction<string[]>) => {
            state.selectedTransactionIds = action.payload;
        },
        setIsImporting: (state, action: PayloadAction<boolean>) => {
            state.isImporting = action.payload;
        },
    },
});

export const {
    setExpandedTransactionId,
    setIsImporting,
    selectTransactionIds,
} = transactionsSlice.actions;
