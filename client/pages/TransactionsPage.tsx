import * as React from 'react';

import ImportTransactions from '../components/ImportTransactions';
import TransactionTable from '../components/TransactionTable';

const TransactionsPage = () => {
    return (
        <div>
            <ImportTransactions />
            <TransactionTable />
        </div>
    );
};

export default TransactionsPage;
