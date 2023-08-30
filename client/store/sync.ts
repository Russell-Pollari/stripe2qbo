import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export const syncSlice = createSlice({
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
