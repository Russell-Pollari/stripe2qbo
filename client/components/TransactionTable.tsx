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
    const { data: transactions = [], isLoading } = useGetTransactionsQuery();
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
            width: 100,
            valueFormatter: (params) => {
                return numToAccountingFormat(params.value as number);
            },
        },
        { field: 'currency', headerName: '', width: 50 },
        { field: 'description', headerName: 'Description', width: 200 },
        { field: 'created', headerName: 'Created', type: 'date', width: 150 },
        {
            field: 'status',
            headerName: 'Status',
            width: 200,
            renderCell: (params) => (
                <SyncStatus status={params.value} id={params.row.id} />
            ),
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
        {
            field: 'actions',
            headerName: '',
            type: 'actions',
            width: 150,
            getActions: (params) => [
                <button
                    className="text-sm text-gray-500 hover:text-gray-700"
                    onClick={() => {
                        dispatch(selectTransaction(params.row.id));
                    }}
                >
                    Details
                </button>,
            ],
        },
    ];

    return (
        <div className="w-max h-3/4">
            <DataGrid
                sx={{
                    '& .MuiDataGrid-columnHeaderTitle': { fontWeight: '600' },
                }}
                onRowSelectionModelChange={(selection) => {
                    setSelectedTransactionIds(selection as string[]);
                }}
                rows={rows}
                loading={isLoading}
                columns={columns}
                checkboxSelection
                disableColumnSelector
                hideFooterSelectedRowCount
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
