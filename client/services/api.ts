import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import {
    QBOCompanyInfo,
    QBOAccount,
    QBOTaxCode,
    QBOVendor,
    Settings,
    StripeInfo,
    SyncOptions,
} from '../types';

export const api = createApi({
    reducerPath: 'api',
    baseQuery: fetchBaseQuery({
        baseUrl: '/',
    }),
    tagTypes: ['Settings', 'Stripe'],
    endpoints: (builder) => ({
        // STRIPE
        getStripeInfo: builder.query<StripeInfo, string>({
            query: () => 'stripe/info',
        }),
        disconnectStripe: builder.mutation<StripeInfo, string>({
            query: () => ({
                url: 'stripe/disconnect',
                method: 'POST',
            }),
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
        disconnectQBO: builder.mutation<QBOCompanyInfo, string>({
            query: () => ({
                url: 'qbo/disconnect',
                method: 'POST',
            }),
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
    }),
});

export const {
    useGetStripeInfoQuery,
    useDisconnectStripeMutation,

    useGetAccountsQuery,
    useGetTaxCodesQuery,
    useGetVendorsQuery,
    useGetCompanyInfoQuery,
    useDisconnectQBOMutation,

    useGetSettingsQuery,
    useUpdateSettingsMutation,
} = api;
