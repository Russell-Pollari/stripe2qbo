import * as React from 'react';
import { useSelector } from 'react-redux';

import ImportTransactions from '../components/ImportTransactions';
import SyncDetails from '../components/SyncDetails';
import TransactionTable from '../components/TransactionTable';
import { RootState } from '../store/store';

const TransactionsPage = () => {
    const selectedTransactionId = useSelector(
        (state: RootState) => state.transactions.selectedTransactionId
    );

    const drawerWidth = 320;

    return (
        <div>
            <div className="mb-2 txt-left">
                <ImportTransactions />
            </div>
            <div
                style={{
                    width: `calc(100% - ${
                        selectedTransactionId ? `${drawerWidth}px)` : '0px'
                    }`,
                }}
            >
                <TransactionTable />
            </div>
            {selectedTransactionId && <SyncDetails drawerWidth={drawerWidth} />}
        </div>
    );
};

export default TransactionsPage;
