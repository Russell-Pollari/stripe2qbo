import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type {
    QBOCompanyInfo,
    QBOAccount,
    QBOTaxCode,
    QBOVendor,
    Settings,
    StripeInfo,
    Transaction,
    SyncOptions, // TODO: Rename to ImportOptions
    User,
} from '../types';

export const api = createApi({
    reducerPath: 'api',
    baseQuery: fetchBaseQuery({
        baseUrl: '/api/',
    }),
    tagTypes: ['Settings', 'Stripe', 'User', 'Transaction', 'QBO'],
    endpoints: (builder) => ({
        // AUTH
        login: builder.mutation<void, { email: string; password: string }>({
            query: (body) => {
                return {
                    url: 'token',
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams([
                        ['username', body.email],
                        ['password', body.password],
                    ]),
                };
            },
            invalidatesTags: ['User'],
        }),
        logout: builder.mutation<void, void>({
            query: () => ({
                url: 'logout',
                method: 'POST',
            }),
        }),
        signup: builder.mutation<void, { email: string; password: string }>({
            query: (body) => {
                return {
                    url: 'signup',
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams([
                        ['username', body.email],
                        ['password', body.password],
                    ]),
                };
            },
            invalidatesTags: ['User'],
        }),
        getCurrentUser: builder.query<User, void>({
            query: () => 'userId',
            providesTags: ['User'],
        }),

        // STRIPE
        setStripeToken: builder.mutation<void, string>({
            query: (code) => ({
                url: 'stripe/oauth2/callback?code=' + code,
                method: 'POST',
            }),
            invalidatesTags: ['User', 'Stripe'],
        }),
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
        setQBOToken: builder.mutation<void, { code: string; realmId: string }>({
            query: (body) => ({
                url:
                    'qbo/oauth2/callback?code=' +
                    body.code +
                    '&realmId=' +
                    body.realmId,
                method: 'POST',
            }),
            invalidatesTags: ['User', 'QBO'],
        }),
        disconnectQBO: builder.mutation<void, void>({
            query: () => ({
                url: 'qbo/disconnect',
                method: 'POST',
            }),
            invalidatesTags: ['User'],
        }),
        getCompanyInfo: builder.query<QBOCompanyInfo, void>({
            query: () => 'qbo/info',
            providesTags: ['QBO'],
        }),
        getAccounts: builder.query<QBOAccount[], string>({
            query: () => 'qbo/accounts',
            providesTags: ['QBO'],
        }),
        getVendors: builder.query<QBOVendor[], string>({
            query: () => 'qbo/vendors',
            providesTags: ['QBO'],
        }),
        getTaxCodes: builder.query<QBOTaxCode[], string>({
            query: () => 'qbo/taxcodes',
            providesTags: ['QBO'],
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
                const HOST = process.env.HOST;
                const PROTOCOL = process.env.SSL ? 'wss' : 'ws';
                const ws = new WebSocket(`${PROTOCOL}://${HOST}/api/sync/ws`);

                try {
                    await cacheDataLoaded;

                    const listener = (event: { data: string }) => {
                        // TODO: Validate that the data is a valid Transaction object
                        const data: Transaction = JSON.parse(
                            event.data
                        ) as Transaction;

                        updateCachedData((draft) => {
                            const index = draft.findIndex(
                                (t: Transaction) => t.id === data.id
                            );
                            draft[index] = data;
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
            async onQueryStarted(
                transaction_ids,
                { dispatch, queryFulfilled }
            ) {
                // Optimistically update the status of the transactions to 'syncing'
                const patchResult = dispatch(
                    api.util.updateQueryData(
                        'getTransactions',
                        undefined,
                        (draft: Transaction[]) => {
                            draft.forEach((t) => {
                                if (transaction_ids.includes(t.id)) {
                                    Object.assign(t, { status: 'syncing' });
                                }
                            });
                        }
                    )
                );
                try {
                    await queryFulfilled;
                } catch (error) {
                    console.error(error);
                    patchResult.undo();
                }
            },
            invalidatesTags: ['Transaction'],
        }),
    }),
});

export const {
    useLoginMutation,
    useLogoutMutation,
    useSignupMutation,
    useGetCurrentUserQuery,

    useSetStripeTokenMutation,
    useGetStripeInfoQuery,
    useDisconnectStripeMutation,

    useSetQBOTokenMutation,
    useDisconnectQBOMutation,
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
