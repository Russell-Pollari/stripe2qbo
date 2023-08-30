import * as React from 'react';

import QBOConnection from './components/QBOConnection';
import StripeConnection from './components/StripeConnection';
import SyncSettings from './components/settings/SyncSettings';
import ImportTransactions from './components/ImportTransactions';
import TransactionTable from './components/TransactionTable';

const App = () => {
    return (
        <div>
            <div className="flex items-center justify-between bg-green-300 p-4">
                <h1 className="font-semibold text-xl">Stripe 2 QBO</h1>
            </div>
            <div className="p-6">
                <div className="flex justify-around">
                    <div className="basis-3/4">
                        <ImportTransactions />
                        <TransactionTable />
                    </div>
                    <div>
                        <StripeConnection />
                        <QBOConnection />
                        <SyncSettings />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default App;
