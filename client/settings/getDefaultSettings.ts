import type { QBOAccount, QBOVendor, QBOTaxCode, Settings } from "../types";
/*
    This function takes in the accounts, vendors, and taxCodes from the QBO API 
    and looks for some sensible defaults for syncing with Stripe.
*/
const getDefaultSettings = ({
  accounts = [],
  vendors = [],
  taxCodes = [],
}: {
  accounts: QBOAccount[],
  vendors: QBOVendor[],
  taxCodes: QBOTaxCode[],
}): Settings => {
  return {
    stripeClearingAccountId:
      accounts.find((act: QBOAccount) => act.Name === "Stripe")?.Id || "",
    stripePayoutAccountId:
      accounts.find((act: QBOAccount) => act.Name === "Checking")?.Id || "",
    stripeVendorId:
      vendors.find((vendor: QBOVendor) => vendor.DisplayName === "Stripe")
        ?.Id || "",
    stripeFeeAccountId:
      accounts.find((act: QBOAccount) => act.Name === "Stripe fees")?.Id || "",
    defaultIncomeAccountId:
      accounts.find((act: QBOAccount) => act.Name === "Stripe sales")?.Id ||
      null,
    defaultTaxCodeId:
      taxCodes.find((taxCode: QBOTaxCode) => taxCode.Name === "TAX")?.Id || "",
    exemptTaxCodeId:
      taxCodes.find((taxCode: QBOTaxCode) => taxCode.Name === "NON")?.Id || "",
  };
};

export default getDefaultSettings;
