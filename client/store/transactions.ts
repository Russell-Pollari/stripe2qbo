import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Transaction } from '../types';

const initialState: Transaction[] = [];

export const transactionsSlice = createSlice({
    name: 'transactions',
    initialState: initialState,
    reducers: {
        addTransaction: (state, action: PayloadAction<Transaction>) => {
            const txn = state.find(
                (t: Transaction) => t.id === action.payload.id
            );
            if (txn && action.payload.status) {
                txn.status = action.payload.status;
            } else {
                state.push(action.payload);
            }
        },
    },
});

export const { addTransaction } = transactionsSlice.actions;
