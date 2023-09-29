import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { DataGrid } from '@mui/x-data-grid';
import type {
    GridRowsProp,
    GridColDef,
    GridRenderCellParams,
    GridRowParams,
} from '@mui/x-data-grid';
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
            width: 150,
            renderCell: (
                params: GridRenderCellParams<{ id: string }, string>
            ) => <SyncStatus status={params.value} id={params.row.id} />,
        },
    ];

    return (
        <div className="w-max h-3/4">
            <DataGrid
                sx={{
                    '& .MuiDataGrid-columnHeader': {
                        backgroundColor: 'rgb(243 244 246)',
                    },
                    '& .MuiDataGrid-columnHeaderTitle': {
                        fontWeight: '600',
                    },
                }}
                onRowSelectionModelChange={(selection) => {
                    dispatch(selectTransactionIds(selection as string[]));
                }}
                rowSelectionModel={selectedTransactionIds}
                onRowClick={(params: GridRowParams<{ id: string }>, event) => {
                    event.defaultMuiPrevented = true;
                    dispatch(setExpandedTransactionId(params.row.id));
                }}
                rows={rows}
                loading={isLoading}
                columns={columns}
                checkboxSelection
                disableColumnSelector
                hideFooterSelectedRowCount
                autoPageSize
                columnVisibilityModel={{
                    description: isBigScreen,
                    fee: isMediumScreen,
                    created: isSmallScreen,
                    amount: isSmallScreen,
                }}
            />
        </div>
    );
};

export default TransactionTable;
