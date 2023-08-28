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

Add the following to `.env` with your own values:

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

## Sync Settings

`Stripe Clearing Account` (**Required**)

The bank account in QBO that you want Stripe transactions to be synced to. This should track your Stripe Balance.

`Stripe Payout Account` (**Required**)

The name of the bank account in QBO that you want Stripe Payouts to be transferred to.

`Stripe Vendor`(**Required**)

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

## TODO:

Here's a rough roadmap to get this to a more usable state:

- [ ] Import transactions for review before syncing
- [ ] Create new QBO accounts from Sync Settings
- [ ] OAuth2 for Stripe
- [ ] Product settings to customize behaviour of individual products
- [ ] Tax settings to customize behaviour of taxes
- [ ] Support all transaction types (e.g. refunds, transfers, etc.)
- [ ] Charges without invoices
- [ ] Add test suite and CI/CD
- [ ] Speed up backend with concurrent requests
- [ ] State management for frontend; optimize data fetching
- [ ] Persistent SQL backend
- [ ] User accounts
- [ ] Deploy
