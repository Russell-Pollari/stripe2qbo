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
import SubmitButton from '../SubmitButton';
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

    console.log(accounts);

    return (
        <div className="shadow-lg p-4">
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
