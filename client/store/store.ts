import { configureStore } from '@reduxjs/toolkit';
import { api } from '../services/api';

import { syncSlice } from './sync';
import { transactionsSlice } from './transactions';

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
