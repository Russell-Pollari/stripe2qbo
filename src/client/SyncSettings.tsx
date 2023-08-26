import * as React from "react";
import { useEffect, useState } from "react";
import { Formik, Form, Field } from "formik";

import type { QBOAccount, QBOTaxCode, QBOVendor } from "./types";

const AccountSelect = ({
  label,
  name,
  accounts = [],
  accountType,
}: {
  label: string;
  name: string;
  accounts: QBOAccount[];
  accountType: string;
}) => {
  return (
    <div style={{ margin: 16 }}>
      <div>
        <label htmlFor={name}>{label}</label>
      </div>
      <Field name={name} as="select">
        {accounts
          .filter((act: QBOAccount) => act.AccountType === accountType)
          .map((act: QBOAccount) => (
            <option key={act.Id} value={act.Id}>
              {act.Name}
            </option>
          ))}
      </Field>
    </div>
  );
};

const VendorSelect = ({
  label,
  name,
  vendors = [],
}: {
  label: string;
  name: string;
  vendors: QBOVendor[];
}) => {
  return (
    <div style={{ margin: 16 }}>
      <div>
        <label htmlFor={name}>{label}</label>
      </div>
      <Field name={name} as="select">
        {vendors.map((vendor: QBOVendor) => (
          <option key={vendor.Id} value={vendor.Id}>
            {vendor.DisplayName}
          </option>
        ))}
      </Field>
    </div>
  );
};

const TaxCodeSelect = ({
  label,
  name,
  taxCodes = [],
}: {
  label: string;
  name: string;
  taxCodes: QBOTaxCode[];
}) => {
  return (
    <div style={{ margin: 16 }}>
      <div>
        <label htmlFor={name}>{label}</label>
      </div>
      <Field name={name} as="select">
        {taxCodes.map((taxCode: QBOTaxCode) => (
          <option key={taxCode.Id} value={taxCode.Id}>
            {taxCode.Name}
          </option>
        ))}
      </Field>
    </div>
  );
};

const getDefaultSettings = ({
  accounts = [],
  vendors = [],
  taxCodes = [],
}: {
  accounts: QBOAccount[];
  vendors: QBOVendor[];
  taxCodes: QBOTaxCode[];
}) => {
  return {
    stripeClearingAccount: accounts.find(
      (act: QBOAccount) => act.Name === "Stripe"
    )?.Id,
    stripePayoutAccount: accounts.find(
      (act: QBOAccount) => act.Name === "Checking"
    )?.Id,
    stripeVendor: vendors.find(
      (vendor: QBOVendor) => vendor.DisplayName === "Stripe"
    )?.Id,
    stripeExpenseAccount: accounts.find(
      (act: QBOAccount) => act.Name === "Stripe fees"
    )?.Id,
    defaultIncomeAccount: accounts.find(
      (act: QBOAccount) => act.Name === "Sales"
    )?.Id,
    defaultTaxCode: taxCodes.find(
      (taxCode: QBOTaxCode) => taxCode.Name === "TAX"
    )?.Id,
    exemptTaxCode: taxCodes.find(
      (taxCode: QBOTaxCode) => taxCode.Name === "NON"
    )?.Id,
  };
};

const SyncSettings = () => {
  const [accounts, setAccounts] = useState<QBOAccount[]>([]);
  const [vendors, setVendors] = useState<QBOVendor[]>([]);
  const [taxCodes, setTaxCodea] = useState<QBOTaxCode[]>([]);

  useEffect(() => {
    fetch("/qbo/accounts")
      .then((response) => response.json())
      .then((data) => {
        if (data) {
          setAccounts(data);
        }
      });
  }, []);

  useEffect(() => {
    fetch("/qbo/vendors")
      .then((response) => response.json())
      .then((data) => {
        if (data) {
          setVendors(data);
        }
      });
  }, []);

  useEffect(() => {
    fetch("/qbo/taxcodes")
      .then((response) => response.json())
      .then((data) => {
        if (data) {
          setTaxCodea(data);
        }
      });
  }, []);

  const defaultSettings = getDefaultSettings({ accounts, vendors, taxCodes });
  // TODO: load settings from db?

  return (
    <div>
      <h3>Settings</h3>
      <Formik
        initialValues={{
          ...defaultSettings,
        }}
        onSubmit={(values, { setSubmitting }) => {
          console.log(values);
          setSubmitting(false);
        }}
        enableReinitialize
      >
        <Form>
          <AccountSelect
            label="Stripe Clearing Account"
            name="stripeClearingAccount"
            accounts={accounts}
            accountType="Bank"
          />
          <AccountSelect
            label="Stripe Payout Account"
            name="stripePayoutAccount"
            accounts={accounts}
            accountType="Bank"
          />
          <VendorSelect
            label="Stripe Vendor"
            name="stripeVendor"
            vendors={vendors}
          />
          <AccountSelect
            label="Stripe Expense Account"
            name="stripeExpenseAccount"
            accounts={accounts}
            accountType="Expense"
          />
          <AccountSelect
            label="Default Income Account"
            name="defaultIncomeAccount"
            accounts={accounts}
            accountType="Income"
          />
          <h4>Tax Codes</h4>
          <TaxCodeSelect
            label="Default Tax Code"
            name="defaultTaxCode"
            taxCodes={taxCodes}
          />
          <TaxCodeSelect
            label="Exempt Tax Code"
            name="exemptTaxCode"
            taxCodes={taxCodes}
          />
        </Form>
      </Formik>
    </div>
  );
};

export default SyncSettings;
