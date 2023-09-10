import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import {
    QBOCompanyInfo,
    QBOAccount,
    QBOTaxCode,
    QBOVendor,
    Settings,
    StripeInfo,
} from '../types';

export const api = createApi({
    reducerPath: 'api',
    baseQuery: fetchBaseQuery({
        baseUrl: '/api/',
    }),
    tagTypes: ['Settings', 'Stripe', 'User'],
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
} = api;
