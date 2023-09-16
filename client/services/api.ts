import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import {
    QBOCompanyInfo,
    QBOAccount,
    QBOTaxCode,
    QBOVendor,
    Settings,
    StripeInfo,
    Transaction,
    SyncOptions, // TODO: Rename to ImportOptions
} from '../types';

export const api = createApi({
    reducerPath: 'api',
    baseQuery: fetchBaseQuery({
        baseUrl: '/api/',
    }),
    tagTypes: ['Settings', 'Stripe', 'User', 'Transaction'],
    endpoints: (builder) => ({
        // AUTH
        getCurrentUser: builder.query<number, void>({
            query: () => 'userId',
            providesTags: ['User'],
        }),
        logout: builder.mutation<void, void>({
            query: () => ({
                url: 'logout',
                method: 'POST',
            }),
            invalidatesTags: ['User'],
        }),

        // STRIPE
        getStripeInfo: builder.query<StripeInfo, void>({
            query: () => 'stripe/info',
            providesTags: ['Stripe'],
        }),
        disconnectStripe: builder.mutation<StripeInfo, void>({
            query: () => ({
                url: 'stripe/disconnect',
                method: 'POST',
            }),
            invalidatesTags: ['Stripe'],
        }),

        // QBO
        getCompanyInfo: builder.query<QBOCompanyInfo, string>({
            query: () => 'qbo/info',
        }),
        getAccounts: builder.query<QBOAccount[], string>({
            query: () => 'qbo/accounts',
        }),
        getVendors: builder.query<QBOVendor[], string>({
            query: () => 'qbo/vendors',
        }),
        getTaxCodes: builder.query<QBOTaxCode[], string>({
            query: () => 'qbo/taxcodes',
        }),

        // settings
        getSettings: builder.query<Settings, string>({
            query: () => 'settings',
            providesTags: ['Settings'],
        }),
        updateSettings: builder.mutation<Settings, Settings>({
            query: (body) => ({
                url: 'settings',
                method: 'POST',
                body,
            }),
            invalidatesTags: ['Settings'],
        }),

        // transactions
        getTransactions: builder.query<Transaction[], void>({
            query: () => `transaction/`,
            providesTags: ['Transaction'],
            async onCacheEntryAdded(
                _,
                { updateCachedData, cacheDataLoaded, cacheEntryRemoved }
            ) {
                const ws = new WebSocket('ws://localhost:8000/api/sync/ws');
                try {
                    await cacheDataLoaded;

                    const listener = (event: { data: string }) => {
                        const data = JSON.parse(event.data);

                        updateCachedData((draft) => {
                            const index = draft.findIndex(
                                (t) => t.id === data.id
                            );
                            draft[index].status = data.status;
                        });
                    };
                    ws.addEventListener('message', listener);
                } catch (error) {
                    console.error('Webhook Error:', error);
                }
                await cacheEntryRemoved;
                ws.close();
            },
        }),
        importTransactions: builder.mutation<string, SyncOptions>({
            query: (options) => {
                const queryString = new URLSearchParams(options).toString();

                return {
                    url: `stripe/transactions?${queryString}`,
                    method: 'POST',
                };
            },
            invalidatesTags: ['Transaction'],
        }),
        syncTransactions: builder.mutation<string, string[]>({
            query: (transaction_ids) => {
                const ids = transaction_ids.map((id) => [
                    'transaction_ids',
                    id,
                ]);
                const queryString = new URLSearchParams(ids).toString();
                return {
                    url: `sync?${queryString}`,
                    method: 'POST',
                };
            },
            invalidatesTags: ['Transaction'],
        }),
    }),
});

export const {
    useGetCurrentUserQuery,
    useLogoutMutation,

    useGetStripeInfoQuery,
    useDisconnectStripeMutation,

    useGetAccountsQuery,
    useGetTaxCodesQuery,
    useGetVendorsQuery,
    useGetCompanyInfoQuery,

    useGetSettingsQuery,
    useUpdateSettingsMutation,

    useGetTransactionsQuery,
    useImportTransactionsMutation,
    useSyncTransactionsMutation,
} = api;
