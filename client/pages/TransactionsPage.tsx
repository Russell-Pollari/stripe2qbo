import * as React from 'react';

import ImportTransactions from '../components/ImportTransactions';
import SyncDetails from '../components/SyncDetails';
import TransactionTable from '../components/TransactionTable';

const TransactionsPage = () => {
    return (
        <div>
            <div className="mb-2 txt-left">
                <ImportTransactions />
            </div>
            <TransactionTable />
            <SyncDetails />
        </div>
    );
};

export default TransactionsPage;
