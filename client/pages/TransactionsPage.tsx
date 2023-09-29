import * as React from 'react';

import ImportTransactions from '../components/ImportTransactions';
import SyncDetails from '../components/SyncDetails';
import TransactionTable from '../components/TransactionTable';
import SyncTransactions from '../components/SyncTransactions';

const TransactionsPage = () => {
    const drawerWidth = 320;

    return (
        <div>
            <div className="my-4 flex justify-between">
                <ImportTransactions />
                <SyncTransactions />
            </div>
            <div className="flex h-full">
                <TransactionTable />
                <SyncDetails drawerWidth={drawerWidth} />
            </div>
        </div>
    );
};

export default TransactionsPage;
