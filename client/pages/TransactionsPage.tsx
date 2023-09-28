import * as React from 'react';
import { useSelector } from 'react-redux';

import ImportTransactions from '../components/ImportTransactions';
import SyncDetails from '../components/SyncDetails';
import TransactionTable from '../components/TransactionTable';
import SyncTransactions from '../components/SyncTransactions';
import type { RootState } from '../store/store';

const TransactionsPage = () => {
    const expandedTransactionId = useSelector(
        (state: RootState) => state.transactions.expandedTransactionId
    );

    const drawerWidth = 320;

    return (
        <div>
            <div className="mb-2 flex">
                <ImportTransactions />
                <SyncTransactions />
            </div>
            <div
                style={{
                    width: `calc(100% - ${
                        expandedTransactionId ? `${drawerWidth}px)` : '0px'
                    }`,
                }}
            >
                <TransactionTable />
            </div>
            <SyncDetails drawerWidth={drawerWidth} />
        </div>
    );
};

export default TransactionsPage;
