import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { DataGrid, GridRowsProp, GridColDef } from '@mui/x-data-grid';
import { useMediaQuery } from 'react-responsive';

import type { RootState } from '../store/store';
import type { Transaction } from '../types';
import {
    setExpandedTransactionId,
    selectTransactionIds,
} from '../store/transactions';
import { useGetTransactionsQuery } from '../services/api';
import numToAccountingFormat from '../numToAccountingString';
import SyncStatus from './SyncStatus';

const TransactionTable = () => {
    const dispatch = useDispatch();
    const { data: transactions = [], isLoading } = useGetTransactionsQuery();
    const selectedTransactionIds = useSelector(
        (state: RootState) => state.transactions.selectedTransactionIds
    );

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
                        dispatch(setExpandedTransactionId(params.row.id));
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
                    dispatch(selectTransactionIds(selection as string[]));
                }}
                rowSelectionModel={selectedTransactionIds}
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
