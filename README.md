# Stripe to Quick Books Online

**Quickly sync your Stripe transactions with Quick Books Online.**

I saved myself ~$100 USD/month with this humble app.

Built with my specific use cases in mind. But it shoudn't be too hard to generalize/customize for others. Issues, feature requests, and PRs welcome!

If you want some help configuring this to your use case, get in touch!

## Installation

> Requires a QBO developer account and an QBO app with a client ID and secret. See [here](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)

### Server

`$ python3 -m venv venv`

`$ source venv/bin/activate`

`$ pip install -r requirements.txt`

`$ touch .env`

```
SECRET_KEY=...
QBO_CLIENT_ID=...
QBO_CLIENT_SECRET=...
QBO_REDIRECT_URI=...
QBO_BASE_URL=...
STRIPE_API_KEY=...
```

### Client

`$ npm install`

## Running locally

Build client

`$ npm run build`

Run server

`$ python -m uvicorn stripe2qbo.api.app:app`

## Settings

`STRIPE_PAYOUT_ACCOUNT` (**Required**)

The name of the bank account in QBO that you want stripe payouts to be synced to. Required. This should be the bank account that your payouts from Stripe get sent to.

Defaults to 'Checking'

`STRIPE_BANK_ACCOUNT` (**Required**)

The name of the bank account in QBO that you want stripe transactions to be synced to. This is sometimes refered to as a clearing account. If you don't have this accont on QBO already, one will be created for you.

Defaults to 'Stripe'

`STRIPE_FEE_EXPENSE_ACCOUNT` (**Required**)

The name of the expense account in QBO that you want Stripe fees to be synced to. If you don't have this accont on QBO already, one will be created for you.

Defaults to 'Stripe fees'

`STRIPE_VENDOR_NAME`(**Required**)

The name of the vendor in QBO that you want Stripe fees to be synced to. If you don't have this vendor on QBO already, one will be created for you.

Defaults to 'Stripe'

`DEFAULT_INCOME_ACCOUNT_NAME` (_Optional_)

The name of the income account in QBO that you want Stripe sales to be synced to. If you don't have this account on QBO already, one will be created for you.

Defaults to 'Stripe Income'.

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

Tax codes will not be created for you if they don't exist.
