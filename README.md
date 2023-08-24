# Stripe to Quick Books Online

**Quickly sync your Stripe transactions with Quick Books Online.**

I run two companies for SharpestMinds (US co. and CAN co.). This, unfortunately, doubles much of our costs—particularly around payment processing and accounting.

Saved the company ~$200 CAD/month with this humble CLI.

Issues, feature requests, and PRs welcome!

If you want some help configuring this to your use case, or setting up, get in touch!

## Installation

> Requires a QBO developer account and an QBO app with a client ID and secret. See [here](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)

`$ python3 -m venv venv`

`$ source venv/bin/activate`

`$ pip install -r requirements.txt`

`$ touch .env`

```
QBO_CLIENT_ID=...
QBO_CLIENT_SECRET=...
QBO_REDIRECT_URI=...
STRIPE_API_KET=...
```

## Configuration

Use settings.py to configure the sync.

`STRIPE_PAYOUT_ACCOUNT` (**Required**)

The name of the bank account in QBO that you want stripe payouts to be synced to. Required. This should be the bank account that your payouts from Stripe get sent to.

`STRIPE_BANK_ACCOUNT` (_Optional_)

The name of the bank account in QBO that you want stripe transactions to be synced to. This is sometimes refered to as a clearing account. If you don't have this accont on QBO already, one will be created for you. Defaults to 'Stripe'

`STRIPE_FEE_EXPENSE_ACCOUNT` (_Optional_)

The name of the expense account in QBO that you want Stripe fees to be synced to. If you don't have this accont on QBO already, one will be created for you. Defaults to 'Stripe fees'

`STRIPE_VENDOR_NAME`(_Optional_)

The name of the vendor in QBO that you want Stripe fees to be synced to. If you don't have this vendor on QBO already, one will be created for you. Defaults to 'Stripe'

`DEFAULT_INCOME_ACCOUNT_NAME` (_Optional_)

The name of the income account in QBO that you want Stripe sales to be synced to. If you don't have this account on QBO already, one will be created for you. Defaults to 'Stripe Income'.

If not set, an income account for will be created with the same name as the Stripe product.

You can override this for individual products using `PRODUCTS` (see below).

`PRODUCTS` (_Optional_)

List of settings to customize syncing of Stripe products.

Each product should have a `stripe_name` and an `income_account` (the name of the income account in QBO that you want the product to be synced to). If you don't have this accont on QBO already, one will be created for you with type `Income`.

```json
    "PRODUCTS": [{
            "product_name": "stripe_product_name",
            "income_account_name": "account_name",
        },
```

> **Note**: if the product exists on QBO already, it may already be linked to an income account. If you want to change this, you'll need to do it manually.

### Tax settings

Support for multiple tax codes and more complex tax configuration is on the roadmap. For now just two fields are required, a default tax code and an exempt tax code. The default tax code is used for all line items with non-zero tax. The exempt tax code is used for all line items with zero tax.

When syncing invoices, any automatic tax calculations done by QBO will be overwritten to ensure the total tax amount matches the Stripe invoice.

`DEFAULT_TAX_CODE_ID` **(required if sales tax is enabled)**

The default tax code to use for all invoice line items with non-zero tax. Defaults to 'TAX'.

`EXEMPT_TAX_CODE_ID` **(required if sales tax is enabled)**

The default tax code to use for all invoice line items with zero tax. Defaults to 'NON'.

> **Note:** 'TAX' and 'NON' are psuedo tax codes specific to US QBO accounts. If you're using a different QBO region, you'll need to change these. See [here](https://developer.intuit.com/app/developer/qbo/docs/develop/tutorials/transaction-tax-detail-entity-fields) for more info on setting up sales tax.

Tax codes will not be created for you if they don't exist. To see a list of existing QBO tax codes with their ids:

`$ python list_tax_codes.py`

## Syncing

```bash
$ python cli.py [-h] [--from_date FROM_DATE] [--to_date TO_DATE] [--type TYPE] [--currency CURRENCY] {sync,logout}

positional arguments:
{sync,logout} Command to run ('sync', 'logout'))

options:
-h, --help show this help message and exit
--from_date FROM_DATE
From date (YYYY-MM-DD)
--to_date TO_DATE To date (YYYY-MM-DD)
--type TYPE Type of transaction
--currency CURRENCY Currency of transactions
```

You will be prompted to connect your QBO account. Follow the link and then copy the resulting URL into the CLI.

> **Note**: If no currency is set, all currencies will be synced. If your QBO does not have multi-currency enabled, you must set the currency to match the currency of your QBO account

## Logout

Disconnect your QBO account (e.g. to connect to a new one)  
`$ python cli.py logout`

## Balance check

Utility for sanity checks to see if your Stripe and QBO balances match.
`$ python balances.py`
