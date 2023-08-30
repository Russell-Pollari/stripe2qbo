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
import getDefaultSettings from './getDefaultSettings';
import schema from './settingsFormSchema';

const SyncSettings = () => {
    const { data: companyInfo } = useGetCompanyInfoQuery('');
    const { data: accounts } = useGetAccountsQuery('', {
        skip: !companyInfo,
    });
    const { data: vendors } = useGetVendorsQuery('', {
        skip: !companyInfo,
    });
    const { data: taxCodes } = useGetTaxCodesQuery('', {
        skip: !companyInfo,
    });

    const { data: settings } = useGetSettingsQuery('', {
        skip: !companyInfo,
    });

    const [updateSettings] = useUpdateSettingsMutation();

    const defaultSettings = settings
        ? settings
        : getDefaultSettings({ accounts, vendors, taxCodes });

    return (
        <div className="w-64 shadow-lg p-4">
            <h3 className="font-semibold mb-4">Sync Settings</h3>
            {!companyInfo ? (
                <div className="text-center">Missing QBO connection</div>
            ) : (
                <Formik
                    validationSchema={schema}
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
                                <button
                                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded m-auto"
                                    disabled={isSubmitting}
                                    type="submit"
                                >
                                    {isSubmitting ? 'Saving...' : 'Save'}
                                </button>
                            </div>
                        </Form>
                    )}
                </Formik>
            )}
        </div>
    );
};

export default SyncSettings;
