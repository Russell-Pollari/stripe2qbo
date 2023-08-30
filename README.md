# Stripe to Quick Books Online

**Import your Stripe transactions into Quick Books Online.**

Connect your accounts, define your sync settings, and import your Stripe transactions into QBO with a single click.

![screenshot](screenshot.png)

I saved myself ~$100 USD/month by replacing some SaaS tools with this custom solution. Sharing it here in case it's useful to anyone else.

Working on generalizing/customizing this so that it is valuable beyond my use cases. Issues, feature requests, and PRs welcome!

## Installation

> Requires a QBO developer account and an QBO app with a client ID and secret. See [here](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)

> Requires a Stripe account with Connect enabled

### Server

`$ python3 -m venv venv`

`$ source venv/bin/activate`

`$ pip install -r requirements.txt`

`$ touch .env`

Add the following to `.env` with your own values:

```
SECRET_KEY=...

QBO_CLIENT_ID=...
QBO_CLIENT_SECRET=...
QBO_REDIRECT_URI=http://localhost:8000/qbo/oauth2/callback
QBO_BASE_URL=https://sandbox-quickbooks.api.intuit.com/v3/company

STRIPE_API_KEY=...
STRIPE_CLIENT_ID=...
STRIPE_REDIRECT_URL=http://localhost:8000/stripe/oauth2/callback
```

Make sure to update your QBO and Stripe settings with the correct redirect URLs.

### Client

`$ npm install`

## Running locally

Build client

`$ npm run build`

Run server

`$ python -m uvicorn stripe2qbo.api.app:app`

## Sync Settings

`Stripe Clearing Account` (**Required**)

The bank account in QBO that you want Stripe transactions to be synced to. This should track your Stripe Balance. (e.g. 'Stripe Balance')

`Stripe Payout Account` (**Required**)

The name of the bank account in QBO that you want Stripe Payouts to be transferred to. Probably your main bank account. (e.g. 'Chequing')

`Stripe Vendor` (**Required**)

The name of the vendor in QBO that you want Stripe fees to be sent to. (e.g. 'Stripe\)

`Stripe Expense Account` (**Required**)

The name of the expense account in QBO that you want Stripe fees to be categorized under. (e.g. 'Stripe Fees')

`Default Income Account ` (**Required**)

The name of the income account in QBO that you want Stripe sales to be categorized under. (e.g. 'Sales')

> Products on QBO will be automatically created for you, using the product name from Stripe. If this product exists on QBO already, it may already be linked to an income account. If you want to change this, you'll need to do it manually.

### Tax settings

For now, just two fields are required—a default tax code and an exempt tax code. The default tax code is used for all line items with non-zero tax. The exempt tax code is used for all line items with zero tax.

> When syncing invoices, any automatic tax calculations done by QBO will be overwritten to ensure the total tax amount matches the Stripe invoice.

`Default Tax Code` **(required if sales tax is enabled)**

The default tax code to use for all invoice line items with non-zero tax. (e.g. TAX, or HST ON)

`Exempt Tax Code` **(required if sales tax is enabled)**

The default tax code to use for all invoice line items with zero tax. (e.g. TAX or Exempt)

> 'TAX' and 'NON' are psuedo tax codes specific to US QBO accounts. If you're using a different QBO region, you'll need to change these. See [here](https://developer.intuit.com/app/developer/qbo/docs/develop/tutorials/transaction-tax-detail-entity-fields) for more info on setting up sales tax.

## ROADMAP:

Here's a rough roadmap of what's on the way to make this generally useful:

-   [ ] Persistent SQL backend
-   [ ] Product settings to customize behaviour of individual products
-   [ ] Tax settings to customize behaviour of taxes
-   [ ] Support all transaction types (e.g. refunds, transfers, etc.)
-   [ ] Add test suite and CI/CD
-   [ ] Create new QBO accounts from Sync Settings
-   [ ] Prettify transaction table - pagination, sorting, filtering, etc. (MUI Data table)
-   [ ] Add more info to transaction table - e.g. fees, tax, customer, etc.
-   [ ] Show details of a synced transaction (e.g. Customer, Invoice, Products, Stripe fee)
-   [ ] Speed up backend with concurrent requests
-   [ ] JWT auth and user accounts
-   [ ] Deploy
-   [ ] Multiple connections per user
-   [ ] Find matches / sync status from historical data
-   [ ] Support all currencies
-   [ ] Sync payment methods (e.g. credit cards, ACH)
