import * as React from 'react';
import { Formik, Form } from 'formik';

import {
    useGetAccountsQuery,
    useGetTaxCodesQuery,
    useGetVendorsQuery,
    useGetCompanyInfoQuery,
    useGetSettingsQuery,
    useUpdateSettingsMutation,
} from '../../services/api';
import type { Settings } from '../../types';
import { AccountSelect, VendorSelect, TaxCodeSelect } from './Inputs';
import LoadingSpinner from '../LoadingSpinner';
import SubmitButton from '../SubmitButton';
import getDefaultSettings from './getDefaultSettings';
import schema from './settingsFormSchema';

const SyncSettings = () => {
    const { data: companyInfo } = useGetCompanyInfoQuery();
    const { data: accounts, isLoading: isLoadingAccounts } =
        useGetAccountsQuery('', {
            skip: !companyInfo,
        });
    const { data: vendors, isLoading: isLoadingVendors } = useGetVendorsQuery(
        '',
        {
            skip: !companyInfo,
        }
    );
    const { data: taxCodes, isLoading: isLoadingTaxCodes } =
        useGetTaxCodesQuery('', {
            skip: !companyInfo,
        });

    const { data: settings, isLoading: isLoadingSettings } =
        useGetSettingsQuery('', {
            skip: !companyInfo,
        });

    const [updateSettings] = useUpdateSettingsMutation();

    const defaultSettings = settings
        ? settings
        : getDefaultSettings({ accounts, vendors, taxCodes });

    const isLoading =
        !companyInfo ||
        isLoadingAccounts ||
        isLoadingVendors ||
        isLoadingTaxCodes ||
        isLoadingSettings;

    return (
        <div className="shadow-lg p-4">
            {isLoading ? (
                <div className="flex justify-center">
                    <LoadingSpinner className="inline-block h-8 w-8" />
                </div>
            ) : (
                <Formik
                    validationSchema={schema}
                    validateOnBlur={false}
                    validateOnChange={false}
                    initialValues={defaultSettings}
                    onSubmit={async (values: Settings, { setSubmitting }) => {
                        await updateSettings(values);
                        setSubmitting(false);
                    }}
                    enableReinitialize
                >
                    {({ isSubmitting }) => (
                        <Form>
                            <AccountSelect
                                label="Stripe Clearing Account"
                                name="stripeClearingAccountId"
                                accounts={accounts}
                                accountType="Bank"
                            />
                            <AccountSelect
                                label="Stripe Payout Account"
                                name="stripePayoutAccountId"
                                accounts={accounts}
                                accountType="Bank"
                            />
                            <VendorSelect
                                label="Stripe Vendor"
                                name="stripeVendorId"
                                vendors={vendors}
                            />
                            <AccountSelect
                                label="Stripe Expense Account"
                                name="stripeFeeAccountId"
                                accounts={accounts}
                                accountType="Expense"
                            />
                            <AccountSelect
                                label="Default Income Account"
                                name="defaultIncomeAccountId"
                                accounts={accounts}
                                accountType="Income"
                            />
                            <h4 className="mb-4 font-bold">Tax Codes</h4>
                            <TaxCodeSelect
                                label="Default Tax Code"
                                name="defaultTaxCodeId"
                                taxCodes={taxCodes}
                            />
                            <TaxCodeSelect
                                label="Exempt Tax Code"
                                name="exemptTaxCodeId"
                                taxCodes={taxCodes}
                            />
                            <div className="text-center mt-4">
                                <SubmitButton isSubmitting={isSubmitting}>
                                    {isSubmitting ? 'Saving...' : 'Save'}
                                </SubmitButton>
                            </div>
                        </Form>
                    )}
                </Formik>
            )}
        </div>
    );
};

export default SyncSettings;
