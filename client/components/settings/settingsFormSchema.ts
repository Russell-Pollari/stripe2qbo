import { object, string } from "yup";

const settingsFormSchema = object().shape({
  stripeClearingAccountId: string().required(
    "Stripe Clearing Account is required"
  ),
  stripePayoutAccountId: string().required("Stripe Payout Account is required"),
  stripeVendorId: string().required("Stripe Vendor is required"),
  stripeFeeAccountId: string().required("Stripe Fee Account is required"),
  defaultIncomeAccountId: string().required(
    "Default Income Account is required"
  ),
  defaultTaxCodeId: string().required("Default Tax Code is required"),
  exemptTaxCodeId: string().required("Exempt Tax Code is required"),
});

export default settingsFormSchema;