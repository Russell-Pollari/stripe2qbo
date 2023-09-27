import * as React from 'react';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { DataGrid, GridRowsProp, GridColDef } from '@mui/x-data-grid';
import { useMediaQuery } from 'react-responsive';

import { selectTransaction } from '../store/transactions';
import {
    useGetTransactionsQuery,
    useSyncTransactionsMutation,
} from '../services/api';
import type { Transaction } from '../types';
import numToAccountingFormat from '../numToAccountingString';
import SyncStatus from './SyncStatus';

const TransactionTable = () => {
    const dispatch = useDispatch();
    const { data: transactions = [] } = useGetTransactionsQuery();
    const [syncTransactions] = useSyncTransactionsMutation();
    const [selectedTransactionIds, setSelectedTransactionIds] = useState<
        string[]
    >([]);

    const isBigScreen = useMediaQuery({ query: '(min-width: 1280px)' });
    const isMediumScreen = useMediaQuery({ query: '(min-width: 900px)' });
    const isSmallScreen = useMediaQuery({ query: '(min-width: 700px)' });
    const isMobile = useMediaQuery({ query: '(min-width: 500px)' });

    const rows: GridRowsProp = transactions.map((transaction: Transaction) => {
        return {
            id: transaction.id,
            type: transaction.type,
            amount: transaction.amount,
            fee: -transaction.fee,
            currency: transaction.currency.toUpperCase(),
            description: transaction.description,
            created: new Date(transaction.created * 1000),
            status: transaction.status,
        };
    });

    const columns: GridColDef[] = [
        { field: 'type', headerName: 'Type', width: 100 },
        {
            field: 'amount',
            headerName: 'Amount',
            width: 150,
            valueFormatter: (params) => {
                return numToAccountingFormat(params.value as number);
            },
        },
        {
            field: 'fee',
            headerName: 'Fee',
            width: 150,
            valueFormatter: (params) => {
                return numToAccountingFormat(params.value as number);
            },
        },
        { field: 'currency', headerName: 'Currency', width: 100 },
        { field: 'description', headerName: 'Description', width: 300 },
        { field: 'created', headerName: 'Created', type: 'date', width: 150 },
        {
            field: 'status',
            headerName: 'Status',
            width: 150,
            renderCell: (params) => (
                <SyncStatus status={params.value} id={params.row.id} />
            ),
        },
        {
            field: 'actions',
            headerName: 'Actions',
            type: 'actions',
            width: 300,
            getActions: (params) => [
                <button
                    className="bg-white hover:bg-gray-100 text-gray-700 font-semibold py-2 px-4 border border-gray-400 rounded-full shadow"
                    onClick={() => {
                        dispatch(selectTransaction(params.row.id));
                    }}
                >
                    View details
                </button>,
            ],
            renderHeader: () => (
                <div className="text-right">
                    <button
                        className="inline-block bg-slate-300 hover:bg-slate-600 text-gray-500 font-bold py-2 px-4 rounded-full text-sm"
                        onClick={() => syncTransactions(selectedTransactionIds)}
                    >
                        {transactions.some((t) => t.status === 'syncing') ? (
                            <span>
                                Syncing{' '}
                                {
                                    transactions.filter(
                                        (t) => t.status === 'syncing'
                                    ).length
                                }{' '}
                                transactions..
                            </span>
                        ) : (
                            <span>
                                Sync {selectedTransactionIds.length}{' '}
                                transactions
                            </span>
                        )}
                    </button>
                </div>
            ),
        },
    ];

    return (
        <div className="w-full h-3/4">
            <DataGrid
                onRowSelectionModelChange={(selection) => {
                    setSelectedTransactionIds(selection as string[]);
                }}
                rows={rows}
                columns={columns}
                checkboxSelection
                pageSizeOptions={[10, 25]}
                autoPageSize
                columnVisibilityModel={{
                    fee: isBigScreen,
                    currency: isBigScreen,
                    type: isBigScreen,
                    description: isMediumScreen,
                    created: isSmallScreen,
                    status: isMobile,
                }}
            />
        </div>
    );
};

export default TransactionTable;
