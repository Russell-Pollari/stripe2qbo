export type QBOCompanyInfo = {
    CompanyName: string;
    Country: string;
};

export type QBOAccount = {
    Id: string;
    Name: string;
    CurrencyRef: {
        value: string;
    };
    AccountType: string;
    CurrentBalance: string;
};

export type QBOVendor = {
    Id: string;
    DisplayName: string;
    CurrencyRef: {
        value: string;
    };
};

export type QBOTaxCode = {
    Id: string;
    Name: string;
    Description: string;
};

export type Settings = {
    stripeClearingAccountId: string;
    stripePayoutAccountId: string;
    stripeVendorId: string;
    stripeFeeAccountId: string;
    defaultIncomeAccountId: string;
    defaultTaxCodeId: string;
    exemptTaxCodeId: string;
    // productSettings: ProductSettings[];
    // taxSettings: TaxSettings[];
};

export type StripeInfo = {
    id: string;
    business_profile: {
        name: string;
    };
    country: string;
    default_currency: string;
};

export type SyncOptions = {
    from_date: string;
    to_date: string;
};

export type Transaction = {
    id: string;
    created: number;
    type: string;
    description: string;
    amount: number;
    status: string;
    failure_reason: string | null;
    fee: number;
    currency: string;
    invoice_id: string | null;
    expense_id: string | null;
    payment_id: string | null;
    transfer_id: string | null;
};
