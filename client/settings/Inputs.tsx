import * as React from "react";
import { Field } from "formik";

import type { QBOAccount, QBOTaxCode, QBOVendor } from "../types";

export const AccountSelect = ({
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
        <option value="" default>
          Select an account
        </option>
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

export const VendorSelect = ({
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
        <option value="" default>
          Select a vendor
        </option>
        {vendors.map((vendor: QBOVendor) => (
          <option key={vendor.Id} value={vendor.Id}>
            {vendor.DisplayName}
          </option>
        ))}
      </Field>
    </div>
  );
};

export const TaxCodeSelect = ({
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
        <option value="" default>
          Select a tax code
        </option>
        {taxCodes.map((taxCode: QBOTaxCode) => (
          <option key={taxCode.Id} value={taxCode.Id}>
            {taxCode.Name}
          </option>
        ))}
      </Field>
    </div>
  );
};
