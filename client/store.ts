import { configureStore } from '@reduxjs/toolkit';
import { api } from './services/api';

import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Transaction } from './types';

const syncSlice = createSlice({
    name: 'sync',
    initialState: {
        isSyncing: false,
        status: '',
    },
    reducers: {
        setIsSyncing: (state, action: PayloadAction<boolean>) => {
            state.isSyncing = action.payload;
        },
        setSyncStatus: (state, action: PayloadAction<string>) => {
            state.status = action.payload;
        },
    },
});

export const { setIsSyncing, setSyncStatus } = syncSlice.actions;

const initialState: Transaction[] = [];
const transactionsSlice = createSlice({
    name: 'transactions',
    initialState: initialState,
    reducers: {
        addTransaction: (state, action: PayloadAction<Transaction>) => {
            state.push(action.payload);
        },
    },
});

export const { addTransaction } = transactionsSlice.actions;

export const store = configureStore({
    reducer: {
        [api.reducerPath]: api.reducer,
        sync: syncSlice.reducer,
        transactions: transactionsSlice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware().concat(api.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
