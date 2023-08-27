import * as React from "react";
import { Field, FieldInputProps } from "formik";

import type { QBOAccount, QBOTaxCode, QBOVendor } from "../types";

const SelectInput = ({
  field,
  options = [],
  label,
  placeholder,
}: {
  field: FieldInputProps<string>;
  options: { value: string; label: string }[];
  placeholder: string;
  label: string;
}) => {
  return (
    <div className="mb-4 relative">
      <div>
        <label
          className="block text-gray-700 text-sm font-bold mb-2"
          htmlFor={field.name}
        >
          {label}
        </label>
      </div>
      <select
        {...field}
        className="block w-full bg-white border border-gray-400 hover:border-gray-500 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline"
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
          <svg
            className="fill-current h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
          >
            <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
          </svg>
        </div>
      </select>
    </div>
  );
};

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
    <Field
      name={name}
      label={label}
      as="select"
      component={SelectInput}
      placeholder="Select an account"
      options={accounts
        .filter((act: QBOAccount) => act.AccountType === accountType)
        .map((act: QBOAccount) => ({ value: act.Id, label: act.Name }))}
    />
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
    <Field
      label={label}
      name={name}
      as="select"
      placeholder="Select a vendor"
      component={SelectInput}
      options={vendors.map((vendor: QBOVendor) => ({
        value: vendor.Id,
        label: vendor.DisplayName,
      }))}
    />
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
    <Field
      name={name}
      label={label}
      as="select"
      placeholder="Select a tax code"
      component={SelectInput}
      options={taxCodes.map((taxCode: QBOTaxCode) => ({
        value: taxCode.Id,
        label: taxCode.Name,
      }))}
    />
  );
};
